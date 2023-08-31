# Script used to Pull NVD CVE data 
# API Reference : https://nvd.nist.gov/developers/vulnerabilities
# Created : August 20 2023
import requests
import json
from datetime import datetime, timedelta

def get_date_range():
    """Function : Get starting and end date based on delta. 7 days from today = edate. Today = sdate."""
    today = datetime.now()
    thirty_days_ago = today - timedelta(days=7)
    
    edate = today.strftime("%Y-%m-%d")
    sdate = thirty_days_ago.strftime("%Y-%m-%d")
    
    return sdate, edate

# pull Data and assign to variable
def fetch_data(api_urls):
    """ Function : Using requests library, get content from response from each of the URL's passed through. Saving each response to response_dict"""
    response_dict = {}
    counter = 0
    for url in api_urls:
        response = requests.get(url)
        response.raise_for_status()
        response_dict["response{0}".format(counter)] = response.content
        counter = counter + 1
    return response_dict
def parse_json(data):
    """ Function : Parse the data, search for keywords and print to shell"""
    # Assign variables based on dictionary key from fetch_data function. 
    windows_data = data['response0']  
    linux_data = data['response1']
    cisco_data = data['response2']
    # List to store each of the variables to loop through
    data_list = [windows_data,linux_data,cisco_data]
    found_cve_list = []
    # enumerate used to find index, seperating the vulns based on keywords 
    for index, d in enumerate(data_list):
        if index == 0:
            print('Windows')
        elif index == 1: 
            print('Linux')
        elif index == 2: 
            print('Cisco')
        json_data = json.loads(d)
        vulns = json_data['vulnerabilities']
        c = 0
        print("\n")
        for i in vulns:
            cve_id = vulns[c]['cve']['id']
            found_cve_list.append(cve_id) 
            cve_published = vulns[c]['cve']['published']
            cve_description = vulns[c]['cve']['descriptions'][0]['value']
            print(f"ID : {cve_id}")
            print(f"Description : {cve_description}")
            print("\n")
            c = c+1
          
# Get date range
sdate, edate = get_date_range()
# URL 
windows_api_url = f"https://services.nvd.nist.gov/rest/json/cves/2.0/?pubStartDate={sdate}T00:00:00.000&pubEndDate={edate}T00:00:00.000&keywordSearch=windows"
linux_api_url = f"https://services.nvd.nist.gov/rest/json/cves/2.0/?pubStartDate={sdate}T00:00:00.000&pubEndDate={edate}T00:00:00.000&keywordSearch=linux"
cisco_api_url = f"https://services.nvd.nist.gov/rest/json/cves/2.0/?pubStartDate={sdate}T00:00:00.000&pubEndDate={edate}T00:00:00.000&keywordSearch=cisco"
# API url list
api_urls = [windows_api_url,linux_api_url,cisco_api_url]
# Fetch data
#print(api_urls)
nvd_data = fetch_data(api_urls)

jsondata = parse_json(nvd_data)


