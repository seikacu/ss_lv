import csv
import json
import os
import re
import time

from tkinter import *
from tkinter.ttk import Combobox, Progressbar 
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm


def get_start_pages():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    url = "https://www.ss.lv/ru/"
    
    r = requests.get(url=url, headers=headers)
    
    if not os.path.exists("data"):
        os.mkdir("data")
    
    with open("data/index.html", "w", encoding="utf-8") as file:
        file.write(r.text)
    
    with open("data/index.html", encoding="utf-8") as file:
        src = file.read()    
    soup = BeautifulSoup(src, "lxml")
    heading = soup.find_all("h2")
    i = 1
    all_categories_dict = {}
    for item in heading:
        # print(i)
        item_href = item.find("a").get("href")
        item_text = item.find("a").get("title")
        all_categories_dict[i] = item_text, item_href
        with open("data/all_categories_dict.json", "w", encoding="utf-8") as file:
            # indent - отступ в файле
            # ensure_ascii=False - не экранирует символы и помогает при работе с кирилицей
            json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)
        i += 1

    
def check_sub_ctegory(soup:BeautifulSoup):
    subCat = soup.finds_all("h4", class_="category")
    if len(subCat) > 0:
        return True;
    else:
        return False
    

def set_driver_options(options:webdriver.ChromeOptions):
    # user-agent
    userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    options.add_argument(f'--user-agent={userAgent}')
        
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")
    # options.add_argument(f"--proxy-server={auth}")
        
    # options.debugger_address = 'localhost:8989'


