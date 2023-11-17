import csv
import json

from datetime import datetime
import tkinter
from tkinter.ttk import Combobox, Progressbar

from secure import log
from beautiful_soup import get_category, get_data, href, get_soup
from db_sql import (connect_db, get_data_to_csv_file, delete_table, delete_data_from_table, check_exist_table,
                    create_table_ads, get_data_from_table)
from selen import fill_data, get_selenium_driver

GLOB_ID = 0
COUNT = 0
PORT = 51000


def get_start_pages():
    url = "https://www.ss.lv/ru/"
    url_split = url.split("/")
    soup = get_soup(2, url, url_split)
    heading = soup.find_all("h2")
    i = 1
    all_categories_dict = {}
    for item in heading:
        item_href = item.find("a").get("href")
        item_text = item.find("a").get("title")
        all_categories_dict[i] = item_text, item_href
        with open("data/all_categories_dict.json", "w", encoding="utf-8") as file:
            # indent - отступ в файле
            # ensure_ascii=False - не экранирует символы и помогает при работе
            # с кирилицей
            json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)
        i += 1


def window():
    log.create_log()
    get_start_pages()

    def clicked_get_phone():
        connection = None
        driver = None
        try:
            connection = connect_db()
            connection.autocommit = True

            data = get_data_from_table(connection, get_category_name())
            driver = get_selenium_driver(True, GLOB_ID, PORT)

            pass
            for row in data:
                id_bd = row[0]
                url = row[1]
                fill_data(connection, driver, id_bd, url)

        except Exception as _ex:
            print("tk_clicked_get_phone_ Error while working with PostgreSQL", _ex)
            log.write_log("tk_clicked_get_phone_ Error while working with PostgreSQL", _ex)
            pass

        finally:
            if driver:
                driver.close()
                driver.quit()
                print("[INFO] Selen driver closed")
            if connection:
                connection.close()
                print("[INFO] Сбор номеров телефонов заверщен")

    def clicked_del_table():
        delete_table()

    def clicked_del_data_by_cat():
        delete_data_from_table(get_category_name())

    def get_category_name():
        selection = combobox.get()
        link = href(selection)
        s = link.split("/")
        return s[2]

    def clicked_get_csv():
        cur_date = datetime.now()
        cur_date_str = cur_date.strftime("%Y-%m-%d %H-%M-%S")
        name_csv = f"{get_category_name()}_{cur_date_str}"
        with open(f"result/{name_csv}.csv", "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(
                (
                    "id",
                    "url",
                    "category",
                    "sub_category_1",
                    "sub_category_2",
                    "sub_category_3",
                    "sub_category_4",
                    "sub_category_5",
                    "location",
                    "phone_1",
                    "phone_2",
                    "launch_point"
                )
            )
        get_data_to_csv_file(name_csv)

    def clicked_get_data():
        cur_date = datetime.now()
        log.write_log("Time start - ", cur_date.strftime("%Y-%m-%d %H-%M-%S"))
        connection = None
        try:
            connection = connect_db()
            connection.autocommit = True

            if check_exist_table(connection) is False:
                create_table_ads(connection)

            selection = combobox.get()
            link = href(selection)

            get_data(link, get_category_name(), selection, update_progress, connection)
        except Exception as _ex:
            print("tk_clicked_get_data_ Error while working with PostgreSQL", _ex)
            log.write_log("tk_clicked_get_data _Error while working with PostgreSQL", _ex)
            pass
        finally:
            if connection:
                connection.close()
                print("[INFO] Сбор данных завершен.")
                cur_date = datetime.now()
                log.write_log("Time end - ", cur_date.strftime("%Y-%m-%d %H-%M-%S"))

    def selected(event):
        selection = combobox.get()
        lbl_select["text"] = f"Вы выбрали: {selection}"

    def update_progress(progress):
        bar['value'] = progress * 100

    win = tkinter.Tk()
    win.geometry('350x500')
    win.title("Парсер сайта объявлений ss.lv")

    lbl = tkinter.Label(
        win,
        text="Выберите категорию для парсинга",
        font=("Arial Bold", 15))
    lbl.grid(column=0, row=0, padx=10, pady=15)

    category = get_category()

    combobox = Combobox(win, values=category, state="readonly", width=30)
    combobox.bind("<<ComboboxSelected>>", selected)
    combobox.current(0)
    combobox.grid(column=0, row=10, padx=10)

    lbl_select = tkinter.Label(win, text="", font=("Arial Bold", 15))
    lbl_select.grid(column=0, row=20)

    btn = tkinter.Button(win, text="1 - Запустить сбор ссылок по категории", command=clicked_get_data)
    btn.grid(column=0, row=30, padx=10, pady=15)

    btn = tkinter.Button(win, text="2 - Заполнить номер телефона по категории", command=clicked_get_phone)
    btn.grid(column=0, row=70, padx=10, pady=15)

    btn = tkinter.Button(win, text="3 - Выгрузить данные в таблицу по категории", command=clicked_get_csv)
    btn.grid(column=0, row=80, padx=10, pady=15)

    btn = tkinter.Button(win, text="4 - Удадлить данные по категории", command=clicked_del_data_by_cat)
    btn.grid(column=0, row=90, padx=10, pady=15)

    btn = tkinter.Button(win, text="5 - !!! УДАЛИТЬ ТАБЛИЦУ С ДАННЫМИ в БД !!!", command=clicked_del_table)
    btn.grid(column=0, row=100, padx=10, pady=15)

    bar = Progressbar(win, length=200, mode='determinate')
    bar.grid(column=0, row=110, padx=10, pady=15)

    win.mainloop()
