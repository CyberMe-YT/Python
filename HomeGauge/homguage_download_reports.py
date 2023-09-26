# Purpose: Login to HomeGauge, scrape download urls for inspection reports based on ID's exported from HomeGauge. HomeGauge did not provide a way to export all reports to local computer
# Using selenium we are able to authenticate to the server and then scrape the elements of page using beautiful soup. We download reports, save to directory, rename to report_id currently being downloaded. 

import os
import pandas as pd
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup
import requests
import time

download_folder = r'<DOWNLOAD_FOLDER>'

def rename_file(report_id):
    time.sleep(2)
    directory_path = r'<DOWNLOAD_FOLDER>'
    for filename in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, filename)):
            # Check if the filename contains the words "FullReport"
            if 'FullReport' in filename:
                new_filename = f'{report_id}.pdf'
                
                # Rename the file to the new filename
                old_filepath = os.path.join(directory_path, filename)
                new_filepath = os.path.join(directory_path, new_filename)
                os.replace(old_filepath, new_filepath)

    return 

# Specify the path to your report IDs CSV file
report_ids_csv_file = r'<report_ids_csv_file>'

# Define your authentication credentials (replace with your actual credentials)
username = '<username>'
password = '<password>'


# Function to log in using Selenium
def login_with_selenium(username, password):
    login_url = 'https://www.homegauge.com/login.html'
    
    # Configure Chrome WebDriver (make sure you have Chromedriver installed)
    driver = webdriver.Chrome()
    driver.get(login_url)
    
    # Find and interact with the login form (replace with actual form field names)
    username_field = driver.find_element(By.NAME, "userName")
    password_field = driver.find_element(By.NAME, "password")
    
    # Input your username and password
    username_field.send_keys(username)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)  # Submit the form
    
    # Wait for successful login (you may need to adjust the wait time)
    driver.implicitly_wait(10)
    
    return driver

# Function to scrape the PDF download URL from the report page
def scrape_pdf_url(report_id, driver):
    url = f'https://www.homegauge.com/report/{report_id}/?pdf=true'
    
    # Go to the URL with the authenticated session
    driver.get(url)
    
    # Get the page source and parse it with BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find the PDF download link within the <div class="pdfButton"> element
    pdf_button_div = soup.find('div', class_='pdfButton')
    if pdf_button_div:
        pdf_url_relative = pdf_button_div.find('a')['href']
        pdf_url = f'https://www.homegauge.com{pdf_url_relative}?dl=true'
        print (pdf_url)
        return pdf_url
    
    return None  # Return None if the PDF download link is not found

try:
    # Perform login using Selenium
    driver = login_with_selenium(username, password)

    # Read the report IDs from the CSV file
    report_ids_df = pd.read_csv(report_ids_csv_file)

    # Ensure that the column name matches the actual column name in your CSV file
    # Modify 'Column_Name' to the actual column name containing the report IDs
    report_id_list = report_ids_df['Report ID'].tolist()

    # Iterate through the list of report IDs
    for report_id in report_id_list:
        # Scrape the PDF download URL from the report page
        pdf_url = scrape_pdf_url(report_id, driver)
        
        if pdf_url:
            # Download and save the PDF report from the scraped URL
            driver.get(pdf_url)
            rename_file(report_id)
    

except FileNotFoundError:
    print(f"FileNotFoundError: The file '{report_ids_csv_file}' was not found.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    # Close the WebDriver when done
    if driver:
        driver.quit()
