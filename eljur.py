import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import datetime
from pprint import pformat

options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

login_url = "https://licey33ivanovo.eljur.ru/authorize"
good_url = "https://licey33ivanovo.eljur.ru/journal-app"
good_url2 = "https://licey33ivanovo.eljur.ru/journal-student-grades-action"


def enter(login, password):
    driver.delete_all_cookies()
    driver.get(login_url)
    login_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type=\"text\"]"))
    )
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type=\"password\"]"))
    )
    login_input.send_keys(login)
    password_input.send_keys(password)
    btn = driver.find_element(By.XPATH, "//button[@type=\"submit\"]")
    btn.click()


def is_valid(login, password):
    enter(login, password)
    WebDriverWait(driver, 3).until_not(
        EC.presence_of_element_located((By.CLASS_NAME, 'page-loading'))
    )
    if driver.current_url == login_url:
        return False
    return True


def get_new_marks(user_id):
    WebDriverWait(driver, 10).until(
        EC.url_contains(good_url)
    )
    btn = driver.find_elements(By.XPATH, "//a[@rel=\"nofollow\"]")[2]
    btn.click()
    WebDriverWait(driver, 10).until(
        EC.url_contains(good_url2)
    )
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    subjects = []
    all_subjects = soup.find_all("div", class_="text-overflow")
    for subject in all_subjects:
        subjects.append(subject.text.replace('.', ''))
    marks = {i: [] for i in subjects}
    for subject in subjects:
        subject_mark_cells = soup.find_all(name="div", attrs={"class": "cell",
                                                              "name": subject,
                                                              "mark_date": True})
        for subject_mark_cell in subject_mark_cells:
            mark = subject_mark_cell.find_next("div").text
            if mark == '\xa0':
                break
            if mark == 'Н':
                continue
            date = subject_mark_cell['mark_date']
            date = datetime.datetime.strptime(date, "%Y-%m-%d")
            month = date.month
            day = date.day
            marks[subject].append([mark, [day, month]])
    with open("database/marks.json", "r", encoding="utf-8") as file:
        marks_file = json.load(file)
    res = {}
    if str(user_id) in marks_file:
        for subject in marks:
            for (mark, (day, month)) in marks[subject]:
                if [mark, [day, month]] not in marks_file[str(user_id)][subject]:
                    if subject not in res:
                        res[subject] = []
                    res[subject].append((mark, (day, month)))
    marks_file[str(user_id)] = marks
    marks_string = pformat(marks_file).replace("\'", "\"")
    with open("database/marks.json", "w", encoding="utf-8") as file:
        file.write(marks_string)
    return res


def get_subjects(user_id):
    with open("database/marks.json", "r", encoding="utf-8") as file:
        d = json.load(file)
    res = []
    for subject in d[str(user_id)]:
        res.append(subject)
    return res


def get_marks(user_id, subject):
    with open("database/marks.json", "r", encoding="utf-8") as file:
        d = json.load(file)
    str_marks = []
    int_marks = []
    for (mark, (day, month)) in d[str(user_id)][subject]:
        str_marks.append(mark)
        if mark.isdecimal():
            int_marks.append(int(mark))
        elif len(mark) == 2:
            int_marks.append(int(mark[:1]))
        else:
            for m in mark.split('/'):
                if m.isdecimal():
                    int_marks.append(int(m))
                elif len(m) == 2:
                    int_marks.append(int(m[:1]))
    return str_marks, int_marks