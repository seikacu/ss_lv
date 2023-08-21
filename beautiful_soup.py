import csv
import json
import os
import re
import threading


import requests

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tqdm import tqdm

from selen import get_phone


def get_category():
    with open("data/all_categories_dict.json", encoding="utf-8") as file:
        all_categories = json.load(file)
    category = list()
    for key, value in all_categories.items():
        category_name = value[0]
        category.append(f"{key} - {category_name}")
    return category


def get_data(href: str, name_csv, selection, progress_callback):
    url = f"https://www.ss.lv{href}"
    url_split = href.split("/")
    soup = get_soup(2, url, url_split)
    if check_sub_category(soup):
        sub_cats = soup.find_all("h4", class_="category")
        total_subcategories = len(sub_cats)
        for idx, item in tqdm(enumerate(sub_cats), total=total_subcategories, desc="Processing subcategories",
                              unit="subcategory"):
            item_href = item.find("a").get("href")
            # item_text = item.find("a").get("title")
            if url_split[1] == "ru":
                get_data(item_href, name_csv, selection, progress_callback)
            progress_callback((idx + 1) / total_subcategories)
    else:
        scrap_data(soup, name_csv, selection, url)  # , progress_callback


def href(selection: str):
    with open("data/all_categories_dict.json", encoding="utf-8") as file:
        all_categories = json.load(file)
    for key, value in all_categories.items():
        category_name = value[0]
        category_link = value[1]
        val = f"{key} - {category_name}"
        if val == selection:
            return category_link


def get_soup(mode, url, url_split):
    ua = UserAgent()
    user_agent = ua.random
    headers = {"User-Agent": f"{user_agent}"}
    file_name = ""

    if mode == 1:
        file_name = url_split[len(url_split) - 3]
    if mode == 2:
        if len(url_split) == 4:
            file_name = url_split[2]
        if len(url_split) == 5:
            file_name = url_split[3]
        if len(url_split) == 6:
            file_name = url_split[4]
        if len(url_split) == 7:
            file_name = url_split[5]
        if len(url_split) == 8:
            file_name = url_split[6]
        if len(url_split) == 9:
            file_name = url_split[7]
        if len(url_split) == 10:
            file_name = url_split[8]
    if mode == 3:
        file_name = url_split[len(url_split) - 1]

    if not file_name.endswith(".html"):
        file_name += ".html"
    r = requests.get(url=url, headers=headers, allow_redirects=False)
    if not os.path.exists("data"):
        os.mkdir("data")
    with open(f"data/{file_name}", "w", encoding="utf-8") as file:
        file.write(r.text)
    with open(f"data/{file_name}", encoding="utf-8") as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")
    return soup


def check_sub_category(soup: BeautifulSoup):
    sub_cat = soup.find_all("h4", class_="category")
    if len(sub_cat) > 0:
        return True
    else:
        return False


def scrap_data(soup: BeautifulSoup, name_csv, selection, url):  # , progress_callback
    # count = 1
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
                lin_split = lin.split("/")
                soup = get_soup(3, url, lin_split)
                get_hrefs(name_csv, selection, soup)
                i += 1
    else:
        pass
        get_hrefs(name_csv, selection, soup)


def fill_data_thread(link_href, name_csv, selection):
    fill_data(link_href, name_csv, selection)


def get_hrefs(name_csv, selection, soup):
    div_d1_tags = soup.find_all('div', {'class': 'd1'})
    for div_tag in div_d1_tags:
        links = div_tag.find_all('a')
        for link in links:
            fill_data(link['href'], name_csv, selection)

    # Многопоточность - каждая ссылка запускается в отдельном потоке (до 25 потоков)
    # threads = []
    # for div_tag in div_d1_tags:
    #     links = div_tag.find_all('a')
    #     for link in links:
    #         link_href = link['href']
    #         thread = threading.Thread(target=fill_data_thread, args=(link_href, name_csv, selection))
    #         threads.append(thread)
    #         thread.start()
    #
    # for thread in threads:
    #     thread.join()


def fill_data(link, name_csv, selection):
    # phone = ""
    email = ""
    # site = ""
    location = ""
    # category = ""
    sub_category_1 = ""
    sub_category_2 = ""
    sub_category_3 = ""
    sub_category_4 = ""
    sub_category_5 = ""
    url = f"https://www.ss.lv{link}"
    url_split = link.split("/")
    soup = get_soup(3, url, url_split)
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
    td_locate = soup.find('td', class_='ads_contacts_name', string=re.compile(r'место', re.IGNORECASE))
    if td_locate:
        next_td_locate = td_locate.find_next('td', class_='ads_contacts')
        if next_td_locate:
            text = next_td_locate.get_text()
            location = text
    phone = get_phone(url)
    with open(f"result/{name_csv}.csv", "a", newline='', encoding="utf-8") as file:
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


def get_list_links(soup: BeautifulSoup, name_csv, selection):
    div_d1_tags = soup.find_all('div', {'class': 'd1'})
    for div_tag in div_d1_tags:
        links = div_tag.find_all('a')
        for link in links:
            fill_data(link['href'], name_csv, selection)
