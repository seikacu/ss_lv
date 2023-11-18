import threading
import time
import zipfile

from python_rucaptcha.image_captcha import ImageCaptcha
from python_rucaptcha.re_captcha import ReCaptcha
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException, \
    WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as ex_cond
from fake_useragent import UserAgent

from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import secure
import tk
from db_sql import add_phone1, add_phone2


def set_driver_options(options):
    # безголовый режим браузера
    options.add_argument('--headless=new')
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument("--disable-blink-features=AutomationControlled")


def get_selenium_driver(use_proxy, num_proxy):
    ua = UserAgent()
    options = webdriver.ChromeOptions()
    set_driver_options(options)

    if use_proxy:
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        plugin_file = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr('manifest.json', secure.get_proxy_pref(num_proxy, 0))
            zp.writestr('background.js', secure.get_proxy_pref(num_proxy, 1))

        options.add_extension(plugin_file)

    options.add_argument(f'--user-agent={ua.random}')

    caps = DesiredCapabilities().CHROME
    caps['pageLoadStrategy'] = 'normal'

    service = Service(ChromeDriverManager().install(), desired_capabilities=caps)
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def extract_phone_numbers(connection, driver: webdriver.Chrome, id_db):
    try:
        phone1 = driver.find_element(By.XPATH, "//span[contains(@id, 'phone_td_1')]").text
        if phone1.endswith("***"):
            return False
        add_phone1(connection, id_db, phone1)
    except NoSuchElementException:
        add_phone1(connection, id_db, "Объявление снято с публикации")
        reason = "selen_extract_phone_numbers_ Объявление снято с публикации"
        secure.log.write_log(reason, '')
        pass
    try:
        phone2 = driver.find_element(By.XPATH, "//span[contains(@id, 'phone_td_2')]").text
        add_phone2(connection, id_db, phone2)
    except NoSuchElementException:
        reason = "selen_extract_phone_numbers_Отсутствует 2-ой телефон"
        secure.log.write_log(reason, '')
        pass


def solve_image_captcha(driver: webdriver.Chrome):
    try:
        try:
            phone_td = driver.find_element(By.XPATH, "//span[contains(@id, 'phone_td_1')]")
            if phone_td:
                phone = phone_td.text
                if '***' not in phone:
                    return
        except NoSuchElementException:
            reason = "selen_solve_image_captcha_Номер телефона отсутствует - Объявление снято с публикации"
            secure.log.write_log(reason, '')
            pass

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
        time.sleep(2)
    except NoSuchElementException:
        reason = "selen_solve_image_captcha_Графическая капча не найдена"
        secure.log.write_log(reason, '')
        pass
    except ElementNotInteractableException as ex:
        reason = "selen_solve_image_captcha (элемент не активен)"
        secure.log.write_log(reason, ex)
        pass


def get_phone(connection, driver: webdriver.Chrome, id_bd):
    try:
        try:
            try:
                driver.find_element(By.XPATH, "//span[contains(@id, 'phone_td_1')]")
            except NoSuchElementException:
                add_phone1(connection, id_bd, "Объявление снято с публикации")
                reason = "get_phone Номер телефона отсутствует, и/или объявление снято с публикации"
                secure.log.write_log(reason, '')
                pass
                return
            show_phone = WebDriverWait(driver, 10).until(ex_cond.presence_of_element_located((
                By.XPATH, "//a[contains(@onclick, '_show_phone')]")))
            if show_phone.is_displayed():
                driver.execute_script("arguments[0].click();", show_phone)
                time.sleep(1)
            try:
                # ПРОВЕРКА НА ВСПЛЫВАЮЩЕЕ ОКНО "Вы зашли по неверной ссылке,
                # либо у объявления истёк срок публикации. ss.lv"
                alert = driver.find_element(By.ID, "alert_msg")
                if alert:
                    alert_txt = alert.text
                    if 'Вы зашли по неверной ссылке' in alert_txt:
                        link = driver.current_url
                        if tk.GLOB_ID < 1:
                            tk.GLOB_ID += 1
                        else:
                            tk.GLOB_ID = 0
                        print('СМЕНА PROXY ПО ALERT')
                        secure.log.write_log("СМЕНА PROXY ПО ALERT: ", f'new tk.GLOB_ID: {tk.GLOB_ID}')
                        time.sleep(600)
                        fill_data(connection, id_bd, link)
            except NoSuchElementException:
                reason = "selen_get_phone_ Верная ссылка - объявление актуально"
                secure.log.write_log(reason, '')
                pass
            pass
        except TimeoutException as ex:
            reason = ("selen_get_phone_timeout - Кнопка Показать номер телефона отсутствует, и/или объявление снято с "
                      "публикации")
            secure.log.write_log(reason, ex)
            pass
        except NoSuchElementException:
            reason = "selen_get_phone_ Кнопка Показать номер телефона отсутствует, и/или объявление снято с публикации"
            secure.log.write_log(reason, f'Номер id в БД: {id_bd}')
            pass
        time.sleep(1)

        solve_image_captcha(driver)
        check_alert(connection, driver, id_bd)
        solve_recaptcha(driver)
        time.sleep(2)
        if extract_phone_numbers(connection, driver, id_bd) is False:
            print("ПОВТОР ПОЛУЧЕНИЯ НОМЕРА")
            secure.log.write_log("ПОВТОР ПОЛУЧЕНИЯ НОМЕРА", f'Запись в БД: {id_bd}')
            driver.refresh()
            get_phone(connection, driver, id_bd)
    except NoSuchElementException as ex:
        reason = "selen_get_phone_Элемент не найден"
        secure.log.write_log(reason, ex)
        pass
    except WebDriverException as ex:
        change_proxy(connection, driver, ex, id_bd)
        pass


