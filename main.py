import csv
import json
import os
import re
import sys
import time
import requests
import random
# import pickle

from proxy_auth_data import login, password
from tkinter import *
from tkinter.ttk import Combobox, Progressbar 
from datetime import datetime
# from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from seleniumwire import webdriver
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tqdm import tqdm
from multiprocessing import Pool

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"


def get_soup(mode, url, str):
    
    # ua = UserAgent()
    # user_agent = ua.random
    headers = { "User-Agent": f"{USER_AGENT}" }
    
    fileName = ""
    
    if mode == 1:
        fileName = str[len(str) - 3]
    if mode == 2:
        if len(str) == 4:
            fileName = str[2] 
        if len(str) == 5:
            fileName = str[3]
        if len(str) == 6:
            fileName = str[4]
        if len(str) == 7:
            fileName = str[5]
        if len(str) == 8:
            fileName = str[6]
        if len(str) == 9:
            fileName = str[7]
        if len(str) == 10:
            fileName = str[8]
    if mode == 3:
        fileName = str[len(str) - 1]
    
    if not fileName.endswith(".html"):
        fileName += ".html"
        
    r = requests.get(url=url, headers=headers, allow_redirects=False)
    
    if not os.path.exists("data"):
        os.mkdir("data")
    
    with open(f"data/{fileName}", "w", encoding="utf-8") as file:
        file.write(r.text)
    
    with open(f"data/{fileName}", encoding="utf-8") as file:
        src = file.read()    
    soup = BeautifulSoup(src, "lxml")
    
    return soup


def get_start_pages():
    
    url = "https://www.ss.lv/ru/"
    str = url.split("/")
    soup = get_soup(1, url, str)
    
    heading = soup.find_all("h2")
    i = 1
    all_categories_dict = {}
    
    for item in heading:
        item_href = item.find("a").get("href")
        item_text = item.find("a").get("title")
        all_categories_dict[i] = item_text, item_href
        
        with open("data/all_categories_dict.json", "w", encoding="utf-8") as file:
            # indent - отступ в файле
            # ensure_ascii=False - не экранирует символы и помогает при работе с кирилицей
            json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)
            
        i += 1

    
def check_sub_ctegory(soup:BeautifulSoup):
    
    subCat = soup.find_all("h4", class_="category")
    
    if len(subCat) > 0:
        return True
    else:
        return False
    

def set_driver_options(options:webdriver.ChromeOptions):
    
    # options.add_argument(f'--user-agent={USER_AGENT}')
    ua = UserAgent()
    user_agent = ua.chrome
    # print(user_agent)
    options.add_argument(f'--user-agent={user_agent}')
    
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument("--disable-proxy-certificate-handler")
    
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    options.add_argument("user-data-dir=C:\\WebDriver\\chromedriver\\user")
    options.add_argument("start-maximized")
    options.add_argument('--headless')


    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    # options.add_argument('--remote-debugging-port=8989')
    options.add_argument('--enable-javascript')
    # options.add_argument("--user-agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:72.0) Gecko/20100101 Firefox/72.0'")
    options.add_argument('--no-sandbox')
    # options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-insecure-localhost')
            
    # options.add_argument('--no-sandbox')
    # options.add_argument("--disable-extensions")
    # options.add_argument("--headless")
    # options.add_argument(f"--proxy-server={auth}")
        
    # options.debugger_address = 'localhost:8989'
    
    # options.add_argument("--proxy-server=212.102.151.99:8000")
    

def get_selenium_driver():
    
    options = webdriver.ChromeOptions()
    set_driver_options(options)
    
    caps = DesiredCapabilities().CHROME
    # caps['pageLoadStrategy'] = 'eager'
    caps['pageLoadStrategy'] = 'normal'
    
    proxy_options = {
        "proxy" : {
            "https" : f"http://{login}:{password}@185.122.206.63:4515"
        }
    }
    service = Service(desired_capabilities=caps, executable_path=r"C:\WebDriver\chromedriver\chromedriver.exe")
    # driver = webdriver.Chrome(service=service, options=options)
    driver = webdriver.Chrome(service=service, options=options, seleniumwire_options=proxy_options)
    # driver.get("https://2ip.ru/")
    return driver


