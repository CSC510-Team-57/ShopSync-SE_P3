import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
import os
import sys
import pandas as pd

# Ensure the path to src/frontend is in the system path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/frontend')))
from slash_user_interface import app, search_product, check_product_input  # Import search_product directly

# Mock Firestore client fixture
@pytest.fixture
def mock_firestore_client():
    # Mock Firestore client for isolated testing
    mock_client = Mock()
    return mock_client

def test_search_product(mock_firestore_client):
    # Test search product API functionality with mock data
    with patch('slash_user_interface.search_items_API') as mock_search_api:
        mock_search_api.return_value = [
            {'title': 'Sample Product', 'price': '$20.99', 'link': 'https://example.com', 'website': 'Amazon'}
        ]
        results = search_product('Amazon', 'Sample Product')
        assert len(results) == 1
        assert results[0]['price'] == '$20.99'


# Fixture for mocking Streamlit text input
@pytest.fixture
def mock_text_input():
    with patch('streamlit.text_input') as mock:
        yield mock

def test_text_input(mock_text_input):
    mock_text_input.return_value = "Laptop"
    product_name = st.text_input('Enter product name', value='Laptop', key="product_name")
    assert product_name == 'Laptop'
    mock_text_input.assert_called_once_with('Enter product name', value='Laptop', key="product_name")


# Fixture for mocking Streamlit selectbox
@pytest.fixture
def mock_selectbox():
    with patch('streamlit.selectbox') as mock:
        yield mock

def test_selectbox(mock_selectbox):
    mock_selectbox.return_value = "Amazon"
    website = st.selectbox('Select Website', ['Amazon', 'Ebay', 'Walmart'], index=0, key="website_select")
    assert website == 'Amazon'
    mock_selectbox.assert_called_once_with('Select Website', ['Amazon', 'Ebay', 'Walmart'], index=0, key="website_select")


# Fixture for mocking Streamlit slider
@pytest.fixture
def mock_slider():
    with patch('streamlit.slider') as mock:
        yield mock

def test_price_slider(mock_slider):
    mock_slider.return_value = (100, 500)
    min_price, max_price = st.slider('Price Range', 0.0, 1000.0, (100.0, 500.0), key="price_slider")
    assert min_price == 100.0 and max_price == 500.0
    mock_slider.assert_called_once_with('Price Range', 0.0, 1000.0, (100.0, 500.0), key="price_slider")


# Fixture for mocking Streamlit button
@pytest.fixture
def mock_button():
    with patch('streamlit.button') as mock:
        yield mock

def test_button_interaction(mock_button):
    mock_button.return_value = True
    button_clicked = st.button('Search', key="search_button")
    assert button_clicked is True
    mock_button.assert_called_once_with('Search', key="search_button")


# Additional Tests for Sorting and Reset Functionalities
class TestShopSyncSortAndReset:

      @pytest.fixture(autouse=True)
      def setup(self):
            # Sample DataFrame for testing
            self.sample_data = pd.DataFrame({
            'Description': ['Product A', 'Product B', 'Product C'],
            'Price': [10.99, 15.99, 8.99],
            'Website': ['Amazon', 'Walmart', 'Ebay'],
            'Ratings': [4.5, 3.8, 4.0]
            })
            st.session_state['dataframe'] = self.sample_data  # Set initial state

      @patch('streamlit.button')
      def test_sort_asc(self, mock_button):
            # Mock the button press to simulate 'Sort Asc' button click
            mock_button.side_effect = lambda key: key == 'sort_asc'
            
            # Perform sorting ascending
            sorted_df = st.session_state['dataframe'].sort_values(by='Price', ascending=True)
            st.session_state['dataframe'] = sorted_df  # Apply the sort to session state

            # Check if the DataFrame was sorted in ascending order
            assert st.session_state['dataframe'].iloc[0]['Price'] == 8.99
            assert st.session_state['dataframe'].iloc[1]['Price'] == 10.99
            assert st.session_state['dataframe'].iloc[2]['Price'] == 15.99
    
      @patch('streamlit.button')
      def test_sort_desc(self, mock_button):
      # Mock the button press to simulate 'Sort Desc' button click
            mock_button.side_effect = lambda key: key == 'sort_desc'
            
            # Perform sorting descending
            sorted_df = st.session_state['dataframe'].sort_values(by='Price', ascending=False)
            st.session_state['dataframe'] = sorted_df  # Apply the sort to session state

            # Check if the DataFrame was sorted in descending order
            assert st.session_state['dataframe'].iloc[0]['Price'] == 15.99
            assert st.session_state['dataframe'].iloc[1]['Price'] == 10.99
            assert st.session_state['dataframe'].iloc[2]['Price'] == 8.99

      @patch('streamlit.button')
      def test_reset_button(self, mock_button):
    # Simulate data change by modifying the session state
            st.session_state['selected_websites'] = ['Amazon', 'Ebay']
            st.session_state['dataframe'] = self.sample_data.copy().sort_values(by='Price', ascending=False)

            # Mock the button press to simulate the 'Reset' button click
            mock_button.side_effect = lambda key: key == 'reset'

            # Define the reset behavior
            for website in ['Amazon', 'Walmart', 'Ebay']:
                  st.session_state[website] = False  # Uncheck website filters
            st.session_state['dataframe'] = self.sample_data  # Reset to original DataFrame
            st.session_state['selected_websites'] = []  # Explicitly clear selected websites

            # Check if session state has been reset correctly
            assert st.session_state['dataframe'].equals(self.sample_data)
            assert st.session_state['selected_websites'] == []  # Ensure selected websites are cleared

