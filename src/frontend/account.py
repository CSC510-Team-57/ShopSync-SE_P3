# account.py
# account.py
import streamlit as st
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
import requests
import base64
import os
import re
from PIL import Image
from PIL import Image
from dotenv import load_dotenv
import json
import slash_user_interface as slash_user_interface
from streamlit_cookies_controller import CookieController
import time

# Load environment variables from .env file
load_dotenv()

# Load Firebase Web API Key from environment variable
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")  # Set your key here if not in environment

# Set the theme (optional, replace with your preferred theme)
st.set_page_config(page_title="ShopSync", layout="wide", initial_sidebar_state="expanded")

def initialize_firebase(mock=False):
    if mock:
        # Mock initialization for testing purposes
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        return True

    json_path = os.path.join(os.path.dirname(__file__), 'shopsync-9ecdc-firebase-adminsdk-60nyc-ec3901d5d7.json')
    try:
        # Path to Firebase service account key
        cred = credentials.Certificate(json_path)
        firebase_admin.initialize_app(cred)
        return True
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        raise e

# Call the function to initialize Firebase
# if not firebase_admin._apps:
#     initialize_firebase()

# Rest of your code remains the same...

def fetch_title():
    return "Account"

def is_valid_email(email):
    # Basic regex for validating an email format
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def verify_password(email, password):
    """Verify email and password using Firebase REST API."""
    # Check for missing fields
    if not email and not password:
        raise ValueError("Both email and password must be provided.")
    elif not email:
        raise ValueError("Email must be provided.")
    elif not password:
        raise ValueError("Password must be provided.")

    # Check for missing fields
    if not email and not password:
        raise ValueError("Both email and password must be provided.")
    elif not email:
        raise ValueError("Email must be provided.")
    elif not password:
        raise ValueError("Password must be provided.")

    try:
        response = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}",
            json={"email": email, "password": password, "returnSecureToken": True}
        )
        response_data = response.json()

        if "idToken" in response_data:
            return True  # Successful login
        elif "error" in response_data:
            error_message = response_data["error"]["message"]
            if error_message == "EMAIL_NOT_FOUND":
                st.warning("No account found with this email address.")
            elif error_message == "INVALID_PASSWORD":
                st.warning("Incorrect password. Please try again.")
            else:
                st.warning(f"Login failed: {error_message}")
        return False
    except Exception as e:
        st.warning(f"Login failed: {str(e)}")
        return False


def app():
    if not firebase_admin._apps:
        initialize_firebase(mock=False)
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    # apply_theme()  # Apply the theme
    
    

# Define the absolute path to the image
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    image_path = os.path.join(root_dir, 'assets', 'shopsync-logos.jpeg')

    # image_path = os.path.join('assets', 'shopsync-logos.jpeg')

    # image_path = "ShopSync-SE\assets\shopsync-logos.jpeg"
    

