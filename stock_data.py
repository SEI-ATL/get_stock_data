###### Imports #######
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import re, requests, io, time, random, string, pprint
from datetime import date
from pymongo import MongoClient
from credentials import email, password
from list_of_stocks import stock_list

# pprint
pp = pprint.PrettyPrinter(indent=4)

# MongoDB
client = MongoClient()
db = client['stock_data']
collection = db["current_data"]

# Chrome Webdriver
driver = webdriver.Chrome('/Users/romebell/downloads/chromedriver-2')
time.sleep(3)

def sign_in(email=email, password=password):
    driver.get('https://wallmine.com')
    time.sleep(2)
    driver.find_element_by_xpath('/html/body/main/header/div/ul/li[1]/ul/li[3]/a').click() # click sign in button
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="new_user"]/div[5]/div[1]/div[2]/a').click() # click on sign in w/ password
    if "We're glad you're back!" in driver.page_source:
        print('On sign in page')
        # sign into website
        driver.find_element_by_xpath('//*[@id="user_email"]').send_keys(email)
        driver.find_element_by_xpath('//*[@id="user_password"]').send_keys(password)
        time.sleep(0.1)
        driver.find_element_by_xpath('//*[@id="new_user"]/div[5]/div[2]/div[1]/button').click()
        time.sleep(3)
    if 'Stock market overview' in driver.page_source:
        print('Sign-In Successful')
    else: 
        print('start over app')

def get_data(stock_list): # needs to be an array of objects, objects need stock_ticker and exchange as keys
    for i in range(len(stock_list)):
        each_stock = stock_list[i]
        print(f"{i}: {each_stock.get('stock_ticker')}, exchange: {each_stock.get('exchange')}")
        driver.get(f"https://wallmine.com/{each_stock.get('exchange')}/{each_stock.get('stock_ticker')}")
        time.sleep(3)
        # company_name
        company_name = driver.find_element_by_xpath('/html/body/main/section/div[2]/div/div[1]/h1/div[2]/a').text
        # current_price
        current_price = driver.find_element_by_xpath('/html/body/main/section/div[3]/div/div/div/div/div[2]/div/div[1]/span[1]').text
    # percentage
        percentage = driver.find_element_by_xpath('/html/body/main/section/div[3]/div/div/div/div/div[2]/div/div[2]/div').text
        price_movement = True
        if driver.find_elements_by_class_name('badge.badge-success'):
            price_up = driver.find_elements_by_class_name('badge.badge-success')[0].text
            if price_up == percentage:
                print('price up')
        elif driver.find_elements_by_class_name('badge.badge-danger'):
            price_down = driver.find_elements_by_class_name('badge.badge-danger')[0].text
            if price_down == percentage:
                price_movement = False
            print('price down')

        # amount changed
        amount_changed = float(driver.find_element_by_xpath('/html/body/main/section/div[3]/div/div/div/div/div[2]/div/div[1]/span[2]').text[1:])

        # market_cap
        try:
            if driver.find_element_by_xpath('/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[1]/table/tbody/tr[1]/td/span'):
                check_market_cap = driver.find_element_by_xpath('/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[1]/table/tbody/tr[1]/td/span').text
                if check_market_cap[-1] == 'T':
                    market_cap = float(check_market_cap[1:-1]) * 1000000000000
                elif check_market_cap[-1] == 'B':
                    print('true?') # come back to later
                    market_cap = float(check_market_cap[1:-1]) * 1000000000
                elif check_market_cap == 'M':
                    market_cap = float(check_market_cap[1:-1]) * 1000000
        except:
            market_cap = 'N/A'

        # enterprise_value
        try:
            if driver.find_element_by_xpath('/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[1]/table/tbody/tr[2]/td/span'): 
                check_enterprise_value = driver.find_element_by_xpath('/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[1]/table/tbody/tr[2]/td/span').text

                if check_enterprise_value[-1] == 'T':
                    enterprise_value = float(check_enterprise_value[1:-1]) * 1000000000000
                elif check_enterprise_value[-1] == 'B':
                    enterprise_value = float(check_enterprise_value[1:-1]) * 1000000000
                elif check_enterprise_value[-1] == 'M':
                    enterprise_value = float(check_enterprise_value[1:-1]) * 1000000
        except:
            enterprise_value = 'N/A'

        # ebitda
        try:
            if driver.find_element_by_xpath('/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[2]/table/tbody/tr[2]/td/span'):
            check_ebitda = driver.find_element_by_xpath('/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[2]/table/tbody/tr[2]/td/span').text
            if check_ebitda[-1] == 'T':
                ebitda = float(check_ebitda[1:-1]) * 1000000000000
            elif check_ebitda[-1] == 'B':
                ebitda = float(check_ebitda[1:-1]) * 1000000000
            elif check_ebitda == 'M':
                ebitda = float(check_enterprise_value[1:-1]) * 1000000
        except:
            ebitda = 'N/A'

        # income
        try:
            if driver.find_element_by_xpath('/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[2]/table/tbody/tr[3]/td/span'):
                check_income = driver.find_element_by_xpath('/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[2]/table/tbody/tr[3]/td/span').text
                if check_income[-1] == 'T':
                    income = float(check_income[1:-1]) * 1000000000000
                elif check_income[-1] == 'B':
                    income = float(check_income[1:-1]) * 1000000000
                elif check_income[-1] == 'M':
                    income = float(check_income[1:-1]) * 1000000
        except:
            income = 'N/A'
        # volume
        check_volume = driver.find_element_by_xpath('/html/body/main/section/div[4]/div[1]/div[2]/div[2]/div[1]/table/tbody/tr[1]/td').text.split(' / ')
        volume_purchased = check_volume[0]
        volume_outstanding = check_volume[1]

        # stock object
        stock_object = {
            'company_name': company_name,
            'stock_ticker': each_stock.get('stock_ticker'),
            'exchange': each_stock.get('exchange'),
            'current_price': current_price,
            'percentage': percentage,
            'price_movement': price_movement,
            'amount_changed': amount_changed,
            'market_cap': market_cap,
            'enterprise_value': enterprise_value,
            'volume_purchased': volume_purchased,
            'volume_outstanding': volume_outstanding,
            'date': str(date.today())
        }
        
        # Insert stock object into database
        db.current_data.insert_one(stock_object)
        retrieve_stock = db.current_data.find_one({"stock_ticker": each_stock.get('stock_ticker')})
        pp.pprint(retrieve_stock)

# run both functions
sign_in(email, password)
time.sleep(1)
get_data(stock_list)