import unittest
from unittest.mock import patch, MagicMock
import streamlit as st
import os
import sys

# Add the path to your app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'frontend')))

# Import the app function to test
from favourites import app, initialize_firebase

class TestFavouritesFunctions(unittest.TestCase):

    def setUp(self):
        # Set up session state for the user
        st.session_state.user_email = "vd@gmail.com"  # Use a real user email
        self.user_uid = "vd"  # Replace with the actual UID for the user with favorites
        
        # Mock Firestore client and Firestore functions
        self.mock_firestore_client = MagicMock()
        self.mock_document = MagicMock()
        
        # Set up the mock for Firestore
        self.mock_firestore_client.collection.return_value.document.return_value = self.mock_document
        
        # Patch the firebase_admin.firestore.client to return the mock
        patch('firebase_admin.firestore.client', return_value=self.mock_firestore_client).start()

        # Patch the firebase_admin.initialize_app function
        patch('firebase_admin.initialize_app').start()

        # Patch the firebase_admin.auth.get_user_by_email function
        self.mock_auth_user = MagicMock()
        self.mock_auth_user.uid = self.user_uid
        patch('firebase_admin.auth.get_user_by_email', return_value=self.mock_auth_user).start()

        # Mock initialize_firebase to use the mock version
        patch('favourites.initialize_firebase', side_effect=lambda mock: None).start()

    def tearDown(self):
        patch.stopall()  # Stop all patches after each test

    def test_favourites_page_with_data(self):
        # Arrange: Mock the Firestore document data
        self.mock_document.get.return_value.exists = True
        self.mock_document.get.return_value.to_dict.return_value = {
            "Description": ["Favorite Item 1", "Favorite Item 2"],
            "Website": ["http://example.com/item1", "http://example.com/item2"],
            "Image": ["http://example.com/item1", "http://example.com/item2"],
            "Price": [10.99, 20.49],
            "Product": ["Item 1", "Item 2"],
            "Ratings": [4.4, 5],
        }

        # Act
        app()  # Call the app function (no need to pass firestore_client since it's patched)

        # Assert: Check if the user's document exists in Firestore
        user_fav_doc = self.mock_firestore_client.collection("favourites").document(self.user_uid).get()
        self.assertTrue(user_fav_doc.exists, "User favorites document should exist.")

    def test_favourites_page_no_data(self):
        # Arrange: Set user_email to a user without favorites
        st.session_state.user_email = "srv@gmail.com"  # Use a real user email without favorites
        self.user_uid = "srv"  # Replace with a non-existent UID

        # Set up the mock to return a document that does not exist
        self.mock_document.get.return_value.exists = False

        # Act
        app()  # Call the app function (no need to pass firestore_client since it's patched)

        # Assert: Check that the user's document does not exist
        user_fav_doc = self.mock_firestore_client.collection("favourites").document(self.user_uid).get()
        self.assertFalse(user_fav_doc.exists, "User favorites document should not exist.")

# Run the tests
if __name__ == '__main__':
    unittest.main()
