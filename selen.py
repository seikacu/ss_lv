# import http.client
# import gzip
# import pickle
# import os
# import sys
import time
# import random
import zipfile

from python_rucaptcha.image_captcha import ImageCaptcha
from python_rucaptcha.re_captcha import ReCaptcha
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from seleniumwire import undetected_chromedriver as uc
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

from fake_useragent import UserAgent
from rucaptcha import token
from proxy_auth_data import login, password

PROXY_HOST = '136.0.181.142'
PROXY_PORT = '64902'
PROXY_USER = login
PROXY_PASS = password

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"76.0.0"
}
"""

background_js = """
let config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };
chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}
chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


def set_driver_options(options):
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument("--disable-proxy-certificate-handler")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--user-data-dir=C:\\WebDriver\\chromedriver\\user")
    options.add_argument("--user-data-dir=C:\\WebDriver\\chromedriver\\user_proxy")
    options.add_argument("--start-maximized")
    # options.add_argument('--headless=new')
    # options.add_argument('--enable-javascript')
    # options.debugger_address = 'localhost:8989'


def get_selenium_driver(use_proxy=False, user_agent=False):
    # options = uc.ChromeOptions()
    options = webdriver.ChromeOptions()
    set_driver_options(options)

    if use_proxy:
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        plugin_file = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr('manifest.json', manifest_json)
            zp.writestr('background.js', background_js)

        options.add_extension(plugin_file)

    ua = UserAgent()
    if user_agent:
        user_agent = ua.random
        options.add_argument(f'--user-agent={user_agent}')
    else:
        user_agent = ua.chrome
        options.add_argument(f'--user-agent={user_agent}')

    caps = DesiredCapabilities().CHROME
    caps['pageLoadStrategy'] = 'eager'
    # caps['pageLoadStrategy'] = 'normal'

    # seleniumwire_options = {
    #     'proxy': {
    #         'https': f'https://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}'
    #     }
    # }

    service = Service(desired_capabilities=caps, executable_path=r"C:\WebDriver\chromedriver\chromedriver.exe")
    # service=service, seleniumwire_options=seleniumwire_options,
    driver = webdriver.Chrome(service=service, options=options)
    # driver = uc.Chrome(version_main=109, service=service, options=options)

    return driver


def extract_phone_numbers(driver: webdriver.Chrome):
    phone1 = ""
    phone2 = ""
    try:
        phone1 = driver.find_element(By.XPATH, "//span[contains(@id, 'phone_td_1')]").text
        phone2 = driver.find_element(By.XPATH, "//span[contains(@id, 'phone_td_2')]").text
    except NoSuchElementException:
        # print(NoSuchElementException)
        # print("Не удалось получить телефоны")
        pass
    phone_numbers = f"{phone1};{phone2}"
    return phone_numbers


def solve_image_captcha(driver: webdriver.Chrome):
    try:
        image_elem = driver.find_element(By.ID, "ss_tcode_img")
        image_elem.screenshot("captcha.png")
        image_captcha = ImageCaptcha(rucaptcha_key=token)
        text_captcha = image_captcha.captcha_handler(captcha_file="captcha.png")['captchaSolve']
        text_captcha = str(text_captcha).upper()
        input_text = driver.find_element(By.XPATH, "//input[contains(@id, 'ads_show_phone')]")
        input_text.send_keys(text_captcha)
        driver.find_element(By.XPATH, "//input[contains(@value, 'Показать номер')]").click()
        time.sleep(1)
    except NoSuchElementException:
        # print(NoSuchElementException)
        # print("Графическая капча не найдена")
        pass