def solve_recaptcha(driver: webdriver.Chrome):
    try:
        phone_td = driver.find_element(By.XPATH, "//span[contains(@id, 'phone_td_1')]")
        if phone_td:
            phone = phone_td.text
            if '***' not in phone:
                return

            WebDriverWait(driver, 10).until(ex_cond.presence_of_element_located((
                By.XPATH, '//iframe[@title="reCAPTCHA"]')))

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
        iframe_hidden = WebDriverWait(driver, 60).until(ex_cond.presence_of_element_located((
            By.XPATH, '//iframe[@style="display: none;"]')))
        driver.execute_script(
            "arguments[0].style.display = 'inline-block';",
            iframe_hidden)
        elem_hidden = WebDriverWait(driver, 60).until(ex_cond.presence_of_element_located((
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
    except IndexError as ierr:
        reason = 'solve_recaptcha IndexError '
        secure.log.write_log(reason, ierr)
        pass
    except TimeoutException:
        reason = "solve_recaptcha iframe_hidden timeout "
        secure.log.write_log(reason, '')
        pass
    except NoSuchElementException:
        reason = "selen_solve_recaptcha_ Recaptcha отсутствует"
        secure.log.write_log(reason, '')
        pass
    except ElementNotInteractableException as ex:
        reason = "selen_solve_recaptcha_ (элемент не активен)"
        secure.log.write_log(reason, ex)
        pass


def check_alert(connection, driver, id_bd):
    try:
        phone_td = driver.find_element(By.XPATH, "//span[contains(@id, 'phone_td_1')]")
        if phone_td:
            phone = phone_td.text
            if '***' not in phone:
                return
    except NoSuchElementException:
        reason = "selen_solve_image_captcha_Номер телефона отсутствует - Объявление снято с публикации"
        secure.log.write_log(reason, '')
        pass
    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert_txt = alert.text
        print('УПАЛА ГУГЛОВСКАЯ КАПЧА!!!')
        print(alert_txt)
        alert.accept()
        time.sleep(60)
        fill_data(connection, id_bd, driver.current_url)
    except TimeoutException:
        pass
    except NoSuchElementException as ex:
        reason = "ALERT NoSuchElementException"
        secure.log.write_log(reason, ex)
        pass
    except ElementNotInteractableException as ex:
        reason = "ALERT ElementNotInteractableException"
        secure.log.write_log(reason, ex)
        pass


def fill_data(connection, id_bd, link):
    driver = None
    try:
        driver = get_selenium_driver(True, tk.GLOB_ID)

        driver.get(link)

        # Кнопка Принять и продолжить
        try:
            cookie_confirm_div = driver.find_element(By.ID, 'cookie_confirm_dv')
            accept_button = cookie_confirm_div.find_element(
                By.XPATH, './/button[contains(text(), "Принять и продолжить")]')
            accept_button.click()
            driver.refresh()
        except NoSuchElementException:
            reason = "selen_fill_data_Кнопка принять и продолжить отсутствует"
            secure.log.write_log(reason, '')
            pass

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        get_phone(connection, driver, id_bd)

    except NoSuchElementException as ex:
        reason = "selen_fill_data_Элемент не найден"
        secure.log.write_log(reason, ex)
        pass
    except WebDriverException as ex:
        print(ex)
        change_proxy(connection, driver, ex, id_bd)
        pass
    finally:
        if driver:
            driver.close()
            driver.quit()
            print("[INFO] Selen driver closed")


def change_proxy(connection, driver, ex, id_bd):
    reason = "clicked_get_phone _ ОШИБКА ПРОКСИ"
    secure.log.write_log(reason, ex)
    link = driver.current_url
    if tk.GLOB_ID < 1:
        tk.GLOB_ID += 1
    else:
        tk.GLOB_ID = 0
    print('СМЕНА PROXY')
    secure.log.write_log("СМЕНА PROXY: ", f'new tk.GLOB_ID: {tk.GLOB_ID}')
    time.sleep(600)
    fill_data(connection, id_bd, link)


def multi_selen(step, connection, ids, urls):

    threads = []
    for i in range(0, step):
        thread = threading.Thread(target=fill_data, args=(connection, ids[i], urls[i],))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
