import csv
import json
import os

from datetime import datetime
from tkinter import *
from tkinter.ttk import Combobox, Progressbar

from beautiful_soup import get_category, get_data, href, get_soup


def get_start_pages():
    url = "https://www.ss.lv/ru/"
    url_split = url.split("/")
    soup = get_soup(1, url, url_split)
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


def window():
    get_start_pages()

    def clicked():
        selection = combobox.get()
        link = href(selection)
        s = link.split("/")
        category_name = s[2]
        if not os.path.exists("result"):
            os.mkdir("result")
        cur_date = datetime.now()
        cur_date_str = cur_date.strftime("%Y-%m-%d")
        name_csv = f"{category_name}_{cur_date_str}"
        with open(f"result/{name_csv}.csv", "w", newline='', encoding="utf-8") as file:
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
        get_data(link, name_csv, selection, update_progress)

    def selected(event):
        selection = combobox.get()
        lbl_select["text"] = f"Вы выбрали: {selection}"

    def update_progress(progress):
        bar['value'] = progress * 100

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

    lbl_select = Label(window, text="", font=("Arial Bold", 15))
    lbl_select.grid(column=0, row=20)

    btn = Button(window, text="Запустить", command=clicked)
    btn.grid(column=0, row=30)

    bar = Progressbar(window, length=200, mode='determinate')
    bar.grid(column=0, row=40)

    window.mainloop()
