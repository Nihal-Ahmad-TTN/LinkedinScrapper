# LinkedIn Scraper

A powerful Python-based tool for automating the extraction of profile data from LinkedIn. This tool utilizes Selenium WebDriver to navigate LinkedIn, search for company employees with specific skills, and extract detailed profile information.

## 🔍 Features

- **Automated LinkedIn Login**: Supports both manual login and cookie-based session persistence
- **Company & Skills Targeting**: Search for employees at specific companies with particular skills
- **Comprehensive Data Extraction**:
  - Personal details (name, location)
  - Professional experience (roles, companies, duration)
  - Educational qualifications
  - Skills
  - AI-generated competency summaries
- **Data Export**: Export results to both CSV and JSON formats
- **Rate Limiting Protection**: Implements random delays between requests to reduce detection risk

## 📋 Prerequisites

- Python 3.6+
- Firefox Browser
- GeckoDriver for Firefox WebDriver
- LinkedIn account

## 🛠️ Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/linkedin-scraper.git
   cd linkedin-scraper
   ```
2. Install required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Download and install GeckoDriver for Firefox WebDriver
4. Update the path to geckodriver in the script:
    ```bash
    self.service = Service(executable_path='/path/to/your/geckodriver')
    ```

## 🚀 Usage
1. Import the LinkedInScraper class:
    ```bash
    from linkedin_scraper import LinkedInScraper
    ```
2. Create an instance and set required parameters:
    ```bash
    scraper = LinkedInScraper()
    scraper.email = "your_linkedin_email@example.com"
    scraper.password = "your_linkedin_password"
    scraper.company = "Target Company Name"
    scraper.search_query = "Target Skill or Keyword"
    scraper.number = 10  # Number of profiles to scrape (max recommended: 100)
    ```
3. Run the scraper:
    ```bash
    scraper.scraper()
    ```

## 📊 Output
- The scraper generates two output files:

    - **<comapny_name>\_<search_keyword>\_<date_time>.csv:** Contains profile data in CSV format
    - **<comapny_name>\_<search_keyword>\_<date_time>.json:** Contains complete profile data in JSON format

## ⚠️ Important Limitations
- **Rate Limiting:** LinkedIn employs request frequency tracking per IP. Excessive scraping can lead to temporary or permanent bans. It's advised to:

    - Limit scraping to max 100 profiles at a time
    - Run the scraper at intervals of several days
    - Use random delays between requests (implemented in the tool)


- **CAPTCHA Challenges:** Suspicious activity may trigger CAPTCHA challenges. The script does not automatically solve these.
- **Authentication Requirements:** LinkedIn requires login for accessing profile data.
- **Technical Barriers:**

    - Dynamic content loading
    - Pagination complexity
    - Data inconsistency across profiles
    - Interference from advertisements


- **Legal Considerations:** Using this tool might violate LinkedIn's Terms of Service. Use responsibly and at your own risk.

## 🔧 Customization
- The script is designed to be extensible. Key areas for customization:

    - **XPath Selectors**: If LinkedIn updates its frontend, you may need to update the XPath selectors in the education() and experience() methods
    - **AI Competency Generation**: Modify the get_competancy() method to customize how competency summaries are generated
    - **Export Format**: Customize the get_csv() and get_json() methods to modify output formats