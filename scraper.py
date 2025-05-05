
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions 
from selenium.webdriver.firefox.service import Service
import pandas as pd
from utils import AIdata
import config
import json
import time
import pickle
import os
import logging
import re
import datetime

# logging.basicConfig(filemode='logfile.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
class NotEnoughNetworkException(Exception):
    """
    Custom exception class to raise user-defined exceptions related to scraping logic.
    """
    def __init__(self, message):
        super().__init__(message)



class LinkedInScraper:
    """
    LinkedInScraper is the class that utomates the process of scraping  data from LinkedIn profiles
    using Selenium and Firefox WebDriver(for now). This class is designed to log in (with cookie support), 
    search for companies's employees, and extract detailed user data including education, 
    work experience, skills, and inferred competency summaries. The final data is exported 
    to CSV and JSON formats.

    Attributes:
        service (Service): Selenium service object to manage the Firefox WebDriver.
        driver (Firefox): The main browser instance used for automation.
        wait (WebDriverWait): WebDriverWait object to handle dynamic loading elements.
        COOKIE_FILE (str): File path for storing and retrieving session cookies.
        email (str): LinkedIn email address (should be set before calling `login`).
        password (str): LinkedIn password (should be set before calling `login`).
        company (str): Target company name for scraping employees.
        search_query (str): Skill or keyword to filter employee search results.
        number (str): Number of employee profiles to scrape.

    Methods:
        exp_count(entries): Converts a list of duration strings (e.g., "2 yrs 3 mos") into total experience.
        save_cookies(): Saves the current session cookies to a file to enable session persistence.
        load_cookies(): Loads previously saved cookies into the browser session.
        login(): Logs into LinkedIn using provided credentials and saves the session cookies.
        education(link, personeDetails): Extracts educational qualifications from a profile.
        subreader(tempDetail): Helper method for nested skill extraction within experience entries.
        experience(link, personeDetails): Extracts professional experience entries including roles, duration, and skills.
        get_competancy(about, experience,title): Uses an AI utility to infer a user's core competency based on experience and bio.
        get_csv(profiles, output_file): Saves all scraped profile data into a CSV file.
        get_json(profiles): Saves all scraped profile data into a JSON file.
        profilereader(peoples): Reads multiple LinkedIn profiles and aggregates the data.
        scraper(): Main function that starts the scraping workflow, including login, navigation, data collection, and file output.

    Usage:
        To use this class, create an instance of LinkedInScraper, populate the necessary fields 
        like `email`, `password`, `company`, `search_query`, and `number`, then call the `scraper()` method.

        Example:
            scraper = LinkedInScraper()
            scraper.email = "user@example.com"
            scraper.password = "securepassword"
            scraper.company = "Google"
            scraper.search_query = "Data Scientist"
            scraper.number = 5
            scraper.scraper()

    Note:
        This class relies on the presence of the `geckodriver` in the specified path('/usr/local/bin/geckodriver') and
        assumes a working Firefox installation. It also expects proper XPath structures,
        which may break if LinkedIn updates their frontend.
        ---------------------------------------------------------------------------------------------------

        Rate Limiting: LinkedIn tracks request frequency per IP; excessive requests can lead to throttling or bans hence max number is limited to 100 and are advised to run the scrapper in days interval

        CAPTCHA Challenges: Triggered by suspicious activity to block bots.

        Authentication Requirements: Key data is behind login walls; automated logins are often detected and blocked.

        Technical Barriers: Includes dynamic content, pagination, inconsistent data, and interference from ads.

    """

    def __init__(self):
        # logging.info("Initializing LinkedInScraper...")
        """
        Initializes the Firefox WebDriver, sets WebDriverWait, and defines the cookie file path.
        """
        self.service = Service(executable_path='/usr/local/bin/geckodriver')
        self.driver = webdriver.Firefox(service= self.service)
        self.wait = WebDriverWait(self.driver, 10)
        self.COOKIE_FILE = "cookies.pkl"
        self.email = ''
        self.password = ''
        self.company = ''
        self.search_query = ''
        self.number = ''

    def exp_count(self, entries):
        # logging.info("Calculating total professional experience...")
        """
        Calculates total professional experience from a list of duration strings.

        Args:
            entries (list): List of strings containing experience durations.

        Returns:
            str: Total experience in years and months.
        """
        total_months = 0
        for entry in entries:

            years = re.search(r'(\d+)\s*yrs?', entry)
            months = re.search(r'(\d+)\s*mos?', entry)

            year_val = int(years.group(1)) if years else 0
            month_val = int(months.group(1)) if months else 0

            total_months += year_val * 12 + month_val
        total_years = total_months // 12
        remaining_months = total_months % 12
        return f"{total_years} yrs {remaining_months} mos"



    def save_cookies(self):
        # logging.info("Saving cookies to file...")
        """
        Saves the current browser session cookies to a file.
        """
        with open(self.COOKIE_FILE, "wb") as file:
            pickle.dump(self.driver.get_cookies(), file)



    def load_cookies(self):
        # logging.info("Loading cookies from file...")
        """
        Loads saved cookies into the current browser session.
        """
        self.driver.get("https://www.linkedin.com")
        time.sleep(config.DELAYS["login_page"])
        with open(self.COOKIE_FILE, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                self.driver.add_cookie(cookie)



    def login(self):
        # logging.info("Logging into LinkedIn...")
        """
        Logs into LinkedIn using credentials
        """
        login_url = "https://www.linkedin.com/login"
        self.driver.get(login_url)
        time.sleep(config.DELAYS["login_page"])
       
        self.driver.maximize_window()

        username = self.wait.until(expected_conditions.presence_of_element_located((By.ID, "username")))
        password = self.wait.until(expected_conditions.presence_of_element_located((By.ID, "password")))

        username.clear()
        password.clear()

        username.send_keys(self.email)
        time.sleep(1)
        password.send_keys(self.password)
        time.sleep(1)

        logButton = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, "/html/body/div/main/div[2]/div[1]/form/div[4]/button")))
        logButton.send_keys(Keys.ENTER)


    def get_contact_info(self, link, personDetails):
        """
        Extracts contact information from a LinkedIn profile.

        Args:
            link (str): Direct URL to the contact info section.
            personeDetails (dict): Dictionary to append contact data into.
        """
        # logging.info("Extracting contact information...")
        self.driver.get(link)
        contact_info = {}
        count = 0
        while True:
            count += 1    
            try:
                
                heading = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, f"//section/div/section[{count}]/h3"))).text
                print("got heading")

                try:
                    content = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, f"//section/div/section[{count}]/div/a"))).text
                except Exception as e:
                    try:
                        content = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, f"//section/div/section[{count}]/div/span"))).text
                    except Exception as e:
                        try:
                            content = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, f"//section/div/section[{count}]/ul/li/span[1]"))).text
                        except Exception as e:
                            pass
                
                contact_info[f'{heading}'] = content

            except Exception as e:
                break
        
        personDetails['Contact_info'] = contact_info
        print(personDetails['contact_info'])




    def education(self, link, personeDetails):
        # logging.info("Extracting educational history...")
        """
        Extracts educational history from a LinkedIn profile.

        Args:
            link (str): Direct URL to the education section of a profile.
            personeDetails (dict): Dictionary to append education data into.
        """
        tempEducation=[]
        self.driver.get(link)
        time.sleep(config.DELAYS["education"])

        count = 0
        while True:
            temp = {}
            try:
                count += 1
                tempDegree = ""
                tempSchool = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, f"//li[{count}]/div/div/div[2]/div[1]/a/div/div/div/div/span[1]")))
                try:
                    tempDegree = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, f"//li[{count}]/div/div/div[2]/div[1]/a/span/span")))
                except Exception as e:
                    pass
                temp["Institute"] = tempSchool.text
                temp["Qualification"] = tempDegree.text
            except Exception as e:
                break 
            tempEducation.append(temp)
        personeDetails["Education"] = tempEducation




    def experience(self, link, personeDetails):
        # logging.info("Extracting professional experience...")
        """
        Extracts professional experience from a LinkedIn profile.

        Args:
            link (str): Direct URL to the experience section.
            personeDetails (dict): Dictionary to append experience data into.
        """
        self.driver.get(link)
        time.sleep(config.DELAYS["experience"])

        tempyear = []
        personExpDetails = []
        
        count = 0
        while True:
            tempDetail = {}
            try:
                count += 1
                skill = ""
                role = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, f"/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul/li[{count}]/div/div/div[2]/div/a/div/div/div/div/span[1]")))
                company = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, f"/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul/li[{count}]/div/div/div[2]/div/a/span[1]/span[1]")))
                year = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, f"/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul/li[{count}]/div/div/div[2]/div/a/span[2]/span[1]")))
                tempDetail["role"] = role.text
                tempDetail["company"] = company.text.split("·")[0]
                tempDetail["year"] = year.text.split("·")[1]
                try:
                    time.sleep(config.DELAYS["skills"])
                    skill = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, f"//li[{count}]/div/div/div[2]/div[2]/ul/li[2]/div/ul/li/div/div/div/span")))
                    tempDetail["skill"] = skill.text.split(":")[1].split("·")
                except Exception as e:
                        pass     
            except Exception as e:
                try:
                    company = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, f"/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul/li[{count}]/div/div/div[2]/div[1]/a/div/div/div/div/span[1]")))
                    year = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, f"/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul/li[{count}]/div/div/div[2]/div[1]/a/span/span[1]")))
                    tempDetail["company"] = company.text.split("·")[0]
                    tempDetail["year"] = year.text.split("·")[1]
                    self.subreader(tempDetail) 

                except Exception as e:
                    break
            tempyear.append(tempDetail["year"])
            personExpDetails.append(tempDetail)
     
        personeDetails["Total_Experiance"] = self.exp_count(tempyear)    
        personeDetails["Experience"] = personExpDetails             

    def get_competancy(self, about, experience,title):
        # logging.info("Generating competency summary using AI...")
        """
        Generates a competency summary using external AI utility.

        Args:
            about (str): About section text.
            experience (list): List of experience dicts.

        Returns:
            str: Competency.
        """
        return AIdata(experience, about, title).strip()


    def get_json(self, profiles):
        # logging.info("Exporting data to JSON...")
        """
        Reads and parses individual LinkedIn profiles.

        Args:
            peoples (list): List of profile URLs.
        """
        with open(f"{self.company}_{self.search_query}_{datetime.datetime.now()}.json", 'w') as file:
            json.dump(profiles, file, indent=4)
        print(f"Json file is saved with name " + file.name)


    def get_csv(self, profiles):
        # logging.info("Exporting data to CSV...")
        """
        Exports scraped data into a CSV file.

        Args:
            profiles (list): List of profile dictionaries.
            output_file (str): Output CSV filename.
        """

        flat_data = []

        for profile in profiles:
            base = {
                'Name': profile.get('Name'),
                'Profile Link': profile.get('Profile Link'),
                'Location': profile.get('Location'),
                'Total Experience': profile.get('Total_Experiance'),
                'Competency': profile.get('Competancy'),
                "Title":profile.get('Title')
            }
            

            base['Education'] = '; '.join(
                f"{edu.get('Institute')}: {edu.get('Qualification')}" 
                for edu in profile.get('Education', [])
            )

            base['Experience'] = '; '.join(
                f"{exp.get('role')} at {exp.get('company')} ({exp.get('year')})" 
                for exp in profile.get('Experience', [])
            )

            flat_data.append(base)

        df = pd.DataFrame(flat_data)
        filename = f"{self.company}_{self.search_query}_{datetime.datetime.now()}.csv"
        df.to_csv(filename, index=False)
        print(f"CSV file is saved with name " + filename)



    def subreader(self, tempDetail):
        # logging.info("Extracting sub-skills from experience...")
        """
        Helper function to extract sub-skills from nested structures under experience.

        Args:
            tempDetail (dict): Experience entry to append skills into.
        """
        temp = []
        for count in range(1, 5):
            try:
                skill = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, f"/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul/li[2]/div/div/div[2]/div[2]/ul/li/div/div/div[1]/ul/li[{count}]/div/div/div[2]/div[2]/ul/li[2]/div/ul/li/div/div/div/span[1]")))
                temp.append(skill.text.split(":")[1].split("·"))
            except Exception as e:
                pass
        tempDetail["skill"] = temp




    def profilereader(self, peoples):
        # logging.info("Reading and scraping individual LinkedIn profiles...")
        """
        Saves the scraped profiles data as a JSON file.
        """
        profiles = []
        for people in peoples:
            personeDetails = {}
            self.driver.get(people)
            time.sleep(config.DELAYS["profile"])

            personeDetails["Profile Link"] = people
            about = ""
            personeDetails["Title"] = ""

            try:
                about = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, "//section[2]/div[3]/div/div/div/span"))).text
            except Exception as e:
                pass    

            personeDetails["Name"] = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, "//span/a/h1"))).text
            print("Scrapping started for this profile :" + personeDetails["Name"])

            try:
                personeDetails["Title"] = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, "//section/div[2]/div[2]/div/div[2]"))).text
            except Exception as e:
                pass    

            personeDetails["Location"] = ""
            try:
                personeDetails["Location"] = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, "//div[2]/span"))).text

            except Exception as e:
                pass    

            self. get_contact_info(people + "/overlay/contact-info", personeDetails)
            self.education(people + "/details/education", personeDetails)
            self.experience(people + "/details/experience", personeDetails)
            personeDetails["Competancy"] = self.get_competancy(about, personeDetails["Experience"], personeDetails["Title"])
            profiles.append(personeDetails)
            print("Scrapping completed for this profile :" + personeDetails["Name"])

        self.get_json(profiles)
        self.get_csv(profiles)


    def scraper(self):
        # logging.info("Starting the scraping process...")
        """
        Main function to handle navigation and scraping workflow on LinkedIn.
        """
        print("Scrapping is starting, Please Wait")
       
        if os.path.exists(self.COOKIE_FILE):
            print("[*] Loading cookies...")
            self.driver.maximize_window()
            self.load_cookies()
            self.driver.refresh()
            

        else:
            print("[*] No cookie file found. Logging in manually...")
            self.login()    
            time.sleep(config.DELAYS["security_check"])
            self.save_cookies()
            

        # Search for the company
        time.sleep(config.DELAYS["search"])
        searchBar = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, '/html/body/div[6]/header/div/div/div/div[1]/input')))
        searchBar.clear()
        searchBar.send_keys(self.company + Keys.ENTER)

        # Filter for companies, select first result, go to "People"
        selectCompany = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, "//button[text()='Companies']")))
        selectCompany.send_keys(Keys.ENTER)

        time.sleep(config.DELAYS['search_results'])
        chooseCompany = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, "//div/span/span/a")))
        chooseCompany.send_keys(Keys.ENTER)

        time.sleep(config.DELAYS['people_page'])
        companyPeople = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, "//a[text()='People']")))
        companyPeople.send_keys(Keys.ENTER)

        # Filter employees by skill (e.g., Java)
        time.sleep(config.DELAYS['search_query'])
        selectPeople = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, "//div/textarea")))
        selectPeople.clear()
        selectPeople.send_keys(self.search_query + Keys.ENTER)

        # Scrape people links
        peopleList = []
        count = -1
        notMemberCount = 0
        counter = 0

        while True:
            count += 1
            
            try:
                time.sleep(config.DELAYS['scroll'])
                profileData = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, f'//*[@id="org-people-profile-card__profile-image-{count}"]')))
                temp = profileData.get_attribute('href')
                if temp is not None:
                    counter += 1
                    peopleList.append(temp.split("?")[0])
                    print(counter)
                    if len(peopleList) == self.number:
                        self.profilereader(peopleList)
                        break
            #     else:
            #         notMemberCount += 1
            #         if (notMemberCount / count) > 0.5 and count == 10:
            #             raise NotEnoughNetworkException("You doesnt have the network reach to that company please expand your network then try again")
                        

            # except NotEnoughNetworkException as e:
            #     print(e)
            #     break


            except Exception as e:
                try:
                    time.sleep(config.DELAYS["load_more"])
                    loadmore = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[3]/div/div[2]/div/div[2]/main/div[2]/div/div/div[2]/div/div[2]/div/button")))
                    loadmore.send_keys(Keys.ENTER)

                except Exception as e:
                    if len(peopleList) > 0:
                        self.profilereader(peopleList)
                    else:
                        break    
                        

        print("Scrapping is completed. Please review your file")
        self.driver.quit()

if __name__ == "__main__":
    obj = LinkedInScraper()
    obj.scraper()

                