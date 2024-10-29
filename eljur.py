import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

driver = webdriver.Chrome()
login_url = "https://licey33ivanovo.eljur.ru/authorize"
good_url = "https://licey33ivanovo.eljur.ru/journal-app"


def is_valid(login, password):
    driver.get(login_url)
    time.sleep(5)
    # login_input = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.XPATH, "input[type='text']"))
    # )
    login_input = driver.find_element(By.XPATH, "input[type=\"text\"]")
    password_input = driver.find_element(By.XPATH, "input[type=\"password\"]")
    login_input.send_keys(login)
    password_input.send_keys(password)
    btn = driver.find_element(By.XPATH, "button[type='submit']")
    btn.click()
    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'notice__content'))
        )
        return False
    except TimeoutException:
        return True


def get_new_marks(user_id, login, password):
    return {"Алгебра": [(5, (2, 10)), (2, (2, 10))], "Химия": [(5, (1, 1))]}
