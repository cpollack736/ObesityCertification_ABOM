# Last Updated: 10.11.19
# Last Updated By: CCP

#%% Import Libraries and Packages

import requests, html5lib, pandas as pd, configparser, os, time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


#%% Bring in HTML

abom_data = pd.DataFrame(columns=['Name', 'Additional Board Certification', 'Initial Certification', 'City', 'State/Province'])


#%% Iterate Over ABOM Page and Pull Diplomates

for i in range(0, 169): #Hard coded page numbers
    print("Now scraping page {}".format(i)) #Print what level on

    #Initialize URL to search
    URL = "https://abom.learningbuilder.com/public/membersearch?slug=Search&model.FirstName=&model.LastName=&model.UniqueId=&model.City=&model.State=&performSearch=true&_p={}&_s=20&_o=LastName&_d=".format(i)

    #Bring in URL value
    r = requests.get(URL)

    #Put into beautiful soup format
    soup = BeautifulSoup(r.content, 'html5lib')

    td_elements = soup.find_all('table')[0].find_all('td') #Pull all the TD elements individually

    for td in range(0, len(td_elements),9): # For each td element in groups of 9
        abom_data = abom_data.append({'Name': td_elements[td],
                                          'Additional Board Certification': td_elements[td+3], #Adds unique users, streamers, and total views to data set
                                          'Initial Certification': td_elements[td+4],
                                          'City': td_elements[td+6],
                                          'State/Province': td_elements[td+7]}, ignore_index = True)

#%% Export ABOM Data

abom_data.to_csv('/Users/cpollack/Documents/Dartmouth/Research/Obesity Certification/Data/ABOM191011.csv', index = None, header=True)


#%% Read separate name lists into Python
names_nodups = pd.read_csv('NoDuplicatedNames_191011.csv')
names_dups = pd.read_csv('DuplicatedNames_191011.csv')

#%% Scrape profiles of physicians without duplicated names
additional_info = pd.DataFrame() #Initializes Data Frame with just the name

for x in names_nodups['x']: #For each name
    print("Now analyzing {}".format(x))

    dictionary = {'Name': x}

    x = x.replace(" ", "-") + "-md" #Create new searchable string with Doximity

    URL = "https://www.doximity.com/pub/" + x #Creates new URL

    #Bring in URL value
    r = requests.get(URL)

    #Put into beautiful soup format
    soup = BeautifulSoup(r.content, 'html5lib')

    sections = soup.findAll('section') #Pull all the sections of the individual's profile

    for sect in sections: #For each section, pull the text into the appropriate category
        dictionary[str(sect['class'][1])] = sect.get_text()

    additional_info = additional_info.append(dictionary, ignore_index = True) #Update database
    
    print("Dictionary had {} entries".format(len(dictionary)))
    time.sleep(10)

#%% Export additional Doximity Data

additional_info.to_csv('/Users/cpollack/Documents/Dartmouth/Research/Obesity Certification/Data/ABOM_Additional191011.csv', index = None, header=True)

#%% Import names that didn't have any pulls
names_leftover = pd.read_csv('NoDoximity_191015.csv')

#%% Run Doximity checking DO instead of MD (should have added to above looop but oh wel)

additional_info_do = pd.DataFrame() #Initializes Data Frame with just the name

for x in names_leftover['Name']: #For each name
    print("Now analyzing {}".format(x))

    dictionary = {'Name': x}

    x = x.replace(" ", "-") + "-do" #Create new searchable string with Doximity

    URL = "https://www.doximity.com/pub/" + x #Creates new URL

    #Bring in URL value
    r = requests.get(URL)

    #Put into beautiful soup format
    soup = BeautifulSoup(r.content, 'html5lib')

    sections = soup.findAll('section') #Pull all the sections of the individual's profile

    for sect in sections: #For each section, pull the text into the appropriate category
        dictionary[str(sect['class'][1])] = sect.get_text()

    additional_info_do = additional_info_do.append(dictionary, ignore_index = True) #Update database
    
    print("Dictionary had {} entries".format(len(dictionary)))
    time.sleep(5)

