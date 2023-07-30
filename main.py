import re
import os
import requests
import json
import csv


from tkinter import *
from tkinter.ttk import Combobox, Progressbar 
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime

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
        i +=1
    
def check_sub_ctegory(soup:BeautifulSoup):
    subCat = soup.find_all("h4", class_="category")
    if len(subCat) > 0:
        return True;
    else:
        return False

def scrap_data(soup:BeautifulSoup, nameCsv, progress_callback):
    
    count = 1
    pages = soup.find("a", class_="navi")
    if pages is not None:
        pages.get("href")
        pattern = r'page(\d+)\.html'
        match = re.search(pattern, pages_count)
        print(pages)
        if match:
            count = int(match.group(1))
            print(count)
        else:
            print("No number found in the string.")
    else:
        print("Страница всего одна.")
        
    i = 0
    while i < count:
        div_d1_tags = soup.find_all('div', {'class': 'd1'})
        for div_tag in div_d1_tags:
            links = div_tag.find_all('a')
            for link in links:
                print(link['href'])
        i +=1

    print("TEST")
    with open(f"result/{nameCsv}.csv", "a", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                phone,
                email,
                site,
                location,
                category_1,
                category_2,
                category_3,
                category_4,
                category_5,
                category_6
              )
        )
    
        # Simulate some work
    # for i in tqdm(range(100), desc="Scraping data", unit="item"):
    #     # Your actual scraping logic here...
    #     # ...
    #
    #     # Update progress
    #     progress_callback((i + 1) / 100)

def get_data(href:str, nameCsv, progress_callback):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    url = f"https://www.ss.lv{href}"
    r = requests.get(url=url, headers=headers)
     
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
                get_data(item_href, nameCsv, progress_callback)
            progress_callback((idx + 1) / total_subcategories)
    else:
        scrap_data(soup, nameCsv, progress_callback)
    
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
        with open(f"result/{nameCsv}.csv", "w", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    "phone",
                    "email",
                    "site",
                    "location",
                    "category_1",
                    "category_2",
                    "category_3",
                    "category_4",
                    "category_5",
                    "category_6"
                )
            )
        
        get_data(link, nameCsv, update_progress)
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
    