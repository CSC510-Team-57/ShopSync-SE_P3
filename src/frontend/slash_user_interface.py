"""
Copyright (c) 2021 Anshul Patel
This code is licensed under MIT license (see LICENSE.MD for details)

@author: slash
"""
# Import Libraries
import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit.components.v1 as components
import re
import pandas as pd
import configs as conf
from url_shortener import shorten_url
from main_streamlit import search_items_API
import streamlit as st
from firebase_admin import firestore, auth
from bs4 import BeautifulSoup
import requests
# sys.path.append('../')
# st.set_page_config(layout= "wide")
# st.title("ShopSync")

def fetch_title():
    return "Home"

def get_firestore_client():
    from firebase_admin import firestore
    return firestore.client()

def create_app(db_client=None):
    if db_client is None:
        db_client = get_firestore_client()

def search_product(website, product_name):
    results = search_items_API(website, product_name)
    #print(results)
    return results

    

def search_walmart_product(query):
    api_key = "YOUR_WALMART_API_KEY"
    url = f"https://api.walmartlabs.com/v1/search"
    params = {
        "query": query,
        "format": "json",
        "apiKey": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [{
            "title": item.get("name"),
            "price": f"${item.get('salePrice', 'N/A')}",
            "link": item.get("productUrl"),
            "image_url": item.get("thumbnailImage", "https://via.placeholder.com/150")
        } for item in data.get("items", [])]
    return []

def search_amazon_product(query):
    url = "https://amazon24.p.rapidapi.com/api/product"
    headers = {
        "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",
        "X-RapidAPI-Host": "amazon24.p.rapidapi.com"
    }
    params = {"country": "US", "keyword": query}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return [{
            "title": product.get("title"),
            "price": product.get("price"),
            "link": product.get("link"),
            "image_url": product.get("thumbnail")
        } for product in data.get("docs", [])]
    return []

def search_ebay_product(query):
    app_id = "YOUR_EBAY_APP_ID"
    url = "https://svcs.ebay.com/services/search/FindingService/v1"
    params = {
        "OPERATION-NAME": "findItemsByKeywords",
        "SERVICE-VERSION": "1.0.0",
        "SECURITY-APPNAME": app_id,
        "RESPONSE-DATA-FORMAT": "JSON",
        "keywords": query
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [{
            "title": item.get("title")[0],
            "price": item.get("sellingStatus", [{}])[0].get("currentPrice", [{}])[0].get("__value__"),
            "link": item.get("viewItemURL", ["#"])[0],
            "image_url": item.get("galleryURL", ["https://via.placeholder.com/150"])[0]
        } for item in data.get("findItemsByKeywordsResponse", [{}])[0].get("searchResult", [{}])[0].get("item", [])]
    return []

def search_bestbuy_product(query):
    api_key = "YOUR_BESTBUY_API_KEY"
    url = f"https://api.bestbuy.com/v1/products((search={query}))"
    params = {
        "format": "json",
        "apiKey": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [{
            "title": product.get("name"),
            "price": product.get("salePrice"),
            "link": product.get("url"),
            "image_url": product.get("image")
        } for product in data.get("products", [])]
    return []

def search_target_product(query):
    url = "https://target1.p.rapidapi.com/products/v3/search"
    headers = {
        "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",
        "X-RapidAPI-Host": "target1.p.rapidapi.com"
    }
    params = {"keyword": query, "count": 10}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return [{
            "title": item.get("title"),
            "price": item.get("price", {}).get("formatted_current_price"),
            "link": item.get("url"),
            "image_url": item.get("images", [{}])[0].get("base_url") + item.get("images", [{}])[0].get("primary")
        } for item in data.get("data", {}).get("search", {}).get("products", [])]
    return []

def search_costco_product(query):
    url = "https://costco4.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",
        "X-RapidAPI-Host": "costco4.p.rapidapi.com"
    }
    params = {"q": query}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return [{
            "title": item.get("name"),
            "price": item.get("price"),
            "link": item.get("url"),
            "image_url": item.get("image")
        } for item in data.get("products", [])]
    return []


def fetch_image_from_bing(product_name):
    api_key = "YOUR_BING_API_KEY"
    search_url = "https://api.bing.microsoft.com/v7.0/images/search"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": product_name, "count": 1}  # Limit to 1 image for speed

    try:
        response = requests.get(search_url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if "value" in data and len(data["value"]) > 0:
                return data["value"][0]["contentUrl"]  # Return the first image URL
    except Exception as e:
        print(f"Error fetching image: {e}")
    
    return "https://via.placeholder.com/150"  # Default image if no result
     
def check_product_input(product):
    """Check if the product input is valid based on multiple criteria."""
    # Check for non-empty input
    if not product.strip():
        st.error("Please enter a valid product name.")
        return False
    
    # Check length
    if len(product) < 1 or len(product) > 100:
        st.error("Product name must be between 1 and 100 characters.")
        return False
    
    # Check for invalid characters (allowing letters, numbers, spaces, hyphens, and underscores)
    if not re.match(r'^[\w\s\-]+$', product):
        st.error("Product name can only contain letters, numbers, spaces, hyphens, and underscores.")
        return False

    # If all checks pass, return True
    return True


def app():
    db = firestore.client()
    page_bg = """
    <style>
        .appview-container {
            background-color: white !important;
        }
        .blur {
            filter: blur(5px);
            transition: filter 0.3s;
        }
        .loading {
            display: flex;
            justify-content: center;
            align-items: flex-start; /* Align to the top */
            height: 100vh; /* Full height of the viewport */
            position: absolute;
            top: 0; /* Position at the top */
            left: 0;
            right: 0;
            background-color: rgba(255, 255, 255, 0.8);
            z-index: 9999;
        }
        .spinner {
            border: 8px solid #f3f3f3; /* Light grey */
            border-top: 8px solid #3498db; /* Blue */
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: left; margin-bottom: -65px; color: #343434;'>Search For the Product to compare</h1>",
                    unsafe_allow_html=True)
    # st.markdown('<span class="my-label">Search For the Product to compare</span>', unsafe_allow_html=True)
    def split_description(description):
        words = description.split()
        lines = []
        line = ""
        for word in words:
            if len(line) + len(word) + 1 <= 6:
                if line:
                    line += " "
                line += word
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return '\n'.join(lines)
        '''words = description.split()
        lines = [' '.join(words[i:i+6]) for i in range(0, len(words), 6)]
        return '\n'.join(lines)'''
    st.markdown(page_bg, unsafe_allow_html=True)
    # Hide Footer in Streamlit
    hide_menu_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

    if 'dataframe' not in st.session_state:
        st.session_state.dataframe = None

    st.markdown(
        """
        <style>
        /* Adjust the text input width */
        .stTextInput {
            font-size: 400px !important;
            width: 100% !important;
            max-width: 500px;
            margin-top: -40px;
        }
        /* Adjust the select box width */
        # .stSelectbox {
        #     font-size: 400px !important;
        #     width: 100% !important;
        #     max-width: 500px;
        #     margin-top: -40px;
        # }
        .stSelectbox {
            font-size: 400px !important;
            width: 100% !important;
            max-width: 500px;
            margin-top: -40px;
        }

        /* Align checkboxes to the right */
        div[data-testid="stHorizontalBlock"] {
            display: flex;
            justify-content: right; /* Align checkboxes to the right */
        }

        label {
            margin-left: auto; /* Push label text to the left */
            text-align: right; /* Align text to the right */
        }
        .stSlider{
        margin-top: -30px;
        margin-left: -65px;
        width: 400px !important;}
        </style>
        """,
        unsafe_allow_html=True
    )

    custom_css = """
    <style>
        .my-label {
            font-size: 20px;
            color: #5F5E5F;  /* Change this value to your desired font size */
            font-weight: bold; /* Optional: make the label bold */
        }
    </style>
    """
    price_custom_css = """
    <style>
        .my-label {
            font-size: 20px;
            color: #5F5E5F;  /* Change this value to your desired font size */
            font-weight: bold;
            margin-top: -60px;
            margin-bottom: -100px; /* Optional: make the label bold */
        }
    </style>
    """
    # Add the custom CSS to the app
    st.markdown(custom_css, unsafe_allow_html=True)
    prod, web = st.columns(2)
    with prod:
        # Create a text input with a custom label
        st.markdown('<span class="my-label">Enter the product item name</span>', unsafe_allow_html=True)
        product = st.text_input('', key='product',
                                placeholder='Type product name...', 
                                label_visibility="visible",
                                on_change=None, 
                                type='default', 
                                value='')  # Use the custom class
        # product = st.text_input('Enter the product item name', key='product', help="Enter the name of the product you are searching for")
        st.markdown(custom_css, unsafe_allow_html=True)
    with web:

        # Create a text input with a custom label
        st.markdown('<span class="my-label">Select Website</span>', unsafe_allow_html=True)
        website = st.selectbox('', ('All', 'Walmart',
                        'Amazon', 'Ebay', 'BestBuy', 'Target', 'Costco', 'All'), key = "website_select")

    website_dict = {
        'Walmart': 'wm',
        'Amazon': 'az',
        'Ebay': 'eb',
        'BestBuy': 'bb',
        'Target': 'tg',
        'Costco': 'cc',
        'All': 'all'
    }


    # Initialize a variable to control loading state
    if 'loading' not in st.session_state:
        st.session_state.loading = False

    # Add a placeholder for loading spinner
    loading_placeholder = st.empty()

    # Add blur class if loading
    if st.session_state.loading:
        st.markdown('<div class="blur"></div>', unsafe_allow_html=True)

    # if 'selected_websites' not in st.session_state:
    #     st.session_state.selected_websites = []
    def reset_button():
        for website_name in website_dict.keys():
            if website_name.lower() != "all":  # Skip the 'all' entry
                # continue
                st.session_state[website_name] = False  # Set checkbox state to False
        # st.session_state['selected_websites'] = []  # Clear selected websites list

        # st.session_state["p"] = False  # Reset the checkbox value


    # Pass product and website to method
    if st.button('Search', key = "search_but") and product and website:
        if not check_product_input(product):
            return  # Exit the function early if the input is invalid

        # Reset selected websites and price range before new search
        selected_websites = []
        selected_websites.clear()  # Reset selected websites
        reset_button()

        # Start loading
        st.session_state.loading = True
        loading_placeholder.markdown('<div class="loading"><div class="spinner"></div></div>', unsafe_allow_html=True)

        # rakuten_discount = rakuten()
        company_list = conf.getCompanies()
        # results = search_product(website, product)        
        results = search_product(website_dict[website], product)

        user = auth.get_user_by_email(st.session_state.user_email)  # Replace with actual user email
        uid = user.uid

        # Reference to the user's document in "hisourites" collection
        user_his_ref = db.collection("history").document(uid)

        # Get the user's current hisorites data, or create a new structure if it doesn't exist
        user_his_doc = user_his_ref.get()
        
        if user_his_doc.exists:
            # If the document exists, retrieve the current data
            user_his_data = user_his_doc.to_dict()
        else:
            # Initialize empty arrays if document doesn't exist
            user_his_data = {
                "Search": [],
                "Timestamp": []
            }

        user_his_data["Search"].append(product)  # Access the actual value
        user_his_data["Timestamp"].append(time.time())  # Access the actual value

        # Update the user's document in Firestore with the new data
        user_his_ref.set(user_his_data)

        # Use st.columns based on return values
        description = []
        url = []
        price = []
        site = []
        rating = []
        image = []

        import random

        def get_random_value_from_list(lst):
            if not lst:
                return None  # Return None if the list is empty
            return random.choice(lst)

        my_list = [4.3, 4.0, 3.9, 4.8, 4.6, 4.4, 3.7, 3.5]

    # After the for loop populating the lists
        print("Lengths of lists:")
        print("Description length:", len(description))
        print("URL length:", len(url))
        print("Price length:", len(price))
        print("Site length:", len(site))
        # print("Rakuten length:", len(rakuten))
        print("Rating length:", len(rating))


        if results is not None and isinstance(results, list):
            for result in results:
                if result != {} and result['price'] != '':
                    description.append(result['title'])
                    url.append(result['link'])
                    price_str = result['price']
                    rating_value = result.get('review', '0')  # Safely access 'review'
                    print(rating_value)
                    image.append(result['image_url'])
                    # Clean and extract price
                    clean_price_str = re.sub(r'[^\d\.\,]', '', price_str)  # Remove unwanted characters
                    match = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)', clean_price_str)
                    rating_matches = re.findall(r"\d+(?:\.\d+)?", rating_value)
                    print(rating_matches)
                    rating_float = [float(match) for match in rating_matches[:1]]
                    if match:
                        price_str = match.group(0).replace(',', '')  # Remove commas for conversion
                        price_f = float(price_str)
                        price.append(price_f)
                        rating.append(rating_float)  # Append rating only if price is valid
                    else:
                        print("Unable to extract a valid price from the string:", price_str)
                        price.append(None)  # Append None if price extraction fails
                        rating.append(None)  # Append None for rating if price fails

                    site.append(result['website'])


        if len(price):

            dataframe = pd.DataFrame(
                {'Image_URL': image, 'Description': description, 'Price': price, 'Link': url, 'Website': site,'Ratings': rating})
            
            def add_http_if_not_present(url):
                if url.startswith('http://') or url.startswith('https://'):
                    return url
                else:
                    return 'https://' + url
            dataframe['Link'] = dataframe['Link'].apply(add_http_if_not_present)

            dataframe['Image'] = dataframe.apply(
                lambda row: f'<a href="{row["Link"]}" target="_blank"><img src="{row["Image_URL"]}" style="width:50px;height:50px;"></a>',
                axis=1
            )
            
            dataframe = dataframe.drop(["Image_URL", "Link"], axis=1)

            dataframe['Description'] = dataframe['Description'].apply(
                split_description)
            dataframe['Product'] = dataframe['Description'].str.split(
            ).str[:3].str.join(' ')
            dataframe['Product'] = dataframe['Product'].str.replace(
                '[,"]', '', regex=True)
            product_column = dataframe.pop('Product')
            dataframe.insert(0, 'Product', product_column)

            dataframe['Price'] = dataframe['Price'].apply(
                lambda x: float(f'{float(x):.2f}') if pd.notnull(x) and str(x).replace('.', '', 1).isdigit() else None
            )
            # dataframe = dataframe.sort_values(by='Price', ascending=True)
            dataframe = dataframe.reset_index(drop=True)
            dataframe['Price'] = dataframe['Price'].apply(lambda x: f'{x:.2f}' if x is not None else 'N/A')


            st.session_state['dataframe'] = dataframe

            styled_table = (
                dataframe.style
                .set_properties(**{'text-align': 'center'})
                .set_table_styles([
                    {"selector": "th", "props": [("text-align", "center")]},
                    {"selector": "td", "props": [("text-align", "center")]}
                ])
            )
            
            # st.markdown(
            #     styled_table.to_html(escape=False),  # Allow HTML content
            #     unsafe_allow_html=True
            # )

            st.success("Data successfully scraped and cached.")
            st.session_state.dataframe = dataframe

        else:
            st.error('Sorry!, there is no other website with same product')
        st.session_state.loading = False
        loading_placeholder.empty()  # Remove loading spinner

    def style_button_row(clicked_button_ix, n_buttons):
        def get_button_indices(button_ix):
            return {
                'nth_child': button_ix,
                'nth_last_child': n_buttons - button_ix + 1
            }

        clicked_style = """
        div[data-testid*="stHorizontalBlock"] > div:nth-child(%(nth_child)s):nth-last-child(%(nth_last_child)s) button {
            border-color: rgb(255, 75, 75);
            color: rgb(255, 75, 75);
            box-shadow: rgba(255, 75, 75, 0.5) 0px 0px 0px 0.2rem;
            outline: currentcolor none medium;
        }
        """
        unclicked_style = """
        div[data-testid*="stHorizontalBlock"] > div:nth-child(%(nth_child)s):nth-last-child(%(nth_last_child)s) button {
            pointer-events: none;
            cursor: not-allowed;
            opacity: 0.65;
            filter: alpha(opacity=65);
            -webkit-box-shadow: none;
            box-shadow: none;
        }
        """
        style = ""
        for ix in range(n_buttons):
            ix += 1
            if ix == clicked_button_ix:
                style += clicked_style % get_button_indices(ix)
            else:
                style += unclicked_style % get_button_indices(ix)
        st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)

    if 'dataframe' in st.session_state and isinstance(st.session_state.dataframe, pd.DataFrame):

        st.markdown("<h1 style='text-align: left; margin-bottom: -65px; color: #343434; margin-bottom: -20px;'>Result</h1>",
                    unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])# adjust the columns for price range and filters
        with col1:

            st.session_state.dataframe['Price'] = pd.to_numeric(
                st.session_state.dataframe['Price'], errors='coerce')
            
            st.markdown(price_custom_css, unsafe_allow_html=True)
            st.markdown('<span class="my-label">Price Range</span>', unsafe_allow_html=True)
            price_range = st.slider("",key = "slider", min_value=st.session_state.dataframe['Price'].min(), max_value=st.session_state.dataframe['Price'].max(
            ), value=(st.session_state.dataframe['Price'].min(), st.session_state.dataframe['Price'].max()))

            # Create two columns for sorting buttons
            button_col1, button_col2 = st.columns(2)

            # Add sorting buttons in separate columns
            with button_col1:
                sort_asc = st.button("Sort Asc", key = "sort_asc", on_click=style_button_row, kwargs={
                    'clicked_button_ix': 1, 'n_buttons': 3
                })
                # sort_asc = st.button("Sort Ascending")
            with button_col2:
                sort_desc = st.button("Sort Desc", key = "sort_desc", on_click=style_button_row, kwargs={
                    'clicked_button_ix': 2, 'n_buttons': 3
                })

            # Sort the DataFrame based on button clicks
            if sort_asc:
                st.session_state.dataframe = st.session_state.dataframe.sort_values(by='Price', ascending=True)
            elif sort_desc:
                st.session_state.dataframe = st.session_state.dataframe.sort_values(by='Price', ascending=False)

        with col2:
            st.markdown('<span class="my-label">Filter by Website</span>', unsafe_allow_html=True)

            # Define the number of checkboxes per row
            num_columns = 3  
            columns = st.columns(num_columns)

            # Iterate over the website dictionary and place each checkbox in a column
            selected_websites = []
            # selected_websites.clear()
            for idx, (website_name, website_code) in enumerate(website_dict.items()):
                if website_name.lower() == "all":
                    continue
                # Check if the website is in the selected_websites list
                col = columns[idx % num_columns]  # Place checkbox in the next column
                is_checked = col.checkbox(website_name, key=website_name)
                # Check if the checkbox is checked
                if is_checked:
                    selected_websites.append(website_name.lower())

            reset = st.button('Reset', on_click=reset_button)


        # Filter the dataframe by price range and selected websites
        filtered_df = st.session_state.dataframe[
            (st.session_state.dataframe["Price"] >= price_range[0]) &
            (st.session_state.dataframe["Price"] <= price_range[1])
        ]
        if selected_websites:
            filtered_df = filtered_df[filtered_df["Website"].isin(selected_websites)]
        # filtered_df = st.session_state.dataframe[(st.session_state.dataframe["Price"] >= price_range[0]) & (
        #     st.session_state.dataframe["Price"] <= price_range[1])]
        
        # Display the filtered dataframe at maximum width
        # st.markdown("<h2 style='text-align: left; color: #343434;'>Filtered Results</h2>", unsafe_allow_html=True)
        styled_df = (
            filtered_df.style
            # .apply(highlight_row, axis=None)
            .set_table_attributes('style="width: 100%; border-collapse: collapse;"')
            .set_properties(**{
                'text-align': 'center',
                'font-size': '20px',
                'border': '1px solid #ddd',
                'padding': '8px',
            })
            .set_table_styles([
                {'selector': 'thead th', 'props': [('background-color', '#4a4e69'), ('color', 'white'), ('font-weight', 'bold')]},
                {'selector': 'tbody tr:hover', 'props': [('background-color', '#e8e8e8')]},  # Row hover effect
                {'selector': 'tbody td', 'props': [('border', '1px solid #ddd')]},  # Border for cells
            ])
        )

        # Display styled DataFrame
        # st.dataframe(
        #     styled_df,
        #     column_config={"Link": st.column_config.LinkColumn("URL to website")},
        #     use_container_width=True  # Ensure the DataFrame uses the maximum width
        # )
        styled_table = (
                filtered_df.style
                .set_properties(**{'text-align': 'center'})
                .set_table_styles([
                    {"selector": "th", "props": [("text-align", "center")]},
                    {"selector": "td", "props": [("text-align", "center")]}
                ])
            )
            
        st.markdown(
            styled_table.to_html(escape=False),  # Allow HTML content
            unsafe_allow_html=True
        )
        # st.markdown("<h1 style='text-align: left; margin-bottom: -65px; color: #343434; margin-bottom: -20px;'>Add for favourites</h1>",
        #             unsafe_allow_html=True)
        # st.write('<span style="font-size: 24px;">Add for favorites</span>', unsafe_allow_html=True)
        # //////////////////////////////////////////////////////////////////////////////////////////////
        # Prints the websites names from filter and dataframe to check
        # st.write("Unique Website values in the dataframe:")
        # st.write(st.session_state.dataframe["Website"].unique())

        # # Print the selected websites list
        # st.write("Selected websites for filtering:")
        # st.write(selected_websites)
       
        #///////////////////////////////////////////////////////////////////////////////////////////////

    if st.session_state.dataframe is not None:
        # Add a label for the selectbox
        st.markdown('<span class="my-label">Select index to add to favourites</span>', unsafe_allow_html=True)

        # Create a selectbox to choose an index from the dataframe
        selected_index = st.selectbox(
            "", 
            [None] + list(range(len(st.session_state.dataframe))),  # Include 'None' for no selection
            format_func=lambda x: f"Row {x}" if x is not None else "Select a row"
        )

        # Close the container div
        st.markdown("</div></div>", unsafe_allow_html=True)

        # Check if a valid row is selected
        if selected_index is not None:
            # Extract the selected row with required columns
            fav_row = st.session_state.dataframe.loc[
                [selected_index], 
                ['Product', 'Description', 'Price', 'Website', 'Ratings', 'Image']
            ]

            fav_row['Ratings'] = fav_row['Ratings'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)

            # Append the row to the favorites table in session state
            if 'fav' in st.session_state:
                st.session_state.fav = pd.concat(
                    [st.session_state.fav, fav_row], axis=0
                ).drop_duplicates()
            else:
                st.session_state.fav = fav_row

            styled_table = (
                st.session_state.fav.style
                .set_properties(**{'text-align': 'center'})
                .set_table_styles([
                    {"selector": "th", "props": [("text-align", "center")]},
                    {"selector": "td", "props": [("text-align", "center")]}
                ])
            )
            
            st.markdown(
                styled_table.to_html(escape=False),  # Allow HTML content
                unsafe_allow_html=True
            )
            #st.dataframe(st.session_state.fav[['Product', 'Description', 'Price', 'Website', 'Ratings', 'Image']], use_container_width=True)

            # Save the favorites table to Firestore
            user = auth.get_user_by_email(st.session_state.user_email) 
            uid = user.uid

            

            # Reference to the user's document in "favourites" collection
            user_fav_ref = db.collection("favourites").document(uid)

            user_fav_doc = user_fav_ref.get()
            if user_fav_doc.exists:
                existing_favorites = pd.DataFrame(user_fav_doc.to_dict())
            else:
                existing_favorites = pd.DataFrame(columns=['Product', 'Description', 'Price', 'Website', 'Ratings', 'Image'])

            updated_favorites = pd.concat([existing_favorites, fav_row], axis=0).drop_duplicates().reset_index(drop=True)
            # Convert favorites table to a dictionary format compatible with Firestore
            user_fav_data = updated_favorites.to_dict(orient='list')

            # Save to Firestore
            user_fav_ref.set(user_fav_data)

#            st.session_state = updated_favorites

            st.success(f"{st.session_state.dataframe.loc[selected_index, 'Product']} has been added to your favorites!")
        
       
    # Add footer to UI
    footer = """
    <style>
        a:link , a:visited{
        color: blue;
        background-color: transparent;
        text-decoration: underline;
    }

    a:hover,  a:active {
        color: red;
        background-color: transparent;
        text-decoration: underline;
    }

    .footer {
        position: fixed;
        left: 0;
        bottom: 0%;
        width: 100%;
        background-color: #DFFFFA;
        color: black;
        text-align: center;
    }

    a, a:link, a:visited {
        text-decoration: none;
        color: #6c63ff;
        font-weight: bold;
        }
    </style>
    <div class="footer">
        <p style='margin-bottom: 4px; display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
        gap: 6px;'>Developed with ❤ by <a style='display: block; text-align: center;' href="https://github.com/devyash2930/ShopSync-SE" target="_blank">ShopSync</a></p>
        <p style='margin-bottom: 4px;'><a style='display: block; text-align: center;' href="https://github.com/Kashika08/CSC510_ShopSync_Group40/blob/main/LICENSE" target="_blank">MIT License Copyright (c) 2023</a></p>
        <p style='margin-bottom: 8px;'>Contributors: Devyash, Vatsal, Smit</p>
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)