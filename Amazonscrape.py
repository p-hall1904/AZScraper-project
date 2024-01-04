import os
import json
import selenium 
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from amazoncaptcha import AmazonCaptcha
from time import sleep

path = "C://chromedriver.exe"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)

# Open captcha broswer
driver.get('https://www.amazon.com/errors/validateCaptcha')

# Deal with captcha
link = driver.find_element(By.XPATH, "//div[@class = 'a-row a-text-center']//img").get_attribute('src')
captcha = AmazonCaptcha.fromlink(link)
captcha_value = AmazonCaptcha.solve(captcha)
input_field = driver.find_element(By.ID,"captchacharacters").send_keys(captcha_value)
button = driver.find_element(By.CLASS_NAME, "a-button-text")
button.click()

#Open amazon now
driver.get('https://www.amazon.com')

# Assign variables to search bar and search button
input_search=driver.find_element(By.ID, 'twotabsearchtextbox')
search_button = driver.find_element(By.XPATH, "(//input[@type='submit'])[1]")

# Searches for items
input_search.send_keys("PCs on sale")
sleep(1)
search_button.click()

#Scrapes the pages
products = []
for i in range(10):
    print('Scraping', i+1)
    product_elements = driver.find_elements(By.XPATH, "//span[@class='a-size-medium a-color-base a-text-normal']")
    
    for p in product_elements:
        product_name = p.text
        product_link = p.find_element(By.XPATH, ".//ancestor::a[@class='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal']").get_attribute('href')
        product = {'Name': product_name, 'Link': product_link}
        products.append(product)
    
    try:
        next_button = driver.find_element(By.XPATH, "//a[text()='Next']")
        next_button.click()
        sleep(3)
    except:
        print("No more pages")
        break

#Saves data to JSON file 
output_file = 'scraped_data.json'
with open(output_file, 'w', encoding='utf-8') as json_file:
    json.dump(products, json_file, ensure_ascii=False, indent=4)

#Opens JSON file
print(f'opening {output_file}')
os.startfile(output_file)
