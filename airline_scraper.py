#!/usr/bin/env python
# coding: utf-8

import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time

from selenium import webdriver
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=options)


# login using selenium
driver.get('https://www.flightradar24.com')
element = driver.find_element_by_css_selector(".premium-menu-title.premium-menu-title-login")
element.click()
username = driver.find_element_by_id("fr24_SignInEmail")
username.send_keys("XXXXXX") # enter username

password = driver.find_element_by_id("fr24_SignInPassword")
password.send_keys("XXXXX") # enter password
time.sleep(4)

python_button = driver.find_elements_by_xpath("//button[@id='fr24_SignIn' and @class='btn btn-blue']")[0]
python_button.click()
time.sleep(3)

# a function to scrap all flights registration
# for example, https://www.flightradar24.com/data/airlines/ac-aca/fleet
# has information to each flight owned by Air Canada.
def company_flights(url, company_name):
    registration = []
    aircraft_type = []
    serial_num = []
    age = []
    company = []
    driver.get(url)
    page_content = BeautifulSoup(driver.page_source, 'html.parser')
    rows = page_content.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells)==4:
            registration.append(cells[0].text.strip())
            aircraft_type.append(cells[1].text.strip())
            serial_num.append(cells[2].text.strip())
            age.append(cells[3].text.strip().split()[0])
            company.append(company_name)
        else:
            registration.append(np.nan)
            aircraft_type.append(np.nan)
            serial_num.append(np.nan)
            age.append(np.nan)
            company.append(np.nan)
        time.sleep(3) 
    # Convert lists into a dataframe which will be used in the next function    
    df = pd.DataFrame({'registration': registration,
                      'aircraft_type': aircraft_type,
                      'serial_num': serial_num,
                      'age': age,
                      'company': company})
    #remove empty rows
    df = df.dropna()
    return df



# Take 21 Air for example. The company has 2 aircrafts
fleets = company_flights('https://www.flightradar24.com/data/airlines/2i-csb/fleet', '21 Air')


# A function that scraps a flight's travel history in 90 days.
def history_90_days(column):   
    Date = []
    From = []
    To = []
    flight_no = []
    duration = []
    STD = []
    ATD = []
    STA = []
    status = []
    registration = []
    iteration = 0
    # convert the column containing all registration codes into lowercase and a list for looping 
    registration_list = list(column.str.lower())
    for flight in registration_list:
        url = 'https://www.flightradar24.com/data/aircraft/' + flight +'#null'
        driver.get(url)
        # press the 'Find out more' button at the bottom of the page for earlier history
        load_buttons = driver.find_elements_by_xpath("//button[@id='btn-load-earlier-flights' and @class='loadButton loadEarlierFlights bottomMargin']")
        # keep loading the page until reaches the bottom
        while True:
            try:
                load_buttons[0].click()
                time.sleep(5)
            except Exception:
                break
                
        page_content = BeautifulSoup(driver.page_source, 'html.parser')
        rows = page_content.find_all('table')[0].find('tbody').find_all('tr')
        # when there's at least one record of flight history
        if len(rows) > 1:
            for row in rows:
                cells = row.find_all('td')
                Date.append(cells[2].text)
                From.append(cells[3].text)
                To.append(cells[4].text)
                flight_no.append(cells[5].text)
                duration.append(cells[6].text)
                STD.append(cells[7].text)
                ATD.append(cells[8].text)
                STA.append(cells[9].text)
                status.append(cells[11].text)
                registration.append(flight)
        else:
            Date.append(np.nan) 
            From.append(np.nan)
            To.append(np.nan)
            flight_no.append(np.nan)
            duration.append(np.nan)
            STD.append(np.nan)
            ATD.append(np.nan)
            STA.append(np.nan)
            status.append(np.nan)
            registration.append(flight)

        iteration += 1
        print('scrapped ' + str(iteration) + ' flight history.')
        time.sleep(5)
        
    df = pd.DataFrame({'registration': registration, 'flight_date': Date, 'from': From, 'destination': To,               'flight_No.':flight_no, 'duration': duration, 'STD': STD, 'ATD': ATD, 'STA': STA, 'status': status })
    return df           



flights = history_90_days(fleets['registration'])


# Export the data
flights.to_csv('flights.csv')

