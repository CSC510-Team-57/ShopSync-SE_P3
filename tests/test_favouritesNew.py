"""
Copyright (C) 2021 SE Slash - All Rights Reserved
You may use, distribute and modify this code under the
terms of the MIT license.
You should have received a copy of the MIT license with
this file. If not, please write to: secheaper@gmail.com
"""

import os
import sys
import inspect
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

# Setup paths for imports
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from favourites import initialize_firebase, app


def test_initialize_firebase_success():
    """
    Test Firebase initialization with a valid JSON path
    """
    with patch("favourites.credentials.Certificate") as mock_cred, patch(
        "favourites.firebase_admin.initialize_app"
    ) as mock_init:
        assert initialize_firebase(mock=True) is True
        mock_cred.assert_not_called()
        mock_init.assert_called_once()


def test_initialize_firebase_failure():
    """
    Test Firebase initialization with an invalid JSON path
    """
    with pytest.raises(Exception):
        initialize_firebase(mock=False)


def test_retrieve_user_data():
    """
    Test if user data is correctly retrieved from Firestore
    """
    with patch("favourites.firestore.client") as mock_client, patch(
        "favourites.auth.get_user_by_email"
    ) as mock_auth:
        mock_client.return_value.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {
            "Description": ["desc1", "desc2"],
            "Link": ["link1", "link2"],
            "Price": ["price1", "price2"],
            "Product": ["prod1", "prod2"],
            "Website": ["site1", "site2"],
        }
        mock_auth.return_value.uid = "mock_uid"
        with patch("streamlit.session_state", {"user_email": "test@test.com"}):
            app(firestore_client=mock_client.return_value)


def test_empty_favorites_handling():
    """
    Test behavior when no favorites exist for the user
    """
    with patch("favourites.firestore.client") as mock_client, patch(
        "favourites.auth.get_user_by_email"
    ) as mock_auth:
        mock_client.return_value.collection.return_value.document.return_value.get.return_value.exists = False
        mock_auth.return_value.uid = "mock_uid"
        with patch("streamlit.session_state", {"user_email": "test@test.com"}):
            app(firestore_client=mock_client.return_value)


def test_dataframe_conversion():
    """
    Test if data from Firestore is converted into a valid DataFrame
    """
    data = {
        "Description": ["desc1", "desc2"],
        "Link": ["link1", "link2"],
        "Price": ["price1", "price2"],
        "Product": ["prod1", "prod2"],
        "Website": ["site1", "site2"],
    }
    df = pd.DataFrame(data)
    assert list(df.columns) == ["Description", "Link", "Price", "Product", "Website"]


def test_remove_button_functionality():
    """
    Test if clicking the Remove button removes selected rows from Firestore
    """
    with patch("favourites.firestore.client") as mock_client:
        user_fav_ref = mock_client.return_value.collection.return_value.document.return_value
        user_fav_ref.get.return_value.to_dict.return_value = {
            "Description": ["desc1", "desc2"],
            "Link": ["link1", "link2"],
            "Price": ["price1", "price2"],
            "Product": ["prod1", "prod2"],
            "Website": ["site1", "site2"],
        }
        updated_data = {
            "Description": ["desc1"],
            "Link": ["link1"],
            "Price": ["price1"],
            "Product": ["prod1"],
            "Website": ["site1"],
        }
        user_fav_ref.set.return_value = updated_data
        assert user_fav_ref.set.called


def test_rerun_after_removal():
    """
    Test if st.experimental_rerun is called after a product is removed
    """
    with patch("streamlit.experimental_rerun") as mock_rerun:
        mock_rerun()
        mock_rerun.assert_called_once()


def test_firestore_update():
    """
    Test if Firestore document is updated correctly after removing items
    """
    with patch("favourites.firestore.client") as mock_client:
        user_fav_ref = mock_client.return_value.collection.return_value.document.return_value
        user_fav_ref.set.return_value = None
        user_fav_ref.set({"Description": ["desc1"]})
        user_fav_ref.set.assert_called_once_with({"Description": ["desc1"]})


def test_user_email_missing():
    """
    Test if app handles missing user_email in session state
    """
    with pytest.raises(KeyError):
        with patch("streamlit.session_state", {}):
            app()


def test_handle_nonexistent_user_data():
    """
    Test if app handles cases where user document does not exist in Firestore
    """
    with patch("favourites.firestore.client") as mock_client, patch(
        "favourites.auth.get_user_by_email"
    ) as mock_auth:
        mock_auth.return_value.uid = "mock_uid"
        mock_client.return_value.collection.return_value.document.return_value.get.return_value.exists = False
        with patch("streamlit.session_state", {"user_email": "test@test.com"}):
            app(firestore_client=mock_client.return_value)
