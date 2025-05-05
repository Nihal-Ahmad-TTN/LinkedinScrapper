"""
Configuration file for LinkedIn Scraper

This file contains all configurable parameters for the LinkedIn Scraper.
Modify these values according to your requirements.
"""

import random

# API Key for Gemini AI
# Replace with your actual API key
# Ensure you have the required permissions and usage limits for the API
API="test"

# File Paths
# Path to the Cookie file where scraped data will be saved
COOKIE_FILE = "cookies.pkl"  


# Randomized delays to mimic human behavior and avoid detection
# These delays are in seconds and can be adjusted as needed
# The delays are randomized to make the scraping process less predictable and more human-like.
DELAYS = {
    "login_page": random.randint(3, 10), 
    "security_check": random.randint(30, 60),
    "search": random.randint(3, 10),
    "search_results": random.randint(3, 10),
    "people_page": random.randint(3, 5),
    "search_query": random.randint(5, 10),
    "load_more": random.randint(5, 10),
    "profile": random.randint(5, 10),
    "contact_info": random.randint(5, 10),
    "scroll": random.randint(3, 5),
    "education": random.randint(10, 20),
    "experience": random.randint(10, 20),
    "skills": random.randint(3, 5),
}