def get_phone(url):
    try:
        options = webdriver.ChromeOptions()

        set_driver_options(options)
        
        caps = DesiredCapabilities().CHROME
        # caps['pageLoadStrategy'] = 'eager'
        caps['pageLoadStrategy'] = 'normal'
        
        service = Service(desired_capabilities=caps, executable_path=r"C:\WebDriver\chromedriver\chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get(url)
        
        driver.maximize_window
        time.sleep(1)
        showPhone = driver.find_element(By.XPATH, "//a[contains(@onclick, '_show_phone')]")
        showPhone.click()
        time.sleep(1)
        recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
        recaptcha_iframe.find_element(By.XPATH, '//textarea[@id="g-recaptcha-response"]')
        recaptcha_iframe.click()
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        
        r = requests.get(url=url, headers=headers)
        
        strs = link.split("/")
        
        with open(f"data/{strs[len(strs)-1]}", "w", encoding="utf-8") as file:
            file.write(r.text)
        
        with open(f"data/{strs[len(strs)-1]}", encoding="utf-8") as file:
            src = file.read()    
    
        soup = BeautifulSoup(src, "lxml")
        phone = ""
        phone_td_1 = table.find("span", id="phone_td_1")
        if phone_td_1:
            phone = phone_td_1.text
            pass
        
        driver.quit()
    
        return phone
    except NoSuchElementException:
        print(NoSuchElementException)     
        return ""      


def fill_data(link, nameCsv, selection):
    
    phone = ""
    email = ""
    site = ""
    location = ""
    category = ""
    sub_category_1 = ""
    sub_category_2 = ""
    sub_category_3 = ""
    sub_category_4 = ""
    sub_category_5 = ""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    url = f"https://www.ss.lv{link}"
    r = requests.get(url=url, headers=headers)
    
    strs = link.split("/")
    
    with open(f"data/{strs[len(strs)-1]}", "w", encoding="utf-8") as file:
        file.write(r.text)
    
    with open(f"data/{strs[len(strs)-1]}", encoding="utf-8") as file:
        src = file.read()    

    soup = BeautifulSoup(src, "lxml")
    
    sels = selection.split("-")
    category = sels[1].replace(" ", "")
    
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
            text = next_td_locate.get_text().strip()
            location = text
    
    # phone_td_1 = table.find("span", id="phone_td_1")
    # if phone_td_1:
    #     # phone = phone_td_1.text
    #     pass
    
    phone = get_phone(url)
    
    with open(f"result/{nameCsv}.csv", "a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                phone,
                email,
                site,
                location,
                category,
                sub_category_1,
                sub_category_2,
                sub_category_3,
                sub_category_4,
                sub_category_5
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
    # print(f"\nPAGES - {pages}")
    if pages is not None:
        pages_count = pages.get("href")
        pattern = r'page(\d+)\.html'
        match = re.search(pattern, pages_count)
        # print(pages)
        if match:
            count = int(match.group(1))
            # print(count)
            i = 1
            while i < count + 1:
                # перебирать страницы
                # print(f"{url}")
                lin = f"{url}page{i}.html"
                print(f"{lin}")
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                }
                
                r = requests.get(url=lin, headers=headers)
                
                strs = lin.split("/")
                
                with open(f"data/{strs[9]}", "w", encoding="utf-8") as file:
                    file.write(r.text)
                
                with open(f"data/{strs[9]}", encoding="utf-8") as file:
                    src = file.read()    
            
                soup = BeautifulSoup(src, "lxml")
                
                div_d1_tags = soup.find_all('div', {'class': 'd1'})
                for div_tag in div_d1_tags:
                    links = div_tag.find_all('a')
                    for link in links:
                        fill_data(link['href'], nameCsv, selection)
                i += 1            
        else:
            print("No number found in the string.")
    else:
        print("Страница всего одна.")
        div_d1_tags = soup.find_all('div', {'class': 'd1'})
        for div_tag in div_d1_tags:
            links = div_tag.find_all('a')
            for link in links:
                fill_data(link['href'], nameCsv, selection)
          
        # Simulate some work
    # for i in tqdm(range(100), desc="Scraping data", unit="item"):
    #     # Your actual scraping logic here...
    #     # ...
    #
    #     # Update progress
    #     progress_callback((i + 1) / 100)


def get_data(href:str, nameCsv, selection, progress_callback):
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    url = f"https://www.ss.lv{href}"
    r = requests.get(url=url, headers=headers, allow_redirects=False)
     
    s = href.split("/")
    l = len(s)
    # print(s)
    if len(s) == 4:
        nameFile = s[2] 
    if len(s) == 5:
        nameFile = s[3]
    if len(s) == 6:
        nameFile = s[4]
    if len(s) == 7:
        nameFile = s[5]
    if len(s) == 8:
        nameFile = s[6]
    if len(s) == 9:
        nameFile = s[7]
    if len(s) == 10:
        nameFile = s[8]
    
    with open(f"data/{nameFile}.html", "w", encoding="utf-8") as file:
        file.write(r.text)
    
    with open(f"data/{nameFile}.html", encoding="utf-8") as file:
        src = file.read()   
         
    soup = BeautifulSoup(src, "lxml")
    
    if check_sub_ctegory(soup):
        subCats = soup.find_all("h4", class_="category")
        total_subcategories = len(subCats)
        # for idx, item in subCats:
        for idx, item in tqdm(enumerate(subCats), total=total_subcategories, desc="Processing subcategories", unit="subcategory"):
            item_href = item.find("a").get("href")
            item_text = item.find("a").get("title")
            if s[1] == "ru": 
                get_data(item_href, nameCsv, selection, progress_callback)
            progress_callback((idx + 1) / total_subcategories)
    else:
        scrap_data(soup, nameCsv, selection, url, progress_callback)

    
def get_category():
    with open("data/all_categories_dict.json", encoding="utf-8") as file:
        all_categories = json.load(file)
    # print(all_categories)
    category = list()
    for key, value in all_categories.items():
        category_name = value[0]
        category.append(f"{key} - {category_name}")
    return category

    
def href(selection:str):
    with open("data/all_categories_dict.json", encoding="utf-8") as file:
        all_categories = json.load(file)
    # print(all_categories)
    category = list()
    for key, value in all_categories.items():
        category_name = value[0]
        category_link = value[1]
        val = f"{key} - {category_name}"
        if val == selection:
            return category_link

    
def window():
    
    def clicked():
        # Получаем выбранный элемент из Combobox
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
                    "site",
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
        # получаем выделенный элемент
        selection = combobox.get()
        # print(selection)
        lblSelect["text"] = f"Вы выбрали: {selection}"
        
    window = Tk()
    window.geometry('400x250')
    window.title("Парсер сайта объявлений ss.lv")
    
    lbl = Label(window, text="Выберите категорию для парсинга", font=("Arial Bold", 15))
    lbl.grid(column=0, row=0)
    
    category = get_category()
    
    # print(f"Категории: {category}")
    combobox = Combobox(window, values=category, state="readonly", width=30)
    combobox.bind("<<ComboboxSelected>>", selected)
    combobox.current(0)  # установите вариант по умолчанию  
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
    
