import time
import pandas as pd
import requests
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class MesProtocol:
    def __init__(self, driver, wallet):
        self.main_url = 'https://testnet.mesprotocol.com/spot/ETH-USDC'
        self.driver = driver
        self.wallet = wallet
        self.wallet.check_current_page(self.main_url)
        self.wallet.wait_window_loaded('//*[@id="app"]/div[3]/div/div[1]/div[1]/div[1]/div/div', 20)
        self.close_modal()
        self.connect_wallet()
        self.balance_usdc = 0
        self.balance_eth = 0
        # self.wallet.switch_page_to_action(
        #     'MetaMask',
        #     self.wallet.add_network_advanced,
        #     'zkSync Alpha Testnet',
        #     'https://zksync2-testnet.zksync.dev',
        #     '280',
        #     'ETH',
        #     'https://scan-v2.zksync.dev'
        # )
        self.wallet.switch_page_to_action('MetaMask', self.wallet.switch_network, self.wallet.zkSync_network)
        self.wallet.switch_page_to_action('MetaMask', self.wallet.check_balance)
        self.check_balance()
        print(self.balance_eth)
        if float(self.balance_eth) > 0:
            self.sell()
        # self.deposit()
        # self.wallet.switch_page_to_action('MetaMask Notification', self.wallet.deposit_zk)
        # if self.wallet.difference is not None:
        #     self.deposit(replay=True)
        #     self.wallet.switch_page_to_action('MetaMask Notification', self.wallet.deposit_zk)

    def close_modal(self):
        try:
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="react-joyride-step-0"]/div/div/div/div[2]/div/button'))).click()
        except TimeoutException:
            print('MesProtocol->close_modal: Modal Close')

    def connect_wallet(self):
        try:
            self.driver.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="app"]/div[3]/div/div[1]/div[2]/div[3]/button'))).click()
            try:
                self.driver.execute_script("""return document.querySelector("onboard-v2").shadowRoot.querySelector(
                            '.wallet-button-styling')""").click()
                if not self.wallet.session_login:
                    self.wallet.switch_page_to_action('MetaMask Notification', self.wallet.login_password)
                self.wallet.switch_page_to_action('MetaMask Notification', self.wallet.connect_wallet)
            except:
                pass
        except TimeoutException:
            pass

    def deposit(self, replay=None):
        try:
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[1]/div[5]/div[4]/div/div[1]/button[2]'))).click()
            time.sleep(1)
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[1]/div[5]/div[4]/div/div[2]/div[2]/div/div[1]/div/button[1]'))).click()
            if replay is not None:
                input = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/div[1]/div[5]/div[4]/div/div[2]/div[2]/div/div[2]/div[1]/div/div[1]/input')))
                input.clear()
                input.send_keys(str(self.wallet.difference))
            else:
                WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                    (By.XPATH,
                     '/html/body/div[1]/div[5]/div[4]/div/div[2]/div[2]/div/div[2]/div[1]/div/div[1]/div/button'))).click()
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[1]/div[5]/div[4]/div/div[2]/div[2]/div/div[2]/div[1]/div/button[1]'))).click()
            time.sleep(2)
        except TimeoutException:
            print('MesProtocol->deposit: Not Found button to deposit')

    def check_balance(self):
        try:
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[1]/div[5]/div[4]/div/div[1]/button[1]'))).click()
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div[5]/div[4]/div/div[2]/div[1]/div/form/div[1]/div/div/div[1]/label'))).click()
            self.balance_usdc = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div[5]/div[4]/div/div[2]/div[1]/div/form/div[3]/div/p/b'))).text
        except TimeoutException:
            pass

        try:
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[1]/div[5]/div[4]/div/div[1]/button[1]'))).click()
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[1]/div[5]/div[4]/div/div[2]/div[1]/div/form/div[1]/div/div/div[2]/label'))).click()
            self.balance_eth = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div[5]/div[4]/div/div[2]/div[1]/div/form/div[3]/div/p/b'))).text
        except TimeoutException:
            pass

    def confirm_offer(self):
        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div/div[2]/div/div[3]/div[1]'))).click()
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[1]/div/div[2]/div/div[4]/button[2]'))).click()
        except TimeoutException:
            pass

    def sell(self):
        try:
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '/html/body/div[1]/div[5]/div[4]/div/div[2]/div[1]/div/form/div[1]/div/div/div[2]/label'))).click()
            Quantity = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div[5]/div[4]/div/div[2]/div[1]/div/form/div[5]/div/div[1]/button')))
            if Quantity.text != 'Quantity':
                Quantity.click()
                try:
                    WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                        (By.XPATH,
                         '/html/body/div[1]/div[5]/div[4]/div/div[2]/div[1]/div/form/div[5]/div/div['
                         '1]/div/div/div/button[1]'))).click()
                except TimeoutException:
                    pass
        except TimeoutException:
            pass

        try:
            input = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="field-:r1r:"]')))
            input.clear()
            input.send_keys(self.balance_eth)
        except TimeoutException:
            pass

        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div[5]/div[3]/div/div[2]/div[12]/div[2]/div[1]'))).click()
        except TimeoutException:
            pass

        try:
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[1]/div[5]/div[4]/div/div[2]/div[1]/div/form/button'))).click()
            time.sleep(2)
            self.wallet.switch_page_to_action('MetaMask Notification', self.confirm_offer)
        except TimeoutException:
            pass
