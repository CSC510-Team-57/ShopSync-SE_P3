import streamlit as st
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pandas as pd
import os

def fetch_title():
    return "Favourites"

def initialize_firebase(mock=False):
    if mock:
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        return True

    json_path = os.path.join(os.path.dirname(__file__), 'shopsync-9ecdc-firebase-adminsdk-60nyc-ec3901d5d7.json')
    try:
        cred = credentials.Certificate(json_path)
        firebase_admin.initialize_app(cred)
        return True
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        raise e

# Found this workaround here: https://github.com/streamlit/streamlit/issues/688#issuecomment-1575704898
# This is a known issue and something they're trying to implement properly into streamlit
def dataframe_with_selections(df):
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", False)
    df_with_selections = df_with_selections.drop(["Image"], axis=1)
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True), "Image": st.column_config.ImageColumn()},
        disabled=df.columns,
    )
    # edited_df = st.write(df_with_selections.to_html(escape=False), unsafe_allow_html=True, hide_index=True)
    selected_indices = list(np.where(edited_df.Select)[0])
    selected_rows = df[edited_df.Select]
    return selected_indices

def app(firestore_client=None):
    if not firebase_admin._apps:
        initialize_firebase(mock=False)

    if firestore_client is None:
        firestore_client = firestore.client()

    st.title("Favorites")

    user_email = st.session_state.user_email  # Ensure this is set
    user = auth.get_user_by_email(user_email)  # Get the user by email
    uid = user.uid

    # Reference to the user's document in the "favourites" collection
    user_fav_ref = firestore_client.collection("favourites").document(uid)
    user_fav_doc = user_fav_ref.get()

    if user_fav_doc.exists:
        user_fav_data = user_fav_doc.to_dict()

        # Convert user's favorites into a DataFrame
        favorites_df = pd.DataFrame({
            "Product": user_fav_data["Product"],
            "Description": user_fav_data["Description"],
            "Price": user_fav_data["Price"],
            "Website": user_fav_data["Website"],
            "Image": user_fav_data["Image"]
        })

        # Display the favorites DataFrame
        selection = dataframe_with_selections(favorites_df)
        
        if st.button(f"Remove"):
            # st.write(selection)
            # Remove the product from Firestore
            updated_favorites = {
                "Description": [d for i, d in enumerate(user_fav_data["Description"]) if i not in selection],
                "Image": [k for i, k in enumerate(user_fav_data["Image"]) if i not in selection],
                "Ratings": [l for i, l in enumerate(user_fav_data["Ratings"]) if i not in selection],
                "Price": [p for i, p in enumerate(user_fav_data["Price"]) if i not in selection],
                "Product": [p for i, p in enumerate(user_fav_data["Product"]) if i not in selection],
                "Website": [w for i, w in enumerate(user_fav_data["Website"]) if i not in selection],
            }
            user_fav_ref.set(updated_favorites)
            # st.success(f"{selection} removed from favorites.")
            st.rerun()  # Refresh the page after removal
    else:
        st.write("You have no favorites yet.")
