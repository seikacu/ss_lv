import platform
import time
import zipfile

from python_rucaptcha.image_captcha import ImageCaptcha
from python_rucaptcha.re_captcha import ReCaptcha
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as ex_cond

from selenium.webdriver.support.ui import WebDriverWait

import secure
from db_sql import add_phone1, add_phone2


def set_driver_options(options):
    # безголовый режим браузера
    # options.add_argument('--headless=new')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-data-dir={get_path_profile()}")


def get_path_profile():
    if platform.system() == "Windows":
        return r"C:\WebDriver\chromedriver\user"
    elif platform.system() == "Linux":
        return "/home/seikacu/webdriver/user"
    elif platform.system() == "Darwin":
        return "webdriver/chromedriver-macos/user"
    else:
        raise Exception("selen_get_path_profile_Unsupported platform!")


def get_path_webdriver():
    if platform.system() == "Windows":
        return r"C:\WebDriver\chromedriver\chromedriver.exe"
    elif platform.system() == "Linux":
        return "/home/seikacu/webdriver//chromedriver"
    elif platform.system() == "Darwin":
        return "webdriver/chromedriver-macos"
    else:
        raise Exception("selen_get_path_webdriver_Unsupported platform!")


def get_selenium_driver(use_proxy=False):
    options = webdriver.ChromeOptions()
    set_driver_options(options)

    if use_proxy:
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        plugin_file = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr('manifest.json', secure.manifest_json_1)
            zp.writestr('background.js', secure.background_js_1)

        options.add_extension(plugin_file)

    user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/116.0.5845.967 YaBrowser/23.9.1.967 Yowser/2.5 Safari/537.36")
    options.add_argument(f'--user-agent={user_agent}')

    caps = DesiredCapabilities().CHROME
    caps['pageLoadStrategy'] = 'eager'

    service = Service(
        desired_capabilities=caps,
        executable_path=get_path_webdriver())
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def extract_phone_numbers(connection, driver: webdriver.Chrome, id_db):
    try:
        phone1 = driver.find_element(By.XPATH, "//span[contains(@id, 'phone_td_1')]").text
        if phone1.endswith("***"):
            return False
        add_phone1(connection, id_db, phone1)
    except NoSuchElementException as ex:
        add_phone1(connection, id_db, "снято с публикации")
        reason = "selen_extract_phone_numbers_Не удалось получить телефон"
        secure.log.write_log(reason, ex)
        pass
    try:
        phone2 = driver.find_element(By.XPATH, "//span[contains(@id, 'phone_td_2')]").text
        add_phone2(connection, id_db, phone2)
    except NoSuchElementException as ex:
        reason = "selen_extract_phone_numbers_Отсутствует 2-ой телефон"
        secure.log.write_log(reason, ex)
        pass


def solve_image_captcha(driver: webdriver.Chrome):
    try:
        image_elem = driver.find_element(By.ID, "ss_tcode_img")
        image_elem.screenshot("captcha.png")
        image_captcha = ImageCaptcha(rucaptcha_key=secure.rucaptcha_token)
        text_captcha = image_captcha.captcha_handler(
            captcha_file="captcha.png")['captchaSolve']
        text_captcha = str(text_captcha).upper()
        input_text = driver.find_element(
            By.XPATH, "//input[contains(@id, 'ads_show_phone')]")
        input_text.send_keys(text_captcha)
        driver.find_element(
            By.XPATH,
            "//input[contains(@value, 'Показать номер')]").click()
        time.sleep(1)
    except NoSuchElementException as ex:
        reason = "selen_solve_image_captcha_Графическая капча не найдена"
        secure.log.write_log(reason, ex)
        pass
    except ElementNotInteractableException as ex:
        reason = "selen_solve_image_captcha (элемент не активен)"
        secure.log.write_log(reason, ex)
        print(reason)
        pass


def click_i_no_robot(driver):
    try:
        recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
        recaptcha_iframe.click()
        time.sleep(1)
    except NoSuchElementException as ex:
        reason = "selen_click_i_no_robot Элемент Я не робот не найден"
        secure.log.write_log(reason, ex)
        pass
    except ElementNotInteractableException as ex:
        reason = "selen_click_i_no_robot (элемент не активен)"
        secure.log.write_log(reason, ex)
        print(reason)
        pass


