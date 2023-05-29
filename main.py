from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait

pd.set_option('display.notebook_repr_html', False)
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 50)
pd.set_option('display.width', 100)
pd.options.mode.chained_assignment = None

# Завантажуєм csv файл в Pandas DataFrame
book = pd.read_csv('List_ID.csv', error_bad_lines=False, sep=';', index_col=0)

# Dolphin remote API
REMOTE_API = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjAzMDE5NiwidXNlcm5hbWUiOiJkb2xwaGluaWdvMzNAZ21haWwuY29tIiwicm9sZSI6ImFkbWluIiwidGVhbUlkIjoxOTc2NTQwLCJ0b2tlbkNyZWF0ZWRBdCI6MTY3NzI2ODEwOX0.4gzf3i4JWOwhVtJVWoX4AhiAz_s7keG9ZZXMHH_g95k'
# Dolphin Local API
LOCALE_API = 'http://localhost:3001/v1.0/browser_profiles/'

# Chrome driver path
CHROME_DRIVER = Service('./chromedriver.exe')

email_url = 'https://mail.google.com/mail/u/0/#all'

site_params = {
    'lime_ware': '/html/body/div[2]/div/section[1]/div/div/div[1]/h1/span[1]',
    'gmail': '/html/body/div[7]/div[3]/div/div[1]/div[3]/header/div[2]/div[1]/div[4]/div/a/img'
}


def menu(dataFrame):
    print('1.LimeWare')
    choice = int(input())
    print(f'Реферальна ссилка: {dataFrame["ref_url"][0]}\n1.Да\n2.Ні')
    choice = int(input())
    if choice == 2:
        print('Введіть нову реферальну ссилку: ')
        dataFrame['ref_url'][0] = str(input())
    print('Виберіть з якого аккаунта розпочинати\nВід 1 до 1000')
    index = int(input())
    dataFrame['index'][0] = index


def get_profiles():
    """Getting all of existing profiles in Dolphin account"""
    data = []
    page = 0
    url = f"https://anty-api.com/browser_profiles?limit=50&page={page}"
    header = {
        'Authorization': f'{REMOTE_API}'
    }
    response = requests.get(url, headers=header)
    data += response.json()['data']

    while len(response.json()['data']) != 0:
        page += 1
        url = f"https://anty-api.com/browser_profiles?limit=50&page={page}"
        header = {
            'Authorization': f'{REMOTE_API}'
        }
        response = requests.get(url, headers=header)
        data += response.json()['data']

    return data


def save_profiles(profile_data):
    """Saving all needed data from every Dolphin profile"""
    for dictionary in profile_data:
        try:
            idx = book[book['profile_id'] == dictionary['id']].index.to_list()[0]
            if "proxy" in dictionary:
                book.loc[idx, 'proxy_name'] = dictionary['proxy']['name']
                book.loc[idx, 'proxy_id'] = str(dictionary['proxy']['id'])
        except:
            pass


def get_proxies():
    """Getting all proxies in Dolphin account"""
    data = []
    try:
        url = 'https://anty-api.com/proxy'
        header = {
            'Authorization': f'{REMOTE_API}'
        }
        response = requests.get(url, headers=header)
        data += response.json()['data']
    except:
        print('Proxys not parsing!')

    return data


def save_proxies(data):
    """Grabs only needed data from all proxies"""
    dictionary = {}
    for i in range(0, len(data)):
        name = data[i]['name']
        changeIpUrl = data[i]['changeIpUrl']

        if changeIpUrl != '':
            dictionary[name] = changeIpUrl

    for id in range(1, len(book['proxy_name']) + 1):
        if book['proxy_name'][id] in dictionary:
            book.loc[id, 'changeIpUrl'] = dictionary[book['proxy_name'][id]]


def get_reload_ip(request_url):
    """Send request for ip reboot"""
    try:
        url = request_url
        header = {
            'Authorization': f'{REMOTE_API}'
        }
        dolphin_response = requests.get(url, headers=header).json()
        print(dolphin_response)
        return dolphin_response
    except:
        print('IP not reloaded correctly')


def close_profile(profile_id, driver):
    """Sending request and closing Dolphin profile"""
    try:
        requests.get(
            f'{LOCALE_API}{profile_id}/stop'
        ).json()
    except:
        print('Помилка при закриті Dolphin!')


def get_debug_port(profile_id):
    """Request to Dolphin certain profile"""
    try:
        data = requests.get(
            f'{LOCALE_API}{profile_id}/start?automation=1'
        ).json()
        return data['automation']['port']
    except:
        print(f'Помилка при відкриті Dolphin: {profile_id} , можливо профіль уже відкритий!')
        return False