def extract_phone_numbers(driver:webdriver.Chrome):
    phoneNumbers = ""
    phone1 = ""
    phone2 = ""
    try:
        phone1 = driver.find_element(By.XPATH, "//span[contains(@id, 'phone_td_1')]").text
        phone2 = driver.find_element(By.XPATH, "//span[contains(@id, 'phone_td_2')]").text
    except NoSuchElementException:
        print(NoSuchElementException)
        print("Не удалось получить телефоны")
    phoneNumbers = f"{phone1};{phone2};"
    return phoneNumbers


def get_phone(url):
    phoneNumbers = ""
    try:
        driver = get_selenium_driver()        
        driver.get(url)
        
        driver.maximize_window
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.randrange(1, 3))
                
        try:
            showPhone = driver.find_element(By.XPATH, "//a[contains(@onclick, '_show_phone')]")
            if showPhone.is_displayed():
                # showPhone.click()
                driver.execute_script("arguments[0].click();", showPhone)
                time.sleep(random.randrange(3, 10))
            else:
                print("The element showPhone is not visible.")
        except NoSuchElementException:
            print(NoSuchElementException)
            print("Кнопка показать телефон не найдена")
        
        try:
            recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
            recaptcha_iframe.find_element(By.XPATH, '//textarea[@id="g-recaptcha-response"]')
            recaptcha_iframe.click()
            time.sleep(random.randrange(5, 10))
        except NoSuchElementException:
            print(NoSuchElementException)
            print("Капча не найдена")
                 
        phoneNumbers = extract_phone_numbers(driver)[:-1]
        # if len(phoneNumbers) > 0:
        #     phoneNumbers = phoneNumbers[:-1]
        
        # pickle.dump(driver.get_cookies, open("cokies", "wb"))
        # driver.close()
        # driver.quit()
    
        return phoneNumbers
    except NoSuchElementException:
        print(NoSuchElementException)     
        return phoneNumbers


def fill_data(link, nameCsv, selection):
    
    phone = ""
    email = ""
    # site = ""
    location = ""
    category = ""
    sub_category_1 = ""
    sub_category_2 = ""
    sub_category_3 = ""
    sub_category_4 = ""
    sub_category_5 = ""
    
    url = f"https://www.ss.lv{link}"
    str = link.split("/")
    soup = get_soup(3, url, str)
        
    sels = selection.split("-")
    category = sels[1]
    
    links = soup.select('h2.headtitle a')
    arr_links = []
    for link in links:
        arr_links.append(link.text)
    
    for i in range(0, len(arr_links)):
        if i == 0:
            sub_category_1 = arr_links[0]
        if i == 1:
            sub_category_2 = arr_links[1]
        if i == 2:
            sub_category_3 = arr_links[2]
        if i == 3:
            sub_category_4 = arr_links[3]
        if i == 4:
            sub_category_5 = arr_links[4]
    
    table = soup.find("div", id="tr_cont")
    td_locate = soup.find('td', class_='ads_contacts_name', string=re.compile(r'место', re.IGNORECASE))
    if td_locate:
        next_td_locate = td_locate.find_next('td', class_='ads_contacts')
        if next_td_locate:
            text = next_td_locate.get_text()
            location = text
    
    phone = get_phone(url)
    
    with open(f"result/{nameCsv}.csv", "a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                phone.replace(",", ";").strip(),
                email.replace(",", ";").strip(),
                # site.replace(",", ";").strip(),
                location.replace(",", ";").strip(),
                category.replace(",", ";").strip(),
                sub_category_1.replace(",", ";").strip(),
                sub_category_2.replace(",", ";").strip(),
                sub_category_3.replace(",", ";").strip(),
                sub_category_4.replace(",", ";").strip(),
                sub_category_5.replace(",", ";").strip()
            )
        )
    

def get_list_links(soup:BeautifulSoup, nameCsv, selection):
    
    div_d1_tags = soup.find_all('div', {'class': 'd1'})
    
    for div_tag in div_d1_tags:
        links = div_tag.find_all('a')
        
        for link in links:
            fill_data(link['href'], nameCsv, selection)


