from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
s = Service('drivers\chromedriver.exe')
driver = webdriver.Chrome(service = s, options = chrome_options)
driver.get("https://lichess.org/analysis")
pgn_box = driver.find_element(By.XPATH, "//textarea[@class='copyable']")
pgn_box.send_keys("1.e4 e5 2.Nc6")
pgn_box.send_keys(Keys.RETURN)