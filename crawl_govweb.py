from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import json
from bs4 import BeautifulSoup
import random

#Translate Chinese into ASCII 
def translate(text):
    whole_list = []
    for char in text:
        if (char < 'A' or char > 'Z') and (char < 'a' or char > 'z') and (char < '0' or char > '9'):
            hex_code = char.encode('utf-8')
            for byte in hex_code:
                temp_code = hex(byte)[2:].upper()
                whole_code = '%25'+temp_code
                whole_list.append(whole_code)
        else:
            whole_list.append(char)
    return 'https://mkt.zycg.gov.cn/mall-view/product/search?keyword=' + ''.join(whole_list)

#Find all products' urls
def collect_urls(driver, url):
    # Open the main website
    driver.get(url)
    time.sleep(10)

    all_urls = []

    try:
        epoch = int(driver.find_element(By.CLASS_NAME, 'layui-laypage-last').text)
    except:
        epoch = 1

    for times in range(epoch):
        product_urls = driver.find_elements(By.XPATH, '//div/div[2]/div[2]/a')
        for i in product_urls:
            all_urls.append(i.get_attribute('href'))
        driver.find_element(By.CLASS_NAME, 'layui-laypage-next').click()
        time.sleep(10)
    return list(set(all_urls))

#Crawl every single product's information
def crawl_info(driver, url, product_info):
    #Open the product's introduction website
    driver.get(url)
    time.sleep(5)

    driver.find_element(By.XPATH, '/html/body/div[9]/div/div[2]/ul/li[3]').click()
    time.sleep(5)

    temp_dict = {}
    product_name = driver.find_element(By.CLASS_NAME, 'name').text
    product_owner = driver.find_element(By.CLASS_NAME, 'gc-attr-content-top').text
    product_price = driver.find_element(By.CLASS_NAME, 'gc-goods-price-rate').text

    temp_list = re.split("\n", driver.find_element(By.ID, 'weight').text)
    product_description = {}
    for i in temp_list:
        if i[0] == '重':
            temp = i.split("）", 1)
            product_description[temp[0] + '）'] = temp[1]
        else:
            temp = i.split(" ", 1)
            product_description[temp[0]] = temp[1]

    temp_dict['url'] = url
    temp_dict['price'] = product_price
    temp_dict['owner'] = product_owner
    temp_dict['description'] = product_description
    product_info[product_name] = temp_dict

def crawl(url):
    #Create a Chrome instance
    driver = webdriver.Chrome()

    #Collect all proudcts' specific urls
    all_urls = collect_urls(driver, url)

    #Crawl information on the single product's website
    product_info = {}
    for product_url in all_urls:
        crawl_info(driver, product_url, product_info)

    driver.close()
    print(product_info)
    return product_info


if __name__ == '__main__':
    product_url = translate("天融信Web应用安全防护系统")
    product_info = crawl(product_url)

    file = "example.json"
    
    # open the file
    with open(file, "w", encoding='utf-8') as f:
        json.dump(product_info, f, ensure_ascii=False, indent=4)
