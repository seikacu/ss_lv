# import http.client
# import gzip
# import pickle
import time
import random
import zipfile

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium_recaptcha_solver import RecaptchaSolver
# from seleniumwire import undetected_chromedriver as uc
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

from fake_useragent import UserAgent

from proxy_auth_data import login, password

PROXY_HOST = '185.122.206.63'
PROXY_PORT = '4515'
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
    # options.add_argument("--disable-proxy-certificate-handler")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--user-data-dir=C:\\WebDriver\\chromedriver\\user")
    options.add_argument("--start-maximized")
    options.add_argument('--headless=new')
    # options.add_argument('--enable-javascript')


def get_selenium_driver(use_proxy=False, user_agent=True):
    # options = uc.ChromeOptions()
    options = webdriver.ChromeOptions()
    set_driver_options(options)

    if use_proxy:
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        plugin_file = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr('manifest.json', manifest_json)
            zp.writestr('background.js', background_js)

        options.add_extension(plugin_file)

    if user_agent:
        ua = UserAgent()
        user_agent = ua.random
        options.add_argument(f'--user-agent={user_agent}')

    caps = DesiredCapabilities().CHROME
    # caps['pageLoadStrategy'] = 'eager'
    caps['pageLoadStrategy'] = 'normal'

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
    phone_numbers = f"{phone1};{phone2};"
    return phone_numbers


def get_phone(url):
    try:
        driver = get_selenium_driver(use_proxy=False, user_agent=True)
        solver = RecaptchaSolver(driver=driver)
        driver.get(url)
        # time.sleep(random.randrange(1, 3))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.randrange(1, 3))

        # Кнопка Принять и продолжить
        try:
            cookie_confirm_div = driver.find_element(By.ID, 'cookie_confirm_dv')
            accept_button = cookie_confirm_div.find_element(By.XPATH,
                                                            './/button[contains(text(), "Принять и продолжить")]')
            accept_button.click()
            time.sleep(random.randrange(3, 6))
        except NoSuchElementException:
            pass
        try:
            element = driver.find_element(By.ID, 'phdivz_1')
            if not element.is_displayed():
                # Изменить значение атрибута style на "display:true;"
                driver.execute_script("arguments[0].style.display = 'inline-block';", element)
                time.sleep(random.randrange(3, 6))
            show_phone = driver.find_element(By.XPATH, "//a[contains(@onclick, '_show_phone')]")
            if show_phone.is_displayed():
                driver.execute_script("arguments[0].click();", show_phone)
                time.sleep(random.randrange(3, 6))
        except NoSuchElementException:
            # print(NoSuchElementException)
            print("Кнопка показать телефон не найдена")
        try:
            recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
            recaptcha_iframe.find_element(By.XPATH, '//textarea[@id="g-recaptcha-response"]')
            recaptcha_iframe.click()
            time.sleep(random.randrange(3, 6))
            show_phone = driver.find_element(By.XPATH, "//a[contains(@onclick, '_show_phone')]")
            try:
                if show_phone.is_displayed():
                    recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
                    solver.click_recaptcha_v2(iframe=recaptcha_iframe)
            except:
                # print(selenium_recaptcha_solver.exceptions.RecaptchaException)
                print("БЛОКИРОВКА ГУГЛ ПРИ РЕШЕНИИ КАПЧИ!!!")
                # time.sleep(random.randrange(30, 60))
                pass
            time.sleep(random.randrange(3, 6))
        except NoSuchElementException:
            print("Капча не найдена")
            pass
        phone_numbers = extract_phone_numbers(driver)[:-1]

        driver.close()
        driver.quit()
        return phone_numbers
    except NoSuchElementException:
        print(NoSuchElementException)
        phone_numbers = extract_phone_numbers(driver)[:-1]
        return phone_numbers
