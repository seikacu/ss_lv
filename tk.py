import csv
import json
import os

from datetime import datetime
import tkinter
from tkinter.ttk import Combobox, Progressbar

from secure import log
from beautiful_soup import get_category, get_data, href, get_soup
from db_sql import (connect_db, get_data_to_csv_file, delete_table, delete_data_from_table, check_exist_table,
                    create_table_ads, get_data_from_table)
from selen import multi_selen, fill_data

GLOB_ID = 0


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

    def get_phones_multithread():
        connection = None
        try:
            connection = connect_db()
            connection.autocommit = True

            data = get_data_from_table(connection, get_category_name())

            step = 0
            data_len = len(data)
            if data_len > 9:
                for j in range(10, 20):
                    if data_len % j == 0:
                        step = j
                        break
                for j in range(9, 1, -1):
                    if data_len % j == 0:
                        step = j
                        break

            elif data_len < 10:
                for j in range(1, 9):
                    if data_len % j == 0:
                        step = j
                        break

            for row in range(0, data_len, step):
                ids = []
                urls = []
                batch = data[row:row + step]
                for i in batch:
                    ids.append(i[0])
                    urls.append(i[1])
                print(f'Будет запущено {step} параллельных потоков')
                multi_selen(step, connection, ids, urls)

        except Exception as _ex:
            print("tk_get_phones_multithread_ Error while working with PostgreSQL", _ex)
            log.write_log("tk_get_phones_multithread_ Error while working with PostgreSQL", _ex)
            pass
        finally:
            if connection:
                connection.close()
                print("[INFO] Сбор номеров телефонов заверщен")

    def get_phones_single():
        connection = None
        try:
            connection = connect_db()
            connection.autocommit = True

            data = get_data_from_table(connection, get_category_name())

            for row in data:
                fill_data(connection, row[0], row[1])

        except Exception as _ex:
            print("tk_get_phones_single_ Error while working with PostgreSQL", _ex)
            log.write_log("tk_get_phones_single_ Error while working with PostgreSQL", _ex)
            pass
        finally:
            if connection:
                connection.close()
                print("[INFO] Сбор номеров телефонов заверщен")

    def clicked_del_table():
        delete_table()

    def clicked_del_data_by_cat():
        delete_data_from_table(get_category_name())

    def del_cache():
        folder_path = 'data'
        files = os.listdir(folder_path)
        html_files = [file for file in files if file.endswith('.html')]
        for html_file in html_files:
            file_path = os.path.join(folder_path, html_file)
            os.remove(file_path)
        print(f"Удалено {len(html_files)} файлов в папке {folder_path}")

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
    win.geometry('400x650')
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

    btn = tkinter.Button(win, text="2.1 - Заполнить номер телефона по категории"
                                   "\n(Многопоточный режим)", command=get_phones_multithread)
    btn.grid(column=0, row=70, padx=10, pady=15)

    btn = tkinter.Button(win, text="2.2 - Заполнить номер телефона по категории"
                                   "\n(Однопоточный режим)", command=get_phones_single)
    btn.grid(column=0, row=75, padx=10, pady=15)

    btn = tkinter.Button(win, text="3 - Выгрузить данные в таблицу по категории", command=clicked_get_csv)
    btn.grid(column=0, row=80, padx=10, pady=15)

    btn = tkinter.Button(win, text="4 - Удадлить данные по категории", command=clicked_del_data_by_cat)
    btn.grid(column=0, row=90, padx=10, pady=15)

    btn = tkinter.Button(win, text="5 - !!! УДАЛИТЬ ТАБЛИЦУ С ДАННЫМИ в БД !!!", command=clicked_del_table)
    btn.grid(column=0, row=100, padx=10, pady=15)

    btn = tkinter.Button(win, text="6 - Очистить кэш", command=del_cache)
    btn.grid(column=0, row=110, padx=10, pady=15)

    bar = Progressbar(win, length=200, mode='determinate')
    bar.grid(column=0, row=120, padx=10, pady=15)

    win.mainloop()
