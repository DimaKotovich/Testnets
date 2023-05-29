import time
import pandas as pd
import requests
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Bridge:
    def __init__(self, driver, wallet):
        self.bridge_url = 'https://goerli.portal.zksync.io/bridge'
        self.driver = driver
        self.wallet = wallet
        self.wallet.check_current_page(self.bridge_url)
        self.connect_wallet()
        if float(self.wallet.balance) <= 0:
            print('Недостаточно тестового ефіру')
            return
        self.deposit()

    def connect_wallet(self):
        try:
            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app"]/section/div[2]/button'))).click()
            try:
                WebDriverWait(self.driver, 2).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]')))
            except TimeoutException:
                if not self.wallet.session_login:
                    self.wallet.switch_page_to_action('MetaMask Notification', self.wallet.login_password)
                self.wallet.switch_page_to_action('MetaMask Notification', self.wallet.connect_wallet)
        except TimeoutException:
            pass

    def deposit(self):
        try:
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/main/div/div/section/div[2]/div/form/div[1]/div[2]/div['
                           '2]/div/button'))).click()
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/main/div/div/section/div[2]/div/form/button[3]'))).click()
            time.sleep(1)
            self.wallet.switch_page_to_action('MetaMask Notification', self.confirm_deposit)
            self.check_transaction()
        except TimeoutException:
            print('Кнопка не клікабельна')

    def confirm_deposit(self):
        try:
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[3]/div[3]/footer/button[2]'))).click()
        except TimeoutException:
            pass

    def check_transaction(self):
        try:
            WebDriverWait(self.driver, 50).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/main/div/div/section/div[2]/div/div/div[1]/div[2]/h3')))
        except TimeoutException:
            pass