def get_webdriver(port):
    """Webdriver parameters"""
    options = webdriver.ChromeOptions()
    options.debugger_address = '127.0.0.1:' + str(port)
    # options.headless = False
    driver = webdriver.Chrome(service=CHROME_DRIVER, options=options)
    driver.wait = WebDriverWait(driver, 5)
    return driver


def set_page_to_front(driver):
    """Setting page to the foreground"""
    driver.minimize_window()
    driver.maximize_window()


def check_current_page(driver, url):
    """Checking if the current page is opened in twitter.com/home"""
    if driver.current_url != url:
        driver.get(url=url)


def wait_window_loaded(driver, site):
    """waiting for octo windows loading"""
    delay = 10
    try:
        WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, site_params[site]))
        )
    except TimeoutException:
        print('wait_window_loaded')


def close_all_tabs(driver):
    """Closed all tabs in the browser"""
    windows = driver.window_handles
    if len(windows) <= 1:
        return
    for index in range(0, len(windows) - 1):
        driver.switch_to.window(windows[index])
        driver.close()
    driver.switch_to.window(windows[len(windows) - 1])
    driver.get('https://www.google.com/')


def paste_email(driver, email, dataFrame, id):
    try:
        input_email = driver.wait.until(EC.presence_of_element_located(
            (By.XPATH,
             '/html/body/div[2]/div/section[4]/div[1]/form/div[1]/div[2]/input')))
        input_email.send_keys(email)
        driver.wait.until(EC.presence_of_element_located(
            (By.XPATH,
             '/html/body/div[2]/div/section[4]/div[1]/form/div[3]/button'))).click()
        dataFrame['lime_ware'][id] = 'Yes'
        dataFrame.to_csv('./data/save.csv', sep=';')
    except:
        print('Error paste_email')
        dataFrame['errors'][id] = 'Error paste_email'
        dataFrame.to_csv('./data/save.csv', sep=';')


def get_email_box(driver, counter, dataFrame, id):
    if counter >= 2:
        dataFrame['email'][id] = 'No envelope'
        dataFrame.to_csv('./data/save.csv', sep=';')
        return
    try:
        box = driver.wait.until(EC.presence_of_element_located(
            (By.XPATH,
             '/html/body/div[7]/div[3]/div/div[2]/div[2]/div/div/div/div/div[2]/div/div[1]/div/div/div[4]/div['
             '1]/div/table/tbody')))
        elements = box.find_elements(By.TAG_NAME, "tr")
        for index in range(0, len(elements)):
            title = elements[index].find_element(
                By.XPATH,
                f'/html/body/div[7]/div[3]/div/div[2]/div[2]/div/div/div/div/div[2]/div/div[1]/div/div/div[4]/div['
                f'1]/div/table/tbody/tr[{index+1}]/td[4]/div[2]/span/span '
            ).text
            print(title)
            if title == 'LimeWire' or title == 'Nova' or title == 'New':
                description = elements[index].find_element(
                    By.XPATH,
                    f'/html/body/div[7]/div[3]/div/div[2]/div[2]/div/div/div/div/div[2]/div/div[1]/div/div/div['
                    f'4]/div[1]/div/table/tbody/tr[{index+1}]/td[5]/div/div/div[2]/span/span '
                ).text
                if description == 'LimeWire Token Sale: Please confirm your e-mail address':
                    time.sleep(1)
                    elements[index].click()
                    dataFrame['email'][id] = 'Verification'
                    dataFrame.to_csv('./data/save.csv', sep=';')
                    time.sleep(1)
                    return
        time.sleep(2)
        try:
            driver.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[7]/div[3]/div/div[2]/div[2]/div/div/div/div/div[1]/div/div[2]/div[1]/div/div/div['
                 '5]/div/div'))) .click()
        except:
            print('Refresh button not found')
        time.sleep(1)
        return get_email_box(driver, counter + 1, dataFrame, id)
    except:
        print('Error get_email_box')
        time.sleep(5)
        return get_email_box(driver, counter + 1, dataFrame, id)
        # dataFrame['errors'][id] = 'Error get_email_box'
        # dataFrame.to_csv('./data/save.csv', sep=';')


def verification_email(driver, dataFrame, id):
    try:
        driver.wait.until(EC.presence_of_element_located(
            (By.XPATH,
             '/html/body/div[7]/div[3]/div/div[2]/div[2]/div/div/div/div/div[2]/div/div[1]/div/div['
             '2]/div/table/tr/td/div[2]/div[2]/div/div[3]/div/div/div/div/div/div[1]/div[2]/div[3]/div[3]/div/div['
             '1]/table/tbody/tr[1]/td/table/tbody/tr/td/p[3]/a'))).click()
        dataFrame['email'][id] = 'Yes'
        dataFrame.to_csv('./data/save.csv', sep=';')
    except:
        print('Error verification_email')
        dataFrame['errors'][id] = 'Error verification_email'
        dataFrame.to_csv('./data/save.csv', sep=';')


