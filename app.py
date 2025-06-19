#!/usr/bin/env python3
"""
Baby Maker 5000 - Main Application Entry Point
"""

import streamlit as st
from src.ui.main_page import main_page

def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(
        page_title="Baby Maker 5000 🍼",
        page_icon="🍼",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Run the main page
    main_page()

if __name__ == "__main__":
    main() 