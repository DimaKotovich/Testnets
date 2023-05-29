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


class MetaMask:
    def __init__(self, driver, password=None):
        self.driver = driver
        self.main_url = 'chrome-extension://cfkgdnlcieooajdnoehjhgbmpbiacopjflbjpnkm/home.html'
        self.setting_advanced = 'chrome-extension://cfkgdnlcieooajdnoehjhgbmpbiacopjflbjpnkm/home.html#settings/advanced'
        self.add_network_manual = 'chrome-extension://cfkgdnlcieooajdnoehjhgbmpbiacopjflbjpnkm/home.html#settings/networks/add-network'
        self.password = 'NjrsjnjrsJ2005'
        self.goerli_network = 'Тестова мережа Goerli'
        self.zkSync_network = 'zkSync Alpha Testnet'
        self.opside_testnet = 'Opside Testnet'
        self.button_approve = '//*[@id="app-content"]/div/div[2]/div/div[2]/div/button[2]'
        self.balance = None
        self.difference = None
        self.session_login = False
        self.current_network = None

    def wait_window_loaded(self, element='//*[@id="app-content"]/div/div[1]/div/div[1]/img', delay=10):
        """waiting for octo windows loading"""
        try:
            WebDriverWait(self.driver, delay).until(
                EC.presence_of_element_located((By.XPATH, element))
            )
        except TimeoutException:
            print('wait_window_loaded')
            self.driver.get(self.main_url)
            self.wait_window_loaded()

    def check_current_page(self, url):
        """Checking if the current page is opened in twitter.com/home"""
        if self.driver.current_url != url:
            self.driver.get(url=url)

    def open_wallet(self):
        # self.driver.execute_script("window.open('');")
        # window_handles = self.driver.window_handles
        # self.driver.switch_to.window(window_handles[1])
        self.driver.switch_to.new_window('tab')
        self.driver.get(self.main_url)

    def login_password(self):
        self.wait_window_loaded()
        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="password"]'))).send_keys(self.password)
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div/button'))).click()
            self.session_login = True
        except TimeoutException:
            pass

    def show_test_networks(self):
        self.wait_window_loaded(
            '//*[@id="app-content"]/div/div[3]/div/div/div/div[2]/div/div[1]/div/div/div/div[1]/div')
        self.check_current_page(self.setting_advanced)
        try:
            status = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div[3]/div/div[2]/div[2]/div[2]/div[7]/div[2]/div/label/div[2]/span[2]')))
            visibility = status.value_of_css_property('visibility')
            if visibility == 'hidden':
                WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                    (By.XPATH,
                     '//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[2]/div[7]/div[2]/div/label'))).click()
        except TimeoutException:
            pass
        self.check_current_page(self.main_url)

    def check_network(self):
        self.wait_window_loaded(
            '//*[@id="app-content"]/div/div[3]/div/div/div/div[2]/div/div[1]/div/div/div/div[1]/div')
        try:
            network = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app-content"]/div/div[1]/div/div[2]/div/div/span'))).text
            self.current_network = network
        except TimeoutException:
            pass

    def switch_network(self, network):
        self.wait_window_loaded(
            '//*[@id="app-content"]/div/div[3]/div/div/div/div[2]/div/div[1]/div/div/div/div[1]/div')
        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app-content"]/div/div[1]/div/div[2]/div/div'))).click()
        except TimeoutException:
            print('switch_network: Button from to switch not found')

        try:
            items = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[2]')))
            networks = items.find_elements(By.CLASS_NAME, 'network-name-item')
            for element in networks:
                network_id = element.text
                if network_id == network:
                    element.click()
                    return
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div/div[3]/div/div/div/div[2]/div/div[1]/div/div/div/div[1]/div/span[2]'))).click()
            return 'Not Found network'
        except TimeoutException:
            print('switch_network: Button from to switch not found')

    def switch_page_to_action(self, title, function=None, *args):
        condition = True
        while condition:
            window_handles = self.driver.window_handles
            for page in window_handles:
                self.driver.switch_to.window(page)
                current_title = self.driver.title
                if current_title == title:
                    condition = False
                    break
        function(*args)
        window_handles = self.driver.window_handles
        self.driver.switch_to.window(window_handles[0])

    def connect_wallet(self):
        try:
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[3]/div[2]/button[2]'))).click()
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[2]/div[2]/div[2]/footer/button[2]'))).click()
        except TimeoutException:
            print('connect_wallet: Error Not Found Confirm Button')

    def confirm_wallet(self, button='//*[@id="app-content"]/div/div[2]/div/div[3]/div[3]/footer/button[2]'):
        try:
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, button))).click()
        except TimeoutException:
            print('connect_wallet: Error Not Found Confirm Button')

    def deposit_zk(self):
        gas = None
        max_amount = None
        try:
            gas = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[3]/div[2]/div/div/div[2]/div[2]/div[1]/div['
                           '1]/div/h6[2]/div/div/span[2]'))).text
        except TimeoutException:
            pass

        try:
            max_amount = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '//*[@id="app-content"]/div/div[2]/div/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/div[1]/div/h6[2]/div/div/span[2]'))).text
        except TimeoutException:
            pass
        if round(float(max_amount), 4) > round(float(self.balance), 4):
            self.difference = (round(float(self.balance) - float(gas), 3))
            try:
                WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                    (By.XPATH,
                     '//*[@id="app-content"]/div/div[2]/div/div[3]/div[4]/footer/button[1]'))).click()
            except TimeoutException:
                pass
            return

        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH,
                 '//*[@id="app-content"]/div/div[2]/div/div[3]/div[3]/footer/button[2]'))).click()
        except TimeoutException:
            pass

    def check_balance(self):
        time.sleep(1)
        try:
            self.balance = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div/div/div[2]/div/div[1]/div/div/div/div['
                           '1]/div/span[2]'))).text
        except TimeoutException:
            pass

    def close_modal(self, delay, element, exception=None):
        try:
            WebDriverWait(self.driver, delay).until(EC.presence_of_element_located(
                (By.XPATH, element))).click()
        except TimeoutException:
            if exception is None:
                pass

    def add_network_advanced(self, name, url, id, symbol, explorer):
        self.check_current_page(self.add_network_manual)
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[2]/div['
                           '1]/label/input'))).send_keys(name)
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[2]/div['
                           '2]/label/input'))).send_keys(url)
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[2]/div['
                           '3]/label/input'))).send_keys(id)
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[2]/div['
                           '4]/label/input'))).send_keys(symbol)
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[2]/div['
                           '5]/label/input'))).send_keys(explorer)
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[3]'
                           '/button[2]'))).click()
        except TimeoutException:
            print('MetaMask->add_network_advanced: Not Found Inputs')
        self.check_current_page(self.main_url)