def check_verification_lime_ware(driver, status, ref_url, dataFrame, id):
    if status == 'No envelope':
        check_current_page(driver, ref_url)
    wait_window_loaded(driver, 'lime_ware')
    try:
        driver.wait.until(EC.presence_of_element_located(
            (By.XPATH,
             '/html/body/div[2]/div/section[4]/div[2]/div[2]/div[2]/div')))
        dataFrame['check_lime_ware'][id] = 'Yes'
        dataFrame.to_csv('./data/save.csv', sep=';')
    except:
        print('Error verification_lime_ware')
        dataFrame['errors'][id] = 'Error verification_lime_ware'
        dataFrame.to_csv('./data/save.csv', sep=';')


def start_webdriver(id, dataFrame, ref_url):
    """Starting browser profile and run all needed functions"""
    profile_id = dataFrame['profile_id'][id]
    email = dataFrame['gmail'][id]
    port = get_debug_port(profile_id)
    if not port:
        dataFrame['errors'][id] = 'Error start Dolphin'
        dataFrame.to_csv('./data/save.csv', sep=';')
        return
    driver = get_webdriver(port)
    close_all_tabs(driver)
    set_page_to_front(driver)
    if dataFrame['lime_ware'][id] == 'No' and dataFrame['errors'][id] == 'No':
        check_current_page(driver, ref_url)
        wait_window_loaded(driver, 'lime_ware')
        paste_email(driver, email, dataFrame, id)
    if dataFrame['email'][id] == 'No' and dataFrame['errors'][id] == 'No' or dataFrame['email'][id] == 'No envelope' or dataFrame['email'][id] == 'Verification':
        check_current_page(driver, email_url)
        wait_window_loaded(driver, 'gmail')
        get_email_box(driver, 0, dataFrame, id)
    if dataFrame['email'][id] == 'No envelope' and dataFrame['errors'][id] == 'No':
        check_verification_lime_ware(driver, dataFrame['email'][id], ref_url, dataFrame, id)
        time.sleep(2)
        driver.get('https://www.google.com/')
        close_profile(profile_id, driver)
        return
    if dataFrame['email'][id] == 'Verification' and dataFrame['errors'][id] == 'No':
        verification_email(driver, dataFrame, id)
        windows = driver.window_handles
        driver.switch_to.window(windows[len(windows) - 1])
    if dataFrame['check_lime_ware'][id] == 'No' and dataFrame['errors'][id] == 'No' and dataFrame['email'][id] == 'Yes':
        check_verification_lime_ware(driver, dataFrame['email'][id], ref_url, dataFrame, id)
    time.sleep(2)
    close_all_tabs(driver)
    driver.get('https://www.google.com/')
    close_profile(profile_id, driver)
    if dataFrame['errors'][id] == 'No':
        dataFrame['results'][id] = 'Yes'
    dataFrame.to_csv('./data/save.csv', sep=';')


def accounts_multiprocess():
    """Looping through all profiles and running them one by one + rebooting every account IP"""
    options = pd.read_csv('./data/options.csv')
    data = pd.read_csv('./data/save.csv', error_bad_lines=False, sep=';', index_col=0)
    menu(options)
    options.to_csv('./data/options.csv', index=False)
    profile_data = get_profiles()
    save_profiles(profile_data)
    proxies_data = get_proxies()
    save_proxies(proxies_data)
    book.fillna('None', inplace=True)
    data.fillna('No', inplace=True)
    print(book)

    for index in range(options['index'][0], len(book['proxy_name']) + 1):
        print(data.loc[index])
        if data['results'][index] == 'Yes':
            print(f'Account: {index} performed all actions')
            continue
        if data['errors'][index] != 'No':
            data['errors'][index] = 'No'
        if book['proxy_name'][index] != 'None' and book['changeIpUrl'][index] != 'None':
            get_reload_ip(book['changeIpUrl'][index])
        start_webdriver(index, data, options['ref_url'][0])
        print(data.loc[index])
        book.drop(columns=book.columns[9:], axis=1).to_csv('List_ID.csv', sep=';')
    # except:
    #     print('Multiprocess error!')
    #
    # book.drop(columns=book.columns[9:], axis=1).to_csv('List_ID.csv', sep=';')


accounts_multiprocess()