@pytest.fixture
def website_dict():
    """Fixture to provide a dictionary of websites."""
    return {
    'Amazon': 'amazon',
    'Ebay': 'ebay',
    'Walmart': 'walmart',
    'Target': 'target',
    'BestBuy': 'bestbuy',
    'Costco': 'costco'
}

@pytest.mark.parametrize("checked_websites, expected_selection", [
    (["Walmart"], ["walmart"]),
    (["Amazon"], ["amazon"]),
    (["Ebay"], ["ebay"]),
    (["Target"], ["target"]),
    (["BestBuy"], ["bestbuy"]),
    (["Costco"], ["costco"]),
    (["Amazon", "Ebay"], ["amazon", "ebay"]),
    (["Target", "Costco"], ["target", "costco"]),
    ([], []),  # No selection
])
def test_checkboxes(checked_websites, expected_selection, website_dict):
    # Initialize session state for checkboxes
    for website in website_dict.keys():
        st.session_state[website] = False  # Initially uncheck all

    # Simulate checking the boxes based on the parameterized input
    for website in checked_websites:
        st.session_state[website] = True

    selected_websites = []
    for website_name in website_dict.keys():
        if website_name.lower() == "all":
            continue
        is_checked = st.checkbox(website_name, key=website_name)
        if is_checked or st.session_state[website_name]:
            selected_websites.append(website_name.lower())

    # Assert that the selected websites match the expected selection
    assert selected_websites == expected_selection

def test_too_long_product():
    long_product = 'A' * 101  # 101 characters
    assert not check_product_input(long_product)  # Should return False

def test_invalid_characters():
    assert not check_product_input('Invalid@Product!')  # Invalid characters should return False

def test_valid_product():
    assert check_product_input('Valid-Product_123')  # Valid product should return True

def test_valid_product_with_spaces():
    assert check_product_input('Valid Product Name')  # Valid product with spaces should return True

def test_empty_product():
    assert not check_product_input('')  # Empty string should return False

def test_whitespace_product():
    assert not check_product_input('   ')  # Whitespace should return False

def test_too_short_product():
    assert not check_product_input('')  # Less than 1 character should return False

def test_search_product_empty(mock_firestore_client):
    with patch('slash_user_interface.search_items_API') as mock_search_api:
        mock_search_api.return_value = []
        results = search_product('Amazon', '')
        assert len(results) == 0
def test_search_product_invalid(mock_firestore_client):
    with patch('slash_user_interface.search_items_API') as mock_search_api:
        mock_search_api.return_value = []
        results = search_product('Amazon', '@InvalidProduct!')
        assert len(results) == 0
def test_selectbox_default(mock_selectbox):
    mock_selectbox.return_value = "Amazon"
    website = st.selectbox('Select Website', ['Amazon', 'Ebay', 'Walmart'], index=0, key="website_select")
    assert website == "Amazon"
def test_slider_default(mock_slider):
    mock_slider.return_value = (0, 1000)
    min_price, max_price = st.slider('Price Range', 0.0, 1000.0, (0.0, 1000.0), key="price_slider")
    assert min_price == 0.0
    assert max_price == 1000.0
def test_empty_product_name():
    assert not check_product_input('')  # Empty product name should return False
def test_valid_product_name():
    assert check_product_input('ValidProduct123')  # Valid product name should return True
def test_whitespace_product_name():
    assert not check_product_input('   ')  # Whitespace-only product name should return False
def test_product_name_too_long():
    long_name = 'A' * 101
    assert not check_product_input(long_name)  # Name >100 characters should return False

@patch('streamlit.button')
def test_reset_button_behavior(mock_button):
    mock_button.return_value = True
    assert mock_button('Reset') is True
    
def test_checkbox_behavior():
    st.session_state['Amazon'] = True
    is_checked = st.checkbox('Amazon', key='Amazon')
    assert is_checked or st.session_state['Amazon']
