from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import time
from fake_useragent import UserAgent
from python_rucaptcha import ReCaptchaV2
from twocaptcha import TwoCaptcha
import requests


RUCAPTCHA_KEY = "555335d2596c15fde65cfe3e74b61877"

# options
options = webdriver.FirefoxOptions()

useragent = UserAgent()

# user-agent
options.set_preference("general.useragent.override", 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0')

driver = webdriver.Firefox(
    executable_path=os.path.abspath('geckodriver.exe')
)
actions = webdriver.ActionChains(driver)
try:
    URL = 'https://www.farpost.ru/verify?r=1&u=%2Fvladivostok%2Ftech%2Faudio_video%2Fearphones%2Fbesprovodnye-naushniki-airpods-2-kopija-besprovodnaja-zarjadka-77783725.html&f=1'
    driver.get(URL)
    driver.implicitly_wait(5)
    time.sleep(3)
    try:
        img = driver.find_element_by_xpath('//img[@src]')
        print('Капча! Решаем...')
        api_key = os.getenv('APIKEY_2CAPTCHA', RUCAPTCHA_KEY)
        solver = TwoCaptcha(api_key)
        p = requests.get(img.get_attribute('src'))
        with open("captchaimg.jpg", "wb") as f:
            f.write(p.content)
        result = solver.normal('captchaimg.jpg')
        inp = driver.find_element_by_xpath('//input[@type="text"]')
        inp.send_keys(result['code'] + Keys.ENTER)
        os.remove('captchaimg.jpg')
        print('Капча решена')
        driver.implicitly_wait(15)
    except Exception:
        pass
    time.sleep(11)
finally:
    driver.close()
    driver.quit()
