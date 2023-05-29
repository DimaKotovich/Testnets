import time
from Wallet.MetaMask.meta_mask import MetaMask
import pandas as pd
import requests
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

pd.options.mode.chained_assignment = None


class Gmx:
    def __init__(self):
        self.book = pd.read_csv('../../List_ID.csv', error_bad_lines=False, sep=';', index_col=0)
        # self.data = pd.read_csv('./data/save.csv', error_bad_lines=False, sep=';', index_col=0)
        self.REMOTE_API = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjAzMDE5NiwidXNlcm5hbWUiOiJkb2xwaGluaWdvMzNAZ21haWwuY29tIiwicm9sZSI6ImFkbWluIiwidGVhbUlkIjoxOTc2NTQwLCJ0b2tlbkNyZWF0ZWRBdCI6MTY3NzI2ODEwOX0.4gzf3i4JWOwhVtJVWoX4AhiAz_s7keG9ZZXMHH_g95k'
        self.LOCALE_API = 'http://localhost:3001/v1.0/browser_profiles/'
        self.FAUCET_API = 'https://faucet.avax.network/'
        self.CHROME_DRIVER = Service('../../chromedriver.exe')
        self.SWAP_API = 'https://app.gmxtest.io/#/dashboard'
        self.BUY_TOKEN_API = 'https://app.gmxtest.io/#/pools'
        self.TRADE_API = 'https://app.gmxtest.io/#/v2'
        self.driver = None
        self.wallet = None
        self.session_wallet = False
        self.password = None
        self.contract_adress = None
        self.start_WebDriver(1000)
        # self.accounts_multiprocess()

    def get_profiles(self):
        """Getting all of existing profiles in Dolphin account"""
        data = []
        page = 0
        url = f"https://anty-api.com/browser_profiles?limit=50&page={page}"
        header = {
            'Authorization': f'{self.REMOTE_API}'
        }
        response = requests.get(url, headers=header)
        data += response.json()['data']

        while len(response.json()['data']) != 0:
            page += 1
            url = f"https://anty-api.com/browser_profiles?limit=50&page={page}"
            header = {
                'Authorization': f'{self.REMOTE_API}'
            }
            response = requests.get(url, headers=header)
            data += response.json()['data']

        return data

    def save_profiles(self, profile_data):
        """Saving all needed data from every Dolphin profile"""
        for dictionary in profile_data:
            try:
                idx = self.book[self.book['profile_id'] == dictionary['id']].index.to_list()[0]
                if "proxy" in dictionary:
                    self.book.loc[idx, 'proxy_name'] = dictionary['proxy']['name']
                    self.book.loc[idx, 'proxy_id'] = str(dictionary['proxy']['id'])
            except:
                pass

    def get_proxies(self):
        """Getting all proxies in Dolphin account"""
        data = []
        try:
            url = 'https://anty-api.com/proxy'
            header = {
                'Authorization': f'{self.REMOTE_API}'
            }
            response = requests.get(url, headers=header)
            data += response.json()['data']
        except:
            print('Proxys not parsing!')

        return data

    def save_proxies(self, data):
        """Grabs only needed data from all proxies"""
        dictionary = {}
        for i in range(0, len(data)):
            name = data[i]['name']
            changeIpUrl = data[i]['changeIpUrl']

            if changeIpUrl != '':
                dictionary[name] = changeIpUrl

        for id in range(1, len(self.book['proxy_name']) + 1):
            if self.book['proxy_name'][id] in dictionary:
                self.book.loc[id, 'changeIpUrl'] = dictionary[self.book['proxy_name'][id]]

    def get_reload_ip(self, request_url):
        """Send request for ip reboot"""
        try:
            url = request_url
            header = {
                'Authorization': f'{self.REMOTE_API}'
            }
            dolphin_response = requests.get(url, headers=header).json()
            print(dolphin_response)
            return dolphin_response
        except:
            print('IP not reloaded correctly')

    def close_profile(self, profile_id):
        """Sending request and closing Dolphin profile"""
        try:
            requests.get(
                f'{self.LOCALE_API}{profile_id}/stop'
            ).json()
        except:
            print('Помилка при закриті Dolphin!')

    def get_debug_port(self, profile_id):
        """Request to Dolphin certain profile"""
        try:
            data = requests.get(
                f'{self.LOCALE_API}{profile_id}/start?automation=1'
            ).json()
            return data['automation']['port']
        except:
            print(f'Помилка при відкриті Dolphin: {profile_id} , можливо профіль уже відкритий!')
            return False

    def get_webdriver(self, port):
        """Webdriver parameters"""
        options = webdriver.ChromeOptions()
        options.debugger_address = '127.0.0.1:' + str(port)
        # options.headless = False
        driver = webdriver.Chrome(service=self.CHROME_DRIVER, options=options)
        driver.wait = WebDriverWait(driver, 5)
        return driver

    def set_page_to_front(self):
        """Setting page to the foreground"""
        self.driver.minimize_window()
        self.driver.maximize_window()

    def check_current_page(self, url):
        """Checking if the current page is opened in twitter.com/home"""
        if self.driver.current_url != url:
            self.driver.get(url=url)

    def close_all_tabs(self):
        """Closed all tabs in the browser"""
        windows = self.driver.window_handles
        if len(windows) <= 1:
            return
        for index in range(0, len(windows) - 1):
            self.driver.switch_to.window(windows[index])
            self.driver.close()
        self.driver.switch_to.window(windows[len(windows) - 1])
        self.driver.get('https://www.google.com/')

    # def wait_window_loaded(self, site):
    #     """waiting for octo windows loading"""
    #     delay = 10
    #     try:
    #         WebDriverWait(self.driver, delay).until(
    #             EC.presence_of_element_located((By.XPATH, site_params[site]))
    #         )
    #     except TimeoutException:
    #         print('wait_window_loaded')

    def start_WebDriver(self, id):
        """Starting browser profile and run all needed functions"""
        profile_id = self.book['profile_id'][id]
        port = self.get_debug_port(profile_id)
        self.driver = self.get_webdriver(port)
        self.set_page_to_front()
        self.close_all_tabs()
        # self.check_current_page(self.FAUCET_API)
        # self.press_faucet_connect_wallet_button()
        # self.check_current_page(self.SWAP_API)
        # self.press_dashboard_connect_wallet_button()
        # self.check_current_page(self.BUY_TOKEN_API)
        # self.buy_tokens()
        self.check_current_page(self.TRADE_API)
        self.buy_long()

        time.sleep(5)
        # self.close_all_tabs()
        # self.driver.quit()
        # self.close_profile(profile_id)

    def accounts_multiprocess(self):
        """Looping through all profiles and running them one by one + rebooting every account IP"""
        profile_data = self.get_profiles()
        self.save_profiles(profile_data)
        proxies_data = self.get_proxies()
        self.save_proxies(proxies_data)
        self.book.fillna('None', inplace=True)
        # self.data.fillna('No', inplace=True)
        print(self.book)
        try:
            for index in range(1, len(self.book['proxy_name']) + 1):
                print(self.data.loc[index])
                self.session_wallet = False
                if self.book['proxy_name'][index] != 'None' and self.book['changeIpUrl'][index] != 'None':
                    self.get_reload_ip(self.book['changeIpUrl'][index])
                self.start_WebDriver(index)
                print(self.data.loc[index])
                self.book.drop(columns=self.book.columns[9:], axis=1).to_csv('List_ID.csv', sep=';')
        except:
            print('Multiprocess error!')

        self.book.drop(columns=self.book.columns[9:], axis=1).to_csv('List_ID.csv', sep=';')

    def press_faucet_connect_wallet_button(self):
        """Pressing on connect wallet button and checking if it was connected"""
        try:
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[1]/div/div[1]/div[1]/div[2]/div[2]/div[1]/span'))).click()
            try:
                WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/div[1]/div/div[1]/div[1]/div[2]/div[2]/button'))).click()
            except TimeoutException:
                print('press_faucet_connect_wallet_button: Could not find Request_2_AVAX button')
        except TimeoutException:
            print('press_faucet_connect_wallet_button: Could not find connect wallet button')

    def press_dashboard_connect_wallet_button(self):
        """Pressing on connect wallet button and checking if it was connected"""
        try:
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="root"]/div[1]/div/header/div[1]/div[2]/div/button'))).click()
            try:
                WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/div[1]/div[4]/div[2]/div[3]/div/button[1]'))).click()
            except TimeoutException:
                print('press_dashboard_connect_wallet_button: Could not find meta mask button')
        except TimeoutException:
            try:
                WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="headlessui-menu-button-144"]/button'))).click()
            except TimeoutException:
                print('press_dashboard_connect_wallet_button: Could not find connect wallet button')

    def buy_tokens(self):
        """Buying tokens"""
        try:
            time.sleep(5)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div[1]/div/div/div[2]/div[2]/div/div[3]/div[1]/div[2]/div[1]/input'))).send_keys('0.1')
            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/div[1]/div[1]/div/div/div[2]/div[2]/div/div[5]/button'))).click()
            except TimeoutException:
                try:
                    WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                        (By.XPATH, '//*[@id="root"]/div[1]/div/div/div[2]/div[2]/div/div[5]/button'))).click()
                except TimeoutException:
                    print('buy_tokens: Could not find Enter_An_Amount button')
        except TimeoutException:
            print('buy_tokens: Could not find pay input')

    def buy_short(self):
        """Buying in short position"""
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/form/div/div[1]/div[1]/div[2]'))).click()
            time.sleep(5)
            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                    (By.XPATH,
                     '/html/body/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/form/div/div[4]/div[2]/div[2]/div/div'))).click()
                try:
                    WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                        (By.XPATH,
                         '/html/body/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/form/div/div[4]/div[2]/div[2]/div/div[1]/div[2]/div[3]/div/div/div[1]'))).click()

                    try:
                        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                            (By.XPATH,
                             '/html/body/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/form/div/div[2]/div[2]/div[1]/input'))).send_keys(
                            '0.1')

                        try:
                            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                                (By.XPATH,
                                 '/html/body/div[1]/div[1]/div/div/div[1]/div[2]/div/div[1]/div[7]/button'))).click()

                            try:
                                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                                    (By.XPATH,
                                     '/html/body/div[1]/div[1]/div/div/div[1]/div[2]/div/div[4]/div/div[2]/div[3]/div/div[1]/div[13]/div/span[1]/svg'))).click()

                                try:
                                    WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                                        (By.XPATH,
                                         '/html/body/div[1]/div[1]/div/div/div[1]/div[2]/div/div[4]/div/div[2]/div[3]/div/div[2]/button'))).click()
                                except TimeoutException:
                                    print('buy_long: could not find buy button')

                            except TimeoutException:
                                print('buy_long: could not find checkbox')

                        except TimeoutException:
                            print('buy_long: Cold not find buy button')

                    except TimeoutException:
                        print('buy_long: could not find token input')

                except TimeoutException:
                    print('buy_long: could not find select token button')

            except TimeoutException:
                print('buy_long: could not find change token button')
        except TimeoutException:
            print('buy_short: could not find short button')

    def buy_long(self):
        """Buying in long position"""
        time.sleep(5)
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/form/div/div[4]/div[2]/div[2]/div/div'))).click()
            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                    (By.XPATH,
                     '/html/body/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/form/div/div[4]/div[2]/div[2]/div/div[1]/div[2]/div[3]/div/div/div[1]'))).click()

                try:
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                        (By.XPATH,
                         '/html/body/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/form/div/div[2]/div[2]/div[1]/input'))).send_keys(
                        '0.1')

                    try:
                        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                            (By.XPATH,
                             '/html/body/div[1]/div[1]/div/div/div[1]/div[2]/div/div[1]/div[7]/button'))).click()

                        try:
                            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                                (By.XPATH,
                                 '/html/body/div[1]/div[1]/div/div/div[1]/div[2]/div/div[4]/div/div[2]/div[3]/div/div[1]/div[10]/div/span[1]/svg'))).click()

                            try:
                                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                                    (By.XPATH,
                                     '/html/body/div[1]/div[1]/div/div/div[1]/div[2]/div/div[4]/div/div[2]/div[3]/div/div[2]/button'))).click()
                            except TimeoutException:
                                print('buy_long: could not find buy button')

                        except TimeoutException:
                            print('buy_long: could not find checkbox')

                    except TimeoutException:
                        print('buy_long: Cold not find buy button')

                except TimeoutException:
                    print('buy_long: could not find token input')

            except TimeoutException:
                print('buy_long: could not find select token button')

        except TimeoutException:
            print('buy_long: could not find change token button')


Gmx()
