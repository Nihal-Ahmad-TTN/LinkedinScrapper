from scraper import LinkedInScraper
import os
import config


scraper = LinkedInScraper()
os.system("clear")
print("====================== WELCOME TO LINKED IN SCRAPPER =====================================\n\n\n")
scraper.email = config.LINKEDIN_EMAIL
scraper.password = config.LINKEDIN_PASSWORD
scraper.company = config.COMPANY
scraper.number = config.NUMBER_OF_PROFILES


while scraper.number > 100 and scraper.number <= 0:
    print("Incorrect number is given please give the correct number")
    scraper.number = int(input("Enter the total number of profile you want to scrape, note that the numb er should not exceed 100"))

scraper.search_query = config.SEARCH_QUERY
scraper.COOKIE_FILE = config.COOKIE_FILE

print(f"Scrapping for the following details- Company: {config.COMPANY}\nNumber:{config.NUMBER_OF_PROFILES}\nSearh Query:{ config.SEARCH_QUERY}")
scraper.scraper()
