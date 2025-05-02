"""
Configuration file for LinkedIn Scraper

This file contains all configurable parameters for the LinkedIn Scraper.
Modify these values according to your requirements.
"""

import random
# LinkedIn Credentials (KEEP THESE SECURE!)
LINKEDIN_EMAIL = "testing"# put your linkedin email addresss
LINKEDIN_PASSWORD = "testing"# put the password

API="testing"# put your gemini api

# Scraping Parameters
COMPANY = "company name"  #try to give full name excluding Pvt ,Ltd etc
SEARCH_QUERY = "skill name or location" # if want multiple skill give it with comma separated 
NUMBER_OF_PROFILES = 1 # Number of profiles to scrape (max 100)


# File Paths
COOKIE_FILE = "cookies.pkl"  

DELAYS = {
    "search": random.randint(1, 5),  # Delay on homepage before searching
    "search_results": random.randint(1, 5),  # Delay after search results load
    "people_page": random.randint(1, 5),  # Delay after loading profile page
    "search_query": random.randint(5, 10),  # Delay before entering the search keywords
    "load_more": random.randint(10, 20),  # Delay after search
    "profile": random.randint(10, 20),  # Delay before profile scraping
    "scroll": random.randint(1, 5),  # Delay after scrolling
    "education": random.randint(10, 20),  # Delay befoe education scraping
    "experience": random.randint(10, 20),  # Delay before experience scraping
    "skills": random.randint(1, 10),  # Delay after skills scraping
}

