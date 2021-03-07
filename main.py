from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import openpyxl
from selenium.common import exceptions
import time
import os
from random import randint
import traceback
import xlrd
from xls2xlsx import XLS2XLSX
from twocaptcha import TwoCaptcha
import requests


def read_xls(file):
    rb = xlrd.open_workbook(os.path.abspath(file), formatting_info=True)
    sheet = rb.sheet_by_index(0)
    rows = list()
    for rownum in range(sheet.nrows):
        row = sheet.row_values(rownum)
        rows.append(row)
    return rows


if __name__ == '__main__':
    RUCAPTCHA_KEY = "555335d2596c15fde65cfe3e74b61877"
    # options
    options = webdriver.FirefoxOptions()

    # change useragent
    options.set_preference("general.useragent.override",
                           "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0")
    options.set_preference("dom.webdriver.enabled", False)
    # options.headless = True
    driver = webdriver.Firefox(
        executable_path=os.path.abspath('geckodriver.exe'),
        options=options
    )
    actions = webdriver.ActionChains(driver)

    rows = read_xls('Мониторинг цен конкурентов.xls')
    x2x = XLS2XLSX("Мониторинг цен конкурентов.xls")
    x2x.to_xlsx("Мониторинг цен конкурентов.xlsx")
    try:
        for i in range(len(rows)):
            url = rows[i][9]
            if type(url) == str and url[:23] == 'https://www.farpost.ru/':
                print('Проходим по ссылке...')
                driver.get(url)
                driver.implicitly_wait(5)
                try:
                    price = driver.find_element_by_xpath('//span[@data-field="price"]').text
                except Exception:
                    driver.get(driver.current_url + "&f=1")
                    driver.implicitly_wait(5)
                    print('Попалась проверка на робота! Решаем...')
                    img = driver.find_element_by_xpath('//img[@src]')
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
                    driver.implicitly_wait(5)
                    price = driver.find_element_by_xpath('//span[@data-field="price"]').text
                print('Считываем цену...')
                wb = openpyxl.load_workbook('Мониторинг цен конкурентов.xlsx')
                ws = wb.get_sheet_by_name('мониторинг цен')
                ws.cell(row=i+1, column=10).value = price[:-1]
                wb.save('Мониторинг цен конкурентов.xlsx')
        print('Парсинг завершён')
    except Exception as e:
        print('Ошибка:\n', traceback.format_exc())
    finally:
        driver.close()
        driver.quit()
        print(input('Press ENTER to close this program'))
