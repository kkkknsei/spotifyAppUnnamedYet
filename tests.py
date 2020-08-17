from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re

s = input("input: ")


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


if s.split("://")[1].split(".")[1] != "albumoftheyear":
    print("Wrong source")
    exit(1)
else:
    store_one = []
    option = Options()
    option.headless = True
    driver = webdriver.Chrome(options=option)

    driver.get(s)

    elements = driver.find_elements_by_xpath("//h2[@class='albumListTitle']")

    for element in elements:
        html_content = element.get_attribute("outerHTML")
        soup = BeautifulSoup(html_content, "html.parser")
        result = soup.find("a")
        store_one.append(result)

    driver.quit()

    for store in store_one:
        html_result = cleanhtml(str(store))
        print(html_result)