def get_phone(connection, driver: webdriver.Chrome, id_bd):
    try:
        try:
            show_phone = driver.find_element(By.XPATH, "//a[contains(@onclick, '_show_phone')]")
            if show_phone.is_displayed():
                driver.execute_script("arguments[0].click();", show_phone)
                time.sleep(1)
            # ДОБАВИТЬ ПРОВЕРКУ НА ВСПЛЫВАЮЩЕЕ ОКНО "Вы зашли по неверной ссылке,
            # либо у объявления истёк срок публикации. ss.lv"
            # Находим элемент с id "alert_msg" и получаем его текст
            alert = driver.find_element(By.ID, "alert_msg").text
            if 'Вы зашли по неверной ссылке' in alert:
                print("ПОПАЛСЯ!!!))))")
                # !!!Добавить смену прокси и обноление страницы!!!
                pass

        except NoSuchElementException as ex:
            reason = "selen_get_phone_ Кнопка Показать номер телефона отсутствует, и/или объявление снято с публикации"
            secure.log.write_log(reason, ex)
            print(reason)
            pass
        # solve_image_captcha(driver)
        # click_i_no_robot(driver)
        # solve_recaptcha(driver)
        time.sleep(1)
        if extract_phone_numbers(connection, driver, id_bd) is False:
            driver.refresh()
            get_phone(connection, driver, id_bd)
    except NoSuchElementException as ex:
        reason = "selen_get_phone_Элемент не найден"
        secure.log.write_log(reason, ex)
        print(ex)
        pass


def solve_recaptcha(driver: webdriver.Chrome):
    try:
        phone = driver.find_element(By.XPATH, "//span[contains(@id, 'phone_td_1')]").text
        if phone.endswith("***") is False:
            return

        # iframe_hidden = driver.find_element(
        #     By.XPATH, '//iframe[@title="reCAPTCHA"]')

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
        iframe_hidden = WebDriverWait(driver, 30).until(ex_cond.presence_of_element_located((
            By.XPATH, '//iframe[@style="display: none;"]')))
        driver.execute_script(
            "arguments[0].style.display = 'inline-block';",
            iframe_hidden)
        elem_hidden = WebDriverWait(driver, 30).until(ex_cond.presence_of_element_located((
            By.XPATH, '//textarea[@id="g-recaptcha-response"]')))
        driver.execute_script(
            "arguments[0].style.display = 'inline-block';",
            elem_hidden)

        # !!! РЕШЕНИЕ КАПЧИ !!!
        re_captcha = ReCaptcha(
            rucaptcha_key=secure.rucaptcha_token,
            pageurl=driver.current_url,
            googlekey=key,
            method='userrecaptcha'
        )
        result = re_captcha.captcha_handler()
        result = result['captchaSolve']

        elem_hidden.send_keys(result)
        driver.execute_script(f"{callback}('{key}')")
    except NoSuchElementException as ex:
        reason = "selen_solve_recaptcha_ Recaptcha отсутствует"
        secure.log.write_log(reason, ex)
        pass
    except ElementNotInteractableException as ex:
        reason = "selen_solve_recaptcha_ (элемент не активен)"
        secure.log.write_log(reason, ex)
        print(reason)
        pass


def fill_data(connection, driver: webdriver.Chrome, id_bd, link):
    try:
        driver.get(link)

        # Кнопка Принять и продолжить
        try:
            cookie_confirm_div = driver.find_element(By.ID, 'cookie_confirm_dv')
            accept_button = cookie_confirm_div.find_element(
                By.XPATH, './/button[contains(text(), "Принять и продолжить")]')
            accept_button.click()
            driver.refresh()
        except NoSuchElementException as ex:
            reason = "selen_fill_data_Кнопка принять и продолжить отсутствует"
            secure.log.write_log(reason, ex)
            pass

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        get_phone(connection, driver, id_bd)

    except NoSuchElementException as ex:
        reason = "selen_fill_data_Элемент не найден"
        secure.log.write_log(reason, ex)
        pass