def get_phone(url):
    try:
        driver = get_selenium_driver(use_proxy=True, user_agent=True)
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Кнопка Принять и продолжить
        try:
            cookie_confirm_div = driver.find_element(By.ID, 'cookie_confirm_dv')
            accept_button = cookie_confirm_div.find_element(By.XPATH,
                                                            './/button[contains(text(), "Принять и продолжить")]')
            accept_button.click()
            driver.refresh()
        except NoSuchElementException:
            pass
        try:
            # element = driver.find_element(By.ID, 'phdivz_1')
            # if not element.is_displayed():
            #     # Изменить значение атрибута style на "display:true;"
            #     driver.execute_script("arguments[0].style.display = 'inline-block';", element)
            #     time.sleep(random.randrange(3, 6))
            show_phone = driver.find_element(By.XPATH, "//a[contains(@onclick, '_show_phone')]")
            if show_phone.is_displayed():
                driver.execute_script("arguments[0].click();", show_phone)
                time.sleep(2)
        except NoSuchElementException:
            # print(NoSuchElementException)
            print("Кнопка показать телефон не найдена")
        solve_recaptcha(driver)
        solve_image_captcha(driver)
        phone_numbers = extract_phone_numbers(driver)[:-1]

        # driver.close()
        driver.quit()
        return phone_numbers
    except NoSuchElementException:
        print(NoSuchElementException)
        phone_numbers = extract_phone_numbers(driver)[:-1]
        return phone_numbers


def solve_recaptcha(driver: webdriver.Chrome):
    try:
        recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
        find_recaptcha_clients = '''
          // eslint-disable-next-line camelcase
          if (typeof (___grecaptcha_cfg) !== 'undefined') {
            // eslint-disable-next-line camelcase, no-undef
            return Object.entries(___grecaptcha_cfg.clients).map(([cid, client]) => {
              const data = { id: cid, version: cid >= 10000 ? 'V3' : 'V2' };
              const objects = Object.entries(client).filter(([_, value]) => value && typeof value === 'object');

              objects.forEach(([toplevelKey, toplevel]) => {
                const found = Object.entries(toplevel).find(([_, value]) => (
                  value && typeof value === 'object' && 'sitekey' in value && 'size' in value
                ));

                if (typeof toplevel === 'object' && toplevel instanceof HTMLElement && toplevel['tagName'] === 'DIV'){
                    data.pageurl = toplevel.baseURI;
                }

                if (found) {
                  const [sublevelKey, sublevel] = found;

                  data.sitekey = sublevel.sitekey;
                  const callbackKey = data.version === 'V2' ? 'callback' : 'promise-callback';
                  const callback = sublevel[callbackKey];
                  if (!callback) {
                    data.callback = null;
                    data.function = null;
                  } else {
                    data.function = callback;
                    const keys = [cid, toplevelKey, sublevelKey, callbackKey].map((key) => `['${key}']`).join('');
                    data.callback = `___grecaptcha_cfg.clients${keys}`;
                  }
                }
              });
              return data;
            });
          }
          return [];
        '''

        find_recaptcha = driver.execute_script(find_recaptcha_clients)
        dict_key = find_recaptcha[0]
        key = dict_key["sitekey"]
        callback = dict_key["callback"]

        # !!! поиск элемента ввода решения капчи !!!
        iframe_hidden = recaptcha_iframe.find_element(By.XPATH, '//iframe[@style="display: none;"]')
        driver.execute_script("arguments[0].style.display = 'inline-block';", iframe_hidden)
        elem_hidden = recaptcha_iframe.find_element(By.XPATH, '//textarea[@id="g-recaptcha-response"]')
        driver.execute_script("arguments[0].style.display = 'inline-block';", elem_hidden)

        # ПРОВЕРКА РАБОТЫ КАПЧИ И СЕРВИСА RUCAPTCHA
        # data_post = {'key': token, 'method': 'userrecaptcha', 'googlekey': key, "pageurl": driver.current_url}
        # response = requests.post(url='https://2captcha.com/in.php', data=data_post)
        # print(response)
        # print(response.text)

        # !!! РЕШЕНИЕ КАПЧИ !!!
        re_captcha = ReCaptcha(
            rucaptcha_key=token,
            pageurl=driver.current_url,
            googlekey=key,
            method='userrecaptcha'
        )
        result = re_captcha.captcha_handler()
        result = result['captchaSolve']

        elem_hidden.send_keys(result)
        driver.execute_script(f"{callback}('{key}')")
        time.sleep(1)
    except NoSuchElementException:
        # print("Recaptcha не найдена")
        pass