# Define the absolute path to the image
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    image_path = os.path.join(root_dir, 'assets', 'shopsync-logos.jpeg')

    # image_path = os.path.join('assets', 'shopsync-logos.jpeg')

    # image_path = "ShopSync-SE\assets\shopsync-logos.jpeg"
    with open(image_path, "rb") as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode()
        st.markdown(
            """
            <style>
            /* Adjust the text input width */
            .stTextInput {
                font-size: 400px !important;
                width: 100% !important;
                max-width: 500px;
                margin: auto;
            }
            /* Adjust the select box width */
            .stSelectbox {
                font-size: 400px !important;
                width: 100% !important;
                padding-top: 80px;
                max-width: 500px;
                margin: auto;
            }
            .stButton{
            margin: auto;
            margin-left: 670px !important;
            width: 200px !important;}
            </style>
            """,
            unsafe_allow_html=True
        )
    # Main application logic
    
    if st.session_state.logged_in:
        user = auth.get_user_by_email(st.session_state.user_email)
        # print('User UID:', user.uid)
        st.title('Welcome to :violet[ShopSync]')
        st.write('You are logged in as:', st.session_state.user_email)
        st.write("Username:",user.uid)
        st.button("Logout", on_click=logout)  # Add logout button
    else:
        st.markdown(
        f"""
        <style>
        /* Flex container to align image and text */
        .welcome-container {{
            display: flex;
            align-items: center; /* Vertically center-aligns text and image */
            justify-content: center; /* Center aligns the entire container */
            gap: 10px; /* Space between the image and text */
        }}
        
        .welcome-text {{
            font-size: 35px;
            font-weight: bold;
            color: #4a4e69; /* Text color */
        }}

        .welcome-image {{
            width: 100px;
            height: 100px;
        }}
        </style>

        <div class="welcome-container">
            <img src="data:image/jpeg;base64,{encoded_image}" class="welcome-image">
            <div class="welcome-text">Welcome to ShopSync</div>
        </div>
        """,
        unsafe_allow_html=True
    )
        # Handle login and signup
        choice = st.selectbox('Login/Signup', ['Login', 'Sign up'])

        if choice == 'Login':
            email = st.text_input('Email Address', key='email')
            password = st.text_input('Password', type='password', key='password')

            if st.button('Login'):
                if not email and not password:
                    st.warning('Please enter the credentials.')
                elif not email:
                    st.warning('Please enter the email.')
                elif not is_valid_email(email):
                    st.warning('Invalid email format. Please enter a valid email address.')
                elif not password:
                    st.warning('Please enter the password.')
                else:
                    if verify_password(email, password):
                        # If login successful, update session state
                        st.session_state.logged_in = True
                        st.session_state.user_email = email

                        with open('tokens.json') as openfile:
                            json_object = json.load(openfile)

                        controller = CookieController()
                        token = controller.get("csrftoken")

                        tokenData = {
                            "email": email,
                            "expiration": time.time() + 70000
                        }
                        
                        json_object["tokens"][token] = tokenData

                        json_output = json.dumps(json_object, indent=4)

                        with open('tokens.json', 'w') as openfile:
                            openfile.write(json_output)

                        st.success('Logged in successfully!')
                        st.rerun()  # Rerun the app to reflect login state

        else:
            email = st.text_input('Email Address', key='email_signup')
            password = st.text_input('Password', type='password', key='password_signup')
            username = st.text_input('Enter your unique username')

            if st.button('Create account'):
                missing_fields = []

                if not email:
                    missing_fields.append('Email Address')
                elif not is_valid_email(email):
                    st.warning('Invalid email format. Please enter a valid email address.')
                
                if not password:
                    missing_fields.append('Password')
                if not username:
                    missing_fields.append('Unique Username')

                if len(missing_fields) == 3:
                    st.warning('Please enter the credentials.')
                elif missing_fields:
                    st.warning(f'Please fill the following field(s): {", ".join(missing_fields)}')
                else:
                    try:
                        user = auth.create_user(email=email, password=password, uid=username)
                        st.success('Account created successfully')
                        st.markdown('Please log in using this email and password')
                    except auth.EmailAlreadyExistsError:
                        st.warning('The email is already registered. Please use another email or log in.')
                    except Exception as e:
                        st.warning(f'Account creation failed: {str(e)}')

def is_valid_email(email):
    # Simple regex for validating email format
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def signup(username, email, password):
    if not username and not email and not password:
        raise ValueError("Please enter the credentials.")
    if not username:
        raise ValueError("Username is required.")
    if not email:
        raise ValueError("Email Address is required.")
    if not password:
        raise ValueError("Password is required.")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")
    if not is_valid_email(email):
        raise ValueError("Invalid email format. Please enter a valid email address.")

    try:
        user = auth.create_user(display_name=username, email=email, password=password)
        return "Account created successfully."
    except Exception as e:
        if "EMAIL_EXISTS" in str(e):
            raise ValueError("The email is already registered.")
        elif "USERNAME_EXISTS" in str(e):
            raise ValueError("The username is already taken.")
        else:
            raise ValueError("An unexpected error occurred.")

def signup(username, email, password):
    if not username and not email and not password:
        raise ValueError("Please enter the credentials.")
    if not username:
        raise ValueError("Username is required.")
    if not email:
        raise ValueError("Email Address is required.")
    if not password:
        raise ValueError("Password is required.")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")
    if not is_valid_email(email):
        raise ValueError("Invalid email format. Please enter a valid email address.")

    try:
        user = auth.create_user(display_name=username, email=email, password=password)
        return "Account created successfully."
    except Exception as e:
        if "EMAIL_EXISTS" in str(e):
            raise ValueError("The email is already registered.")
        elif "USERNAME_EXISTS" in str(e):
            raise ValueError("The username is already taken.")
        else:
            raise ValueError("An unexpected error occurred.")

def logout():
    # Delete token on logout
    with open('tokens.json', 'r') as openfile:
        json_object = json.load(openfile)
    controller = CookieController()
    token = controller.get("csrftoken")

    del json_object["tokens"][token]

    json_output = json.dumps(json_object, indent=4)

    with open('tokens.json', 'w') as openfile:
        openfile.write(json_output)

    # Clear session state on logout
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.success("You have been logged out.")
    st.rerun()  # Rerun the app to reflect logout state

# Call the app function
if __name__ == '__main__':
    app()