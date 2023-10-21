



# dcap = dict (DesiredCapabilities.PHANTOMJS) #setuserAgent
# dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 ")

# Путь к исполняемому файлу PhantomJS
# phantomjs_path = r'C:\WebDriver\PhantomJS\phantomjs'

# dcap = dict(DesiredCapabilities.PHANTOMJS) dcap["phantomjs.page.settings.userAgent"] = ( "Mozilla/5.0 (Windows
# NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3" )


# Создание объекта драйвера PhantomJS
# driver = webdriver.PhantomJS(executable_path=phantomjs_path, desired_capabilities=dcap)



# driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': 'alert("Hooray! I did it!")'})

# new_onclick_value = "_show_phone(1,'',null);"
# driver.execute_script("arguments[0].setAttribute('onclick', arguments[1]);", show_phone, new_onclick_value)
# driver.execute_script("arguments[0].click();", show_phone)



def test():
    cookies = {
        'LG': 'ru',
        'sid': '690797dfd93d29b221e4f580c6e91b778df5ef2f97e3f9837bc7fb4f6cd77efd583d8bdefb6228a5bce16df9f16023fe',
        '_ga': 'GA1.2.1714425831.1690582726',
        '__gads': 'ID=e478bd1281b7c0d7-22573a830fe30021:T=1690582785:RT=1691090915:S=ALNI_MaO1z8q5g7Xq7s7z51mVScrQXTgIA',
        '__gpi': 'UID=00000d29fb330c2f:T=1690582785:RT=1691090915:S=ALNI_MZDmkpX3wmtaHC4z5Xe_eWsGtO6xA',
        'PHPSESSID': 'd0d2eabc18fa09403a91a6f4fc9a3e9d',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0',
        'Accept': 'message/x-ajax',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.ss.lv/msg/ru/construction/garden-technics/hothouses/bmghxn.html',
        # 'Cookie': 'LG=ru; sid=690797dfd93d29b221e4f580c6e91b778df5ef2f97e3f9837bc7fb4f6cd77efd583d8bdefb6228a5bce16df9f16023fe; _ga=GA1.2.1714425831.1690582726; __gads=ID=e478bd1281b7c0d7-22573a830fe30021:T=1690582785:RT=1691090915:S=ALNI_MaO1z8q5g7Xq7s7z51mVScrQXTgIA; __gpi=UID=00000d29fb330c2f:T=1690582785:RT=1691090915:S=ALNI_MZDmkpX3wmtaHC4z5Xe_eWsGtO6xA; PHPSESSID=d0d2eabc18fa09403a91a6f4fc9a3e9d',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }

    response = requests.get(
        'https://www.ss.lv/js/ru/2022-10-04/e1a7846f3e4f02824c69f0e48b63a4b29ae3be2afbb13a976b291131943ad8fa.js?d=N1V1RdtC^%^2BPxWA1NhUTC^%^2BiQ0UJ^%^2FSpuqE^%^2Bnvk5oogs6YogluM64UBA5qf^%^2FFi^%^2FSr5Z6iXbqLVB7dU2KoBf016VsfevEmRxsFBZr0ITTtGZzkFZMom5jMYK4UlZt0BqOEWCpACXG25eHbfN0DjHiHjK5DHBEICh9MOOzuDojLsj60uki6WTLlbVN86qk8dL7UUrMyDvJF66AlG^%^2F6CjnWBzbdg33CmQj38agNTANQgfn1Q3WSB4n7dEGwmbD4VuBxoi^%^2B1duGvpNxNqCNlX6FfQPIhMos6YDn9ZYuNWxAdbBiwX66yyqHkH908tvR6YO9LQKcWdCbAFNAGmxaOqVBsYO88UeqQxRo735bnTwwRfSUICNHOnE2HkbWHOYYqls2kNAHL2rgQHpU5NHFHfERWb9KuJNmpsWsQfhhQ8Sa0xlxBXR7ILpZxsKJo6BCoDa^%^2BmkFlJGpjOMgaNNjHpj5j3BwRDlzmHuREykRM3NcjVaJ8Tth17JXr9n4HLG95TrYcbVfAB&c=1&x=870&y=571&code=nsk',
        cookies=cookies,
        headers=headers,
    )

    with open(f"data/test.html", "w", encoding="utf-8") as file:
        file.write(response.text)


def test_2():
    url = "https://www.ss.lv/js/ru/2023-07-21/5d448e531eb26e5cd978fab3b399bf72af7f39f63ec80ce0b20cba336198f91e.js?d=https//www.ss.lv/msg/ru/transport/cars/volkswagen/tiguan/mfbhk.html"
    response = requests.get(url)
    response.json
    print(response.content)


def test_3():
    phantomjs_path = r'C:\WebDriver\PhantomJS\phantomjs'

    driver = webdriver.PhantomJS(executable_path=phantomjs_path)

    driver.get('https://www.google.com')

    driver.quit()


def test_proxy():
    options = uc.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')

    # options = webdriver.ChromeOptions()
    # set_driver_options(options)

    ua = UserAgent()
    user_agent = ua.random
    options.add_argument(f'--user-agent={user_agent}')
    options.add_argument("--start-maximized")

    # caps = DesiredCapabilities().CHROME
    # # caps['pageLoadStrategy'] = 'eager'
    # caps['pageLoadStrategy'] = 'normal'

    seleniumwire_options = {
        'verify_ssl': False,
        'proxy': {
            'https': f'https://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}'
        }
    }

    # service = Service(desired_capabilities=caps, executable_path=r"C:\WebDriver\chromedriver\chromedriver.exe")
    driver = uc.Chrome(version_main=108, seleniumwire_options=seleniumwire_options, options=options)

    # seleniumwire_options=seleniumwire_options,
    # service=service,
    driver.get("https://whoer.net")
    time.sleep(100)



# def fill_data_thread(link_href, name_csv, selection):
#     fill_data(link_href, name_csv, selection)


# def get_hrefs(name_csv, selection, soup):
#     # urls = []
#     div_d1_tags = soup.find_all('div', {'class': 'd1'})
#     for div_tag in div_d1_tags:
#         links = div_tag.find_all('a')
#         for link in links:
#             # urls.append(link['href'])
#             fill_data(link['href'], name_csv, selection)


# print(urls)
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


# def fill_data(link, name_csv, selection):
#     # phone = ""
#     email = ""
#     # site = ""
#     location = ""
#     # category = ""
#     sub_category_1 = ""
#     sub_category_2 = ""
#     sub_category_3 = ""
#     sub_category_4 = ""
#     sub_category_5 = ""
#     url = f"https://www.ss.lv{link}"
#     url_split = link.split("/")
#     soup = get_soup(2, url, url_split)
#     sels = selection.split("-")
#     category = sels[1]
#     links = soup.select('h2.headtitle a')
#     arr_links = []
#     for link in links:
#         arr_links.append(link.text)
#     for i in range(0, len(arr_links)):
#         if i == 0:
#             sub_category_1 = arr_links[0]
#         if i == 1:
#             sub_category_2 = arr_links[1]
#         if i == 2:
#             sub_category_3 = arr_links[2]
#         if i == 3:
#             sub_category_4 = arr_links[3]
#         if i == 4:
#             sub_category_5 = arr_links[4]
#     td_locate = soup.find('td', class_='ads_contacts_name', string=re.compile(r'место', re.IGNORECASE))
#     if td_locate:
#         next_td_locate = td_locate.find_next('td', class_='ads_contacts')
#         if next_td_locate:
#             text = next_td_locate.get_text()
#             location = text
#     # phones = get_phone(url)
#     # phone = ";".join(phones)
#     with open(f"result/{name_csv}.csv", "a", newline='', encoding="utf-8") as file:
#         writer = csv.writer(file)
#         writer.writerow(
#             (
#                 # phone.replace(",", ".").strip(),
#                 email.replace(",", ".").strip(),
#                 # site.replace(",", ".").strip(),
#                 location.replace(",", ".").strip(),
#                 category.replace(",", ".").strip(),
#                 sub_category_1.replace(",", ".").strip(),
#                 sub_category_2.replace(",", ".").strip(),
#                 sub_category_3.replace(",", ".").strip(),
#                 sub_category_4.replace(",", ".").strip(),
#                 sub_category_5.replace(",", ".").strip(),
#                 url
#             )
#         )


# async def gather_data(launch_point, selection, soup, connection):
#     urls = []
#     div_d1_tags = soup.find_all('div', {'class': 'd1'})
#     for div_tag in div_d1_tags:
#         links = div_tag.find_all('a')
#         for link in links:
#             urls.append(link['href'])
#             # fill_data(link['href'], name_csv, selection)
#
#     async with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as session:  # trust_env=True
#         tasks = []
#
#         for url in range(0, len(urls)):
#             link = urls[url]
#             task = asyncio.create_task(get_page_data(session, link, launch_point, selection, connection))
#             tasks.append(task)
#
#         await asyncio.gather(*tasks)


            # s = link.split("/")
            # category_name = s[2]
            # cur_date = datetime.now()
            # cur_date_str = cur_date.strftime("%Y-%m-%d %H-%M-%S")
            # name_csv = f"{category_name}_{cur_date_str}"
            # with open(f"result/{name_csv}.csv", "w", newline='', encoding="utf-8") as file:
            #     writer = csv.writer(file)
            #     writer.writerow(
            #         (
            #             "phone",
            #             "email",
            #             # "site",
            #             "location",
            #             "category",
            #             "sub_category_1",
            #             "sub_category_2",
            #             "sub_category_3",
            #             "sub_category_4",
            #             "sub_category_5",
            #             "url"
            #         )
            #     )










# ОТОБРАЖЕНИЕ КАТЕГОРИЙ

        for item in sub_cats:
            item_href = item.find("a").get("href")
            print(item_href)
            # for
            get_data(item_href, launch_point, selection, progress_callback, connection)



    # таким же способом проверять следующию иерархию ссылки, и если она не равна предыдущей, то пропускать ее
    len_link_split = len(link_split)
    if len_link_split == 5:
        print(link)
        pass
    elif len_link_split == 6:
        print(link)
        pass
    elif len_link_split == 7:
        print(link)
        pass
    elif len_link_split == 8:
        print(link)
        pass
    elif len_link_split == 9:
        print(link)
        pass
    elif len_link_split == 10:
        print(link)
        pass
