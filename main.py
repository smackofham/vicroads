import sys
import time
import bs4
import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, ElementNotVisibleException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
from PyQt5 import QtWidgets, QtGui


# Change this variable to current date of the driving test.
# [Day, Month]
date_of_test = [29, 10]
# Controls the breaking of the main loop if no available dates are found.
brk = False
# Sleep time between selenium commands.
sleep_time = 10
# Learners permit number
permit_no = str(input('Please enter your learners permit number.'))
# Last name on permit
last_name = str(input('Please enter your last name.'))

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
driver = webdriver.Chrome(options=chrome_options)

# download the chrome driver from https://sites.google.com/a/chromium.org/chromedriver/downloads and put it in the
# current directory

checkbook_url = 'https://billing.vicroads.vic.gov.au/bookings/Manage/Details'
appointments_url = 'https://billing.vicroads.vic.gov.au/bookings/Manage/Appointments'
timeslots_url = 'https://billing.vicroads.vic.gov.au/bookings/Appointment/Timeslotselect'
office_sel_url = 'https://billing.vicroads.vic.gov.au/bookings/Appointment/OfficeSelect'
transfer_url = 'https://billing.vicroads.vic.gov.au/bookings/Transfer/TermsAndConditions'
invalid_sess_url = 'https://billing.vicroads.vic.gov.au/bookings/Home/InvalidSession'


def system_tray_notif(title, content):
    # Displays a Windows 10 notification with a title and message.
    app = QtWidgets.QApplication(sys.argv)
    systemtray_icon = QtWidgets.QSystemTrayIcon(QtGui.QIcon("python.png"), app)
    systemtray_icon.show()
    systemtray_icon.showMessage(title, content)


def input_permit_name():
    try:
        # Finds the element where I type my license no.
        permit_no_elem = WebDriverWait(driver, 15).until(
            ec.presence_of_element_located((By.ID, "ClientID")))
        # Clears the field before entering the permit number.
        permit_no_elem.clear()
        permit_no_elem.send_keys(permit_no)
    except TimeoutException:
        print("Timed out waiting for page to load")
    # Finds the element where I type my family name.
    last_name_elem = driver.find_element_by_id('FamilyNameOne')
    last_name_elem.clear()
    last_name_elem.send_keys(last_name)
    # Clicks the submit button.
    submit_button()


def transfer_page():
    # Try and except block tries to wait for the page to load the explicit element I want.
    # Clicks on the transfer test booking option.
    try:
        change_appointment_elem = WebDriverWait(driver, 15).until(
            ec.presence_of_element_located((By.ID, "ChangeSelection")))
        # print(type(change_appointment_elem))
        change_appointment_elem.click()
        submit_button()
    except TimeoutException:
        print("Timed out waiting for page to load")


def office_page():
    # For selecting the vicroads branch for the test.
    # Creates a Select object that allows me to manipulate dropdown menu.
    select_option = Select(driver.find_element_by_id('officeid'))
    # Value of 46 corresponds to Sunbury branch.
    select_option.select_by_value('46')
    try:
        change_appointment_elem = WebDriverWait(driver, 15).until(
            ec.presence_of_element_located((By.ID, "NextAvailableAppointment")))
        # print(type(change_appointment_elem))
        change_appointment_elem.click()
        # Not using the defined button function because of different id.
        submit_elem_page3 = driver.find_element_by_id('searchbtn')
        submit_elem_page3.click()
    except TimeoutException:
        print("Timed out waiting for page to load")


def timeslot_page(current_best_date):
    # Creates the BeautifulSoup object from the page html.
    timeslot_soup = bs4.BeautifulSoup(driver.page_source, "html.parser")
    # Selects the weekdays and the corresponding dates.
    days_dates = timeslot_soup.select('div.timeslotheader.hidden-md.hidden-lg.stickyday')
    dates = []
    for item in days_dates:
        # Finds the dates and makes them into a list of lists.
        # Each date is it's own list with the first element being the day and the second being the month.
        date = re.findall('[0-9][0-9]/[0-9][0-9]', item.getText())
        date.append(int(date[0][-2:]))
        date[0] = int(date[0][:2])
        dates.append(date)
    # Breaks main loop by default unless available dates are found.
    break_loop = True
    for date in dates:
        # Compares available dates to the current best date.
        if current_best_date[1] > date[1]:
            system_tray_notif('NEW DATE RESULT', 'NEW DATE FOUND: ' + str(date[0]) + '/' + str(date[1]))
            print('NEW DATE RESULT', 'NEW DATE FOUND: ' + str(date[0]) + '/' + str(date[1]))
            break_loop = False
        elif current_best_date[1] == date[1] and current_best_date[0] > date[0]:
            system_tray_notif('NEW DATE RESULT', 'NEW DATE FOUND: ' + str(date[0]) + '/' + str(date[1]))
            print('NEW DATE RESULT', 'NEW DATE FOUND: ' + str(date[0]) + '/' + str(date[1]))
            break_loop = False
    if break_loop:
        print('NO BETTER DATES AVAILABLE')
        global brk
        brk = True


def submit_button():
    # Presses the common submit button with id 'submitbtn'.
    try:
        try:
            submit_elem_page3 = WebDriverWait(driver, 15).until(
                ec.presence_of_element_located((By.ID, "submitbtn")))
            submit_elem_page3.click()
        except TimeoutException:
            print("Timed out waiting for page to load")
    except ElementNotVisibleException:
        submit_button()


while not brk:
    current_url = driver.current_url
    if current_url == 'data:,':
        driver.get(checkbook_url)
        # print(driver.current_url)
    elif current_url == invalid_sess_url:
        driver.get(checkbook_url)
    elif current_url == checkbook_url:
        input_permit_name()
        print('Typed out number/last name')
    elif current_url == appointments_url:
        transfer_page()
        print('Clicked transfer radio button and submit')
    elif current_url == transfer_url:
        submit_button()
    elif current_url == office_sel_url:
        office_page()
    elif current_url == timeslots_url:
        timeslot_page(date_of_test)
    time.sleep(sleep_time)

sys.exit()
