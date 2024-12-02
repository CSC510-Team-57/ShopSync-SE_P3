import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pandas as pd
import os

def fetch_title():
    return "History"

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

# db = firestore.client()
def app(firestore_client=None):
    # Allow mock initialization
    if not firebase_admin._apps:
        initialize_firebase(mock=False)
    
    # If firestore_client is None, initialize it
    if firestore_client is None:
        firestore_client = firestore.client()

    st.title("History")

    # Fetch the user ID (UID) from Firebase Authentication
    user_email = st.session_state.user_email  # Ensure this is set
    user = auth.get_user_by_email(user_email)  # Get the user by email
    uid = user.uid

    # Reference to the user's document in the "history" collection
    user_his_ref = firestore_client.collection("history").document(uid)
    user_his_doc = user_his_ref.get()

    if user_his_doc.exists:
        user_his_data = user_his_doc.to_dict()

        timestamps = list()
        for stamp in user_his_data["Timestamp"]:
            temp = pd.Timestamp(stamp, unit='s', tz='US/Eastern')
            # temp.floor(freq='h')
            timestamps.append(temp.floor(freq='s'))

        # Create a DataFrame from the user's history
        history_df = pd.DataFrame({
            "Search": user_his_data["Search"],
            "Timestamp": timestamps
        })

        # Display the history DataFrame
        st.dataframe(history_df.style, column_config={
            "Link": st.column_config.LinkColumn("URL to Website"),
            "Button": st.column_config.LinkColumn("Add to history"),
        })
    else:
        st.write("You have no history yet.")

# In your main app file, call history.app() to use this