#%% Export additional Doximity Data

additional_info_do.to_csv('/Users/cpollack/Documents/Dartmouth/Research/Obesity Certification/Data/ABOM_Additional_DO191015.csv', index = None, header=True)

#%% Bring in final bout of Doximity data
names_leftover_do = pd.read_csv('NoDoximity_MDDO_191015.csv')

#%% Pull information from US News
names_leftover_do = names_leftover_do.set_index('Name')

#configuration parser initialization
config = configparser.ConfigParser()
config.read('../config.ini')
delay = 5 # waits for 5 seconds for the correct element to appeaar

#Open the webdriver
driver = webdriver.Chrome(executable_path = os.path.abspath("chromedriver.exe"))

all_leftovers = pd.DataFrame()

for name in names_leftover_do.index: #For each name that didn't have a value
    print("Now analyzing {}".format(name))
    #Go to US News and search person
    driver.get("https://health.usnews.com/doctors/search?distance=20&name={0}%20{1}&location={2}%2C%20{3}".format(name.split(sep = " ")[0], name.split(sep = " ")[1], names_leftover_do.loc[name, 'City'], names_leftover_do.loc[name, 'State.Province']))

    #Click on their link
    try:
        driver.find_element_by_css_selector("a[href*='{}']".format(name.replace(" ", "-").lower())).click()

    except NoSuchElementException:
        print("No user found!")
        continue

    #Click on their Doximity profile
    try:
        driver.find_element_by_css_selector("a[href*='doximity.com']").click()

    except NoSuchElementException:
        print("No Doximity account found")
        continue

    #Wait to pul URL
    dictionary = {'Name': name}

    time.sleep(1)
    URL = driver.current_url
    
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html5lib')

    sections = soup.findAll('section') #Pull all the sections of the individual's profile

    for sect in sections: #For each section, pull the text into the appropriate category
        dictionary[str(sect['class'][1])] = sect.get_text()

    all_leftovers = all_leftovers.append(dictionary, ignore_index = True) #Update database
    
    print("Dictionary had {} entries".format(len(dictionary)))

#%% If fails, pick back up here.

for name in names_leftover_do.index[377:]: #For each name that didn't have a value
    print("Now analyzing {}".format(name))
    #Go to US News and search person
    driver.get("https://health.usnews.com/doctors/search?distance=20&name={0}%20{1}&location={2}%2C%20{3}".format(name.split(sep = " ")[0], name.split(sep = " ")[1], names_leftover_do.loc[name, 'City'], names_leftover_do.loc[name, 'State.Province']))

    #Click on their link
    try:
        driver.find_element_by_css_selector("a[href*='{}']".format(name.replace(" ", "-").lower())).click()

    except NoSuchElementException:
        print("No user found!")
        continue

    #Click on their Doximity profile
    try:
        driver.find_element_by_css_selector("a[href*='doximity.com']").click()

    except NoSuchElementException:
        print("No Doximity account found")
        continue

    #Wait to pul URL
    dictionary = {'Name': name}

    time.sleep(1)
    URL = driver.current_url
    
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html5lib')

    sections = soup.findAll('section') #Pull all the sections of the individual's profile

    for sect in sections: #For each section, pull the text into the appropriate category
        dictionary[str(sect['class'][1])] = sect.get_text()

    all_leftovers = all_leftovers.append(dictionary, ignore_index = True) #Update database
    
    print("Dictionary had {} entries".format(len(dictionary)))

#%% Export Doximity via US News

all_leftovers.to_csv('/Users/cpollack/Documents/Dartmouth/Research/Obesity Certification/Data/ABOM_DoxViaUSNews_191015.csv', index = None, header=True)




