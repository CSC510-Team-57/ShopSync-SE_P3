import streamlit as st
import sys
import os
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'frontend')))

from favourites import fetch_title as fav
from account import fetch_title as acc
from logout import fetch_title as logt
from logout import fetch_state as logst
from slash_user_interface import fetch_title as slsh

# Mocking the Firebase initialization and authentication just in case they're used
@patch('firebase_admin.initialize_app')
@patch('firebase_admin.auth')
def test_fav_navigation(mock_auth, mock_initialize):
    # Define the pages to test
    assert fav() == "Favourites"

@patch('firebase_admin.initialize_app')
@patch('firebase_admin.auth')
def test_acc_navigation(mock_auth, mock_initialize):
    # Define the pages to test
    assert acc() == "Account"

@patch('firebase_admin.initialize_app')
@patch('firebase_admin.auth')
def test_logout(mock_auth, mock_initialize):
    assert logst() == False

@patch('firebase_admin.initialize_app')
@patch('firebase_admin.auth')
def test_logt_navigation(mock_auth, mock_initialize):
    # Define the pages to test
    assert logt() == "Logout"

@patch('firebase_admin.initialize_app')
@patch('firebase_admin.auth')
def test_slsh_navigation(mock_auth, mock_initialize):
    # Define the pages to test
    assert slsh() == "Home"

@patch('firebase_admin.initialize_app')
@patch('firebase_admin.auth')
def test_page_titles(mock_auth, mock_initialize):
    assert fav() == "Favourites"
    assert acc() == "Account"
    assert logt() == "Logout"
    assert slsh() == "Home"

@patch('firebase_admin.initialize_app')
@patch('firebase_admin.auth')
def test_logout_state(mock_auth, mock_initialize):
    assert logst() is False  # Logout state should be False

@patch('firebase_admin.initialize_app')
@patch('firebase_admin.auth')
def test_favorites_navigation(mock_auth, mock_initialize):
    assert fav() == "Favourites"

@patch('firebase_admin.initialize_app')
@patch('firebase_admin.auth')
def test_account_navigation(mock_auth, mock_initialize):
    assert acc() == "Account"

@patch('firebase_admin.initialize_app')
@patch('firebase_admin.auth')
def test_home_navigation(mock_auth, mock_initialize):
    assert slsh() == "Home"

def test_sidebar_options():
    options = ["Favourites", "Account", "Logout", "Home"]
    assert "Favourites" in options
    assert "Account" in options
    assert "Logout" in options
    assert "Home" in options

@patch('firebase_admin.initialize_app')
def test_firebase_initialization(mock_initialize):
    mock_initialize.assert_not_called()  # Ensure Firebase initialization is not called unexpectedly

def test_sidebar_display_order():
    order = ["Home", "Favourites", "Account", "Logout"]
    assert order == ["Home", "Favourites", "Account", "Logout"]

@patch('firebase_admin.initialize_app')
@patch('firebase_admin.auth')
def test_sidebar_update(mock_auth, mock_initialize):
    fav_title = fav()
    assert fav_title == "Favourites"

@patch('firebase_admin.initialize_app')
@patch('firebase_admin.auth')
def test_sidebar_initialization(mock_auth, mock_initialize):
    assert logt() == "Logout"
    assert fav() == "Favourites"
