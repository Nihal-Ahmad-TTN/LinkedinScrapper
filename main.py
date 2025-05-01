from scraper import LinkedInScraper
import os
import config


linkedin = LinkedInScraper()
os.system("clear")
print("====================== WELCOME TO LINKED IN SCRAPPER =====================================\n\n\n")
linkedin.email = config.LINKEDIN_EMAIL
linkedin.password =config.LINKEDIN_PASSWORD
linkedin.company = config.COMPANY
linkedin.number=config.NUMBER_OF_PROFILES


while linkedin.number >100 and linkedin.number<=0:
    print("Incorrect number is given please give the correct number")
    linkedin.number=int(input("Enter the total number of profile you want to scrape, note that the numb er should not exceed 100"))

linkedin.search_query = config.SEARCH_QUERY

linkedin.COOKIE_FILE = config.COOKIE_FILE
print(f"Scrapping for the following details- Company: {config.COMPANY}\nNumber:{config.NUMBER_OF_PROFILES}\nSearh Query:{ config.SEARCH_QUERY}")
linkedin.scraper()
