from scraper import LinkedInScraper
import os
import config

scraper = LinkedInScraper()
os.system("clear")
print("====================== WELCOME TO LINKED IN SCRAPPER =====================================\n\n\n")

scraper.COOKIE_FILE = config.COOKIE_FILE
if not os.path.exists(config.COOKIE_FILE):
    scraper.email = input("Enter your LinkedIn email: ")
    scraper.password = input("Enter your LinkedIn password: ")

scraper.company = input("Enter the company name you want to search: ")
scraper.search_query = input("Enter the parameter (language or location) you want to filter the profiles: ")
scraper.number = int(input("Enter the total number of profile you want to scrape, note that the number should not exceed 100: "))

while scraper.number > 100 and scraper.number < 0:
    print("Incorrect number is given please give the correct number")
    scraper.number = int(input("Enter the total number of profile you want to scrape, note that the numb er should not exceed 100"))

print(f"Scrapping for the following details- Company: {scraper.company}\nNumber:{scraper.number}\nSearh Query:{scraper.search_query}\n")
scraper.scraper()
