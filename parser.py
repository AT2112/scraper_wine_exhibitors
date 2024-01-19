from selenium import webdriver
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import requests
import csv

URL = "https://wineparis-vinexpo.com/newfront/marketplace/exhibitors?limit=60"

wine_paris_links = []


driver = webdriver.Chrome()
driver.get(URL)

WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/div[1]/main/div/div/div[3]/div/div[2]/div[1]/div[2]/div[1]/div/div[1]/div')))

last_page = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[1]/main/div/div/div[3]/div/div[2]/div[4]/nav/ul/li[8]/button')
next_button = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[1]/main/div/div/div[3]/div/div[2]/div[4]/nav/ul/li[9]/button')
exhibitors_h2 = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[1]/main/div/div/div[3]/div/div[2]/div[2]/h2')

page_count = 1

print(last_page.text)

while page_count <= int(last_page.text):

    first_exhibitor = None

    while not first_exhibitor:
        ActionChains(driver) \
            .scroll_to_element(exhibitors_h2) \
            .perform()
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH,
                                                 '//*[@id="__next"]/div[2]/div[1]/main/div/div/div[3]/div/div[2]/div[3]/div[1]/div/div[1]/a/div/div')))
        first_exhibitor = driver.find_element(By.XPATH,
                                              '//*[@id="__next"]/div[2]/div[1]/main/div/div/div[3]/div/div[2]/div[3]/div[1]/div/div[1]/a/div/div')

    i = 0
    while i < 31:
        delta_y = 200
        ActionChains(driver) \
            .scroll_by_amount(0, delta_y) \
            .perform()
        time.sleep(0.3)
        i+=1

    WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/div[2]/div[1]/main/div/div/div[3]/div/div[2]/div[3]/div/div/div/a')))

    find_exhibitors = driver.find_elements(By.XPATH, './/*[@id="__next"]/div[2]/div[1]/main/div/div/div[3]/div/div[2]/div[3]/div/div/div/a')

    href_values = [exhibitor.get_attribute("href") for exhibitor in find_exhibitors]

    for link in href_values:
            print(link)
            wine_paris_links.append(link)

    print(f'length of wine_paris: {len(wine_paris_links)}')

    print(f"length of current page: {len(href_values)}")

    ActionChains(driver) \
        .scroll_by_amount(0, -250) \
        .perform()

    ActionChains(driver) \
        .scroll_to_element(next_button) \
        .perform()

    ActionChains(driver).click(next_button).perform()

    page_count += 1

dict_res = {}
for url in wine_paris_links:

    response = requests.get(url)

    content_str = response.content.decode('utf-8')

    start_index = content_str.find('"exhibitor":{"id":')
    end_index = content_str.find('}', start_index) + 1

    exhibitor_info_str = content_str[start_index:end_index]

    name_start_index = exhibitor_info_str.find('"name":"') + len('"name":"')
    name_end_index = exhibitor_info_str.find('"', name_start_index)
    name = exhibitor_info_str[name_start_index:name_end_index]

    website_start_index = exhibitor_info_str.find('"website":"') + len('"website":"')
    website_end_index = exhibitor_info_str.find('"', website_start_index)
    website = exhibitor_info_str[website_start_index:website_end_index]

    print(f'{name}: {website}')

    dict_res[name] = website

csv_file_path = 'result.csv'

with open(csv_file_path, 'w', newline='') as csvfile:
    fieldnames = ['Company Name', 'Website']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    for company_name, website in dict_res.items():
        writer.writerow({'Company Name': company_name, 'Website': website})


