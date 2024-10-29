import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

options = Options()
# options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

login_url = "https://licey33ivanovo.eljur.ru/authorize"
good_url = "https://licey33ivanovo.eljur.ru/journal-app"
good_url2 = "https://licey33ivanovo.eljur.ru/journal-student-grades-action"


def is_valid(login, password):
    driver.get(login_url)
    login_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))
    )
    # login_input = driver.find_element(By.XPATH, "//input[@type=\"text\"]")
    password_input = driver.find_element(By.XPATH, "//input[@type=\"password\"]")
    login_input.send_keys(login)
    password_input.send_keys(password)
    btn = driver.find_element(By.XPATH, "//button[@type='submit']")
    btn.click()
    try:
        WebDriverWait(driver, 0.5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'notice__content'))
        )
        return False
    except TimeoutException:
        return True


def get_new_marks(user_id, login, password):
    driver.get(login_url)
    login_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))
    )
    password_input = driver.find_element(By.XPATH, "//input[@type=\"password\"]")
    login_input.send_keys(login)
    password_input.send_keys(password)
    btn = driver.find_element(By.XPATH, "//button[@type='submit']")
    btn.click()
    WebDriverWait(driver, 10).until(
        EC.url_contains(good_url)
    )
    btn = driver.find_elements(By.XPATH, "//a[@rel=\"nofollow\"]")[2]
    btn.click()
    WebDriverWait(driver, 10).until(
        EC.url_contains(good_url2)
    )
    return {}
