from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from amazoncaptcha import AmazonCaptcha
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

def scrape_and_save(user_search):
    products = []

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--headless')

    with webdriver.Chrome(options=options) as driver:
        # Open captcha browser
        driver.get('https://www.amazon.com/errors/validateCaptcha')

        # Deal with captcha
        link = driver.find_element(By.XPATH, "//div[@class='a-row a-text-center']//img").get_attribute('src')
        captcha = AmazonCaptcha.fromlink(link)
        captcha_value = AmazonCaptcha.solve(captcha)
        input_field = driver.find_element(By.ID, "captchacharacters").send_keys(captcha_value)
        button = driver.find_element(By.CLASS_NAME, "a-button-text")
        button.click()

        # Open amazon now
        driver.get('https://www.amazon.com')

        # Assign variables to the search bar and search button
        input_search = driver.find_element(By.ID, 'twotabsearchtextbox')
        search_button = driver.find_element(By.XPATH, "(//input[@type='submit'])[1]")

        # Searches for items
        if user_search:
            input_search.send_keys(user_search)
            sleep(1)
            search_button.click()

        # Scrapes the pages
        for i in range(5):
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

    return products

@app.route('/', methods=['GET', 'POST'])
def index():
    products = []
    user_search = request.form.get('user_search', '')
    if request.method == 'POST' and user_search:
        products = scrape_and_save(user_search)
    return render_template('index.html', products=products, user_search=user_search)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
