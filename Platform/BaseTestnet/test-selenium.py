import time
from Platform.BaseTestnet.CreateWallet import CreateWallet
import pandas as pd
import requests
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

pd.set_option('display.notebook_repr_html', False)
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 50)
pd.set_option('display.width', 100)
pd.options.mode.chained_assignment = None


class BaseTestnet:
    def __init__(self):
        self.book = pd.read_csv('../../List_ID.csv', error_bad_lines=False, sep=';', index_col=0)
        self.REMOTE_API = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjAzMDE5NiwidXNlcm5hbWUiOiJkb2xwaGluaWdvMzNAZ21haWwuY29tIiwicm9sZSI6ImFkbWluIiwidGVhbUlkIjoxOTc2NTQwLCJ0b2tlbkNyZWF0ZWRBdCI6MTY3NzI2ODEwOX0.4gzf3i4JWOwhVtJVWoX4AhiAz_s7keG9ZZXMHH_g95k'
        self.LOCALE_API = 'http://localhost:3001/v1.0/browser_profiles/'
        self.CHROME_DRIVER = Service('../../chromedriver.exe')
        self.extension_store = 'https://chrome.google.com/webstore/detail/coinbase-wallet-extension/hnfanknocfeofbddgcijnmhnfnkdnaad/related'
        self.main_page_wallet = 'chrome-extension://hnfanknocfeofbddgcijnmhnfnkdnaad/index.html'
        self.bridge_goerli = 'https://bridge.base.org/deposit'
        self.smart_contract_url = 'https://thirdweb.com/thirdweb.eth/DropERC721'
        self.quest_url = 'https://quests.base.org/'
        self.button_confirm_bridge = '/html/body/div[1]/div/div/div/div/div/div/div/div/div/div[3]/div/div[2]/div/ul/li[3]/button'
        self.button_confirm_contract = '/html/body/div[1]/div/div/div/div/div/div/div/div/div/div[3]/div/div/div/ul/li[3]/button'
        self.button_confirm_signature = '/html/body/div[1]/div/div/div/div/div/div[3]/div/ul/li[3]/button'
        self.data = pd.read_csv('./data/save.csv', error_bad_lines=False, sep=';', index_col=0)
        self.driver = None
        self.session_wallet = False
        self.password = None
        self.contract_adress = None
        self.accounts_multiprocess()

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

    # def wait_window_loaded(self, site):
    #     """waiting for octo windows loading"""
    #     delay = 10
    #     try:
    #         WebDriverWait(self.driver, delay).until(
    #             EC.presence_of_element_located((By.XPATH, site_params[site]))
    #         )
    #     except TimeoutException:
    #         print('wait_window_loaded')

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

    def check_install_wallet(self, index):
        self.check_current_page(self.extension_store)
        status = None
        counter = 0
        while counter < 5 or counter is True:
            try:
                button = self.driver.wait.until(EC.presence_of_element_located(
                    (By.CLASS_NAME,
                     'dd-Va')))
                status = button.get_attribute('aria-label')
                if status == 'Remove from Chrome':
                    print('Wallet installed')
                    self.data['InstallWallet'][index] = 'Yes'
                    self.data.to_csv('./data/save.csv', sep=';')
                    break
                # elif status == 'Add to Chrome':
                #     print('Wallet not installed')
                #     button.click()
                #     WebDriverWait(driver, 60).until(EC.alert_is_present(),
                #                                     'Timed out waiting for PA creation ' +
                #                                     'confirmation popup to appear.')
                #
                #     alert = driver.switch_to.alert
                #     alert.accept()
            except:
                print('check_install_wallet: Status not Found')
                status = 'Error Parsing'
                counter += 1
                time.sleep(0.3)

    def check_registration_wallet(self, index):
        self.check_current_page(self.main_page_wallet)
        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[1]/div/div/div/div/div/div/div/div/div/div[2]/div[1]/div[2]/ul/li[1]/button'))).click()
            result = CreateWallet(self.driver)
            self.data['BackupWords'][index] = " ".join(result.backup_array)
            self.data['PasswordWallet'][index] = result.password
            print(f'Result: {result.password}')
            print(f'Result: {result.backup_array}')
        except TimeoutException:
            self.login_wallet()

        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div/div/div/div/div/div/div/div/div/div[2]/div[2]/ul/li[3]/button'))).click()
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div/div/div/div/div[1]/div/div/div/div[1]/div[1]/button/div/div/span'))).click()
        except TimeoutException:
            pass

        self.data['RegisrtyWallet'][index] = 'Yes'
        self.data.to_csv('./data/save.csv', sep=';')

    def login_wallet(self):
        try:
            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div/div/div/div[1]/div/div/div[3]/div[1]/div/div/div/span/'
                 'input'))).send_keys(self.password)
        except TimeoutException:
            return

        try:
            self.driver.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div/div/div/div[1]/div/div/div[3]/div[2]'))).click()
        except TimeoutException:
            print('login_wallet: Not Found Button')

        self.session_wallet = True

    def connect_wallet(self):
        while True:
            window_handles = self.driver.window_handles
            if len(window_handles) >= 2:
                break
        self.driver.switch_to.window(window_handles[1])
        if not self.session_wallet:
            self.login_wallet()
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div/div/div/div/div[4]/div/ul/li[3]/button'))).click()
        except TimeoutException:
            print('connect_wallet: Not Found Button Connect')
        self.driver.switch_to.window(window_handles[0])
        self.set_page_to_front()

    def confirm_wallet(self, XPATH):
        result = False
        while True:
            window_handles = self.driver.window_handles
            if len(window_handles) >= 2:
                break
        self.driver.switch_to.window(window_handles[1])
        self.login_wallet()
        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div/div/div/div/div/div/div/div/div[2]/button'))).click()
        except TimeoutException:
            pass
        try:
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, XPATH))).click()
        except TimeoutException:
            print('connect_wallet: Not Found Button Confirm')
            result = True
            self.driver.close()
        self.driver.switch_to.window(window_handles[0])
        self.set_page_to_front()
        return result

    def create_smart_contract(self):
        self.check_current_page(self.smart_contract_url)
        self.check_privacy_policy()

        try:
            WebDriverWait(self.driver, 100).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[1]/div[2]/div/header/div[2]/button[2]'))).click()
        except TimeoutException:
            print('create_smart_contract: Error click Button')
        try:
            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[4]/ul/li[2]/button'))).click()
            self.connect_wallet()
            try:
                WebDriverWait(self.driver, 100).until(EC.element_to_be_clickable(
                    (By.XPATH,
                     '/html/body/div[1]/div[2]/div/header/div[2]/button[2]'))).click()
            except TimeoutException:
                print('create_smart_contract: Error click Button')
        except TimeoutException:
            pass

        self.check_privacy_policy()

        try:
            current_network = WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[3]/div/div[3]/button')))
            if current_network.text != 'Base Goerli Testnet':
                current_network.click()
                self.switch_network()
        except TimeoutException:
            print('create_smart_contract: Error with check Balance Block and check Network')

        result = self.check_balance(False)
        if result == 'Not enough Goerli ETH':
            return
        self.driver.get(self.smart_contract_url)
        while True:
            if self.check_balance(True):
                break
            time.sleep(5)
            self.driver.get(self.smart_contract_url)
        self.deploy_now()
        if self.confirm_wallet(self.button_confirm_contract):
            return
        self.confirm_wallet(self.button_confirm_signature)

    def deploy_now(self):
        try:
            WebDriverWait(self.driver, 100).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[1]/div[2]/main/div/div/div[1]/div[2]/div/button'))).click()
        except TimeoutException:
            print('deploy_now: Button Deploy Not Found')

        try:
            WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[3]/div[3]/div/div/div/div/form/div[2]/div[2]/div[2]/div[1]/div[1]'
                 '/input'))).send_keys('BaseNft')
        except TimeoutException:
            print('deploy_now: Input Name Not Found')

        try:
            WebDriverWait(self.driver, 100).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[3]/div[3]/div/div/div/div/form/div[5]/button[2]'))).click()
        except TimeoutException:
            print('deploy_now: Button Last Not Found')

    def switch_network(self):
        try:
            WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[4]/div[2]/div[3]/input'))).send_keys('Base Goerli Testnet')
            WebDriverWait(self.driver, 100).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[4]/div[2]/div[5]/div/ul/li[1]/div/div'))).click()
        except TimeoutException:
            pass

    def check_balance(self, bridge_complete):
        try:
            balance = WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div[2]/div/header/div[2]/button[2]/div[2]/span[1]'))).text
            if float(balance.split()[0]) <= 0 and not bridge_complete:
                print('Go Faucet')
                return self.switch_tokens()
            if float(balance.split()[0]) > 0:
                return True
        except TimeoutException:
            print('check_balance: Error get balance')

    def click_deposit(self):
        try:
            WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div[5]/button'))).click()
            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[2]/div[2]/div/div/div/div/div[2]/footer/div/button[2]'))).click()
        except TimeoutException:
            print('switch_tokens: Not Found Button Deposit')

        try:
            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[2]/div[2]/div/div/div/div/div[2]/footer/div/button[2]'))).click()
        except TimeoutException:
            pass

    def switch_tokens(self):
        self.check_current_page(self.bridge_goerli)
        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div/div/div/div/div[2]/div[1]/header/nav/div/div/button'))).click()
            WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[2]/div/div/div[2]/div/div/div/div/div/div[2]/div[2]/div[1]/button/div/div/div[2]'))).click()
            self.connect_wallet()
        except TimeoutException:
            pass

        try:
            WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div[4]/div[2]/button'))).click()
            input_balance = WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/input')))
            balance = input_balance.get_attribute('value')
            if float(balance) < 0.01:
                return 'Not enough Goerli ETH'
            else:
                input_balance.clear()
                input_balance.send_keys('0,01')
        except TimeoutException:
            print('switch_tokens: Not Found Button Max')

        try:
            network = WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div/div/div/div/div[2]/div[1]/header/nav/div/div/div/div/button[1]')))
            if network.text == 'SWITCH NETWORK':
                network.click()
        except TimeoutException:
            print('switch_tokens: Not Found Button Network')

        while True:
            self.click_deposit()
            transaction = self.confirm_wallet(self.button_confirm_bridge)
            if not transaction:
                break
            time.sleep(1)

    def check_privacy_policy(self):
        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[3]/div[3]/div/section/div/form/div/label/span'))).click()
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[3]/div[3]/div/section/div/form/button'))).click()
        except TimeoutException:
            pass

    def mint_nft(self):
        self.check_current_page(self.quest_url)
        try:
            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div[1]/div/div[1]/button'))).click()
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[6]/ul/li[1]/button'))).click()
            self.connect_wallet()
        except TimeoutException:
            pass

        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[1]/div/div[1]/div/div[2]/div/div/div/div[2]/div/button'))).click()
        except TimeoutException:
            print('mint_nft: Button Start Quest Not Found')

        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[1]/div/div[1]/div/div[2]/div/div/div/div[3]/label/div/div/div/input'))).click()
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[1]/div/div[1]/div/div[2]/div/div/div/div[4]/div'))).click()
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[2]/div/div/div[2]/div/div/button'))).click()
        except TimeoutException:
            pass

        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH,
                 'EC.presence_of_element_located'))).send_keys(self.contract_adress)
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div/button'))).click()
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div/button'))).click()
        except TimeoutException:
            pass


        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[2]/div[1]/div/div/div[2]/div/div/button'))).click()
        except TimeoutException:
            pass

    def routing(self, index):
        if self.data['InstallWallet'][index] == 'No':
            self.check_install_wallet(index)
        self.password = self.data['PasswordWallet'][index]
        if self.data['RegisrtyWallet'][index] == 'No':
            self.check_registration_wallet(index)
        self.password = self.data['PasswordWallet'][index]
        if self.data['SmartContract'] == 'No':
            self.create_smart_contract()
        if self.data['MintNft'] == 'No':
            self.mint_nft()


    def start_WebDriver(self, id):
        """Starting browser profile and run all needed functions"""
        profile_id = self.data['profile_id'][id]
        port = self.get_debug_port(profile_id)
        self.driver = self.get_webdriver(port)
        self.close_all_tabs()
        self.set_page_to_front()
        self.routing(id)

        # close_profile(id)

    def accounts_multiprocess(self):
        """Looping through all profiles and running them one by one + rebooting every account IP"""
        profile_data = self.get_profiles()
        self.save_profiles(profile_data)
        proxies_data = self.get_proxies()
        self.save_proxies(proxies_data)
        self.book.fillna('None', inplace=True)
        self.data.fillna('No', inplace=True)
        print(self.book)
        try:
            for index in range(1, len(self.book['proxy_name']) + 1):
                print(self.data.loc[index])
                self.session_wallet = False
                if self.data['MintNft'][index] == 'Yes':
                    print(f'Account: {index} performed all actions')
                    continue
                # if data['errors'][index] != 'No':
                #     data['errors'][index] = 'No'
                # if book['proxy_name'][index] != 'None' and book['changeIpUrl'][index] != 'None':
                #     get_reload_ip(book['changeIpUrl'][index])
                self.start_WebDriver(index)
                print(self.data.loc[index])
                self.book.drop(columns=self.book.columns[9:], axis=1).to_csv('List_ID.csv', sep=';')
        except:
            print('Multiprocess error!')

        self.book.drop(columns=self.book.columns[9:], axis=1).to_csv('List_ID.csv', sep=';')


BaseTestnet()