def scrap_data(soup:BeautifulSoup, nameCsv, selection, url, progress_callback):
    
    count = 1
    pages = soup.find("a", class_="navi")
    
    if pages is not None:
        pages_count = pages.get("href")
        pattern = r'page(\d+)\.html'
        match = re.search(pattern, pages_count)
        
        if match:
            count = int(match.group(1))
            i = 1
            
            while i < count + 1:
                lin = f"{url}page{i}.html"
                
                str = lin.split("/")
                soup = get_soup(3, url, str)
                
                div_d1_tags = soup.find_all('div', {'class': 'd1'})
                for div_tag in div_d1_tags:
                    links = div_tag.find_all('a')
                    for link in links:
                        fill_data(link['href'], nameCsv, selection)
                i += 1
                
    else:
        div_d1_tags = soup.find_all('div', {'class': 'd1'})
        for div_tag in div_d1_tags:
            links = div_tag.find_all('a')
            for link in links:
                fill_data(link['href'], nameCsv, selection)


def get_data(href:str, nameCsv, selection, progress_callback):
    
    url = f"https://www.ss.lv{href}"
    str = href.split("/")
    soup = get_soup(2, url, str)
      
    if check_sub_ctegory(soup):
        subCats = soup.find_all("h4", class_="category")
        total_subcategories = len(subCats)
        
        for idx, item in tqdm(enumerate(subCats), total=total_subcategories, desc="Processing subcategories", unit="subcategory"):
            item_href = item.find("a").get("href")
            item_text = item.find("a").get("title")
            if str[1] == "ru": 
                get_data(item_href, nameCsv, selection, progress_callback)
            progress_callback((idx + 1) / total_subcategories)
    else:
        scrap_data(soup, nameCsv, selection, url, progress_callback)

    
def get_category():
    
    with open("data/all_categories_dict.json", encoding="utf-8") as file:
        all_categories = json.load(file)
        
    category = list()
    
    for key, value in all_categories.items():
        category_name = value[0]
        category.append(f"{key} - {category_name}")
        
    return category

    
def href(selection:str):
    
    with open("data/all_categories_dict.json", encoding="utf-8") as file:
        all_categories = json.load(file)
        
    category = list()
    
    for key, value in all_categories.items():
        category_name = value[0]
        category_link = value[1]
        val = f"{key} - {category_name}"
        
        if val == selection:
            return category_link

    
def window():
    
    def clicked():
        
        selection = combobox.get()
        link = href(selection)
        s = link.split("/")
        category_name = s[2]
        
        if not os.path.exists("result"):
            os.mkdir("result")
       
        curDate = datetime.now()
        curDateStr = curDate.strftime("%Y-%m-%d")
        nameCsv = f"{category_name}_{curDateStr}"
        
        with open(f"result/{nameCsv}.csv", "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    "phone",
                    "email",
                    # "site",
                    "location",
                    "category",
                    "sub_category_1",
                    "sub_category_2",
                    "sub_category_3",
                    "sub_category_4",
                    "sub_category_5"
                )
            )
        
        get_data(link, nameCsv, selection, update_progress)
        
        print("FINISH!!!")
        
    def selected(event):
        
        selection = combobox.get()
        lblSelect["text"] = f"Вы выбрали: {selection}"
        
    window = Tk()
    window.geometry('400x250')
    window.title("Парсер сайта объявлений ss.lv")
    
    lbl = Label(window, text="Выберите категорию для парсинга", font=("Arial Bold", 15))
    lbl.grid(column=0, row=0)
    
    category = get_category()
    
    combobox = Combobox(window, values=category, state="readonly", width=30)
    combobox.bind("<<ComboboxSelected>>", selected)
    combobox.current(0)
    combobox.grid(column=0, row=10) 
    
    lblSelect = Label(window, text="", font=("Arial Bold", 15))
    lblSelect.grid(column=0, row=20)  
    
    btn = Button(window, text="Запустить", command=clicked)  
    btn.grid(column=0, row=30)  
    
    bar = Progressbar(window, length=200, mode='determinate')
    bar.grid(column=0, row=40)
    
    def update_progress(progress): 
        bar['value'] = progress * 100
    
    window.mainloop()


def main():
    
    print("start")
    
    get_start_pages()
    window()
    
    print("end")

    
if __name__ == '__main__':
    main()
    
