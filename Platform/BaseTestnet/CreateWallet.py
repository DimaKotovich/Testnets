from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import pyperclip
import string
import random
from selenium.webdriver.support.wait import WebDriverWait


class CreateWallet:
    def __init__(self, driver):
        self.backup_array = None
        self.password = None
        self.StepOne(driver)
        self.StepTwo(driver)
        self.generatePassword()
        self.StepThree(driver)

    def StepOne(self, driver):
        try:
            driver.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div/div/div/div/div/div/div/div/div[2]/div[2]/button[1]/div/div[2]/div/div/span'))).click()
        except:
            pass

        try:
            driver.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div/div/div/div/div/div/div/div/div[2]/div[2]/button[2]/div/p'))).click()
            copy = pyperclip.paste()
            self.backup_array = copy.split()
        except:
            pass

        try:
            driver.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div/div/div/div/div/div/div/div/div[2]/div[3]/div/label/div[1]/input'))).click()
        except:
            pass

        try:
            driver.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div/div/div/div/div/div/div/div/div[2]/div[3]/button'))).click()
        except:
            pass

    def StepTwo(self, driver):
        try:
            first_word = None
            second_word = None
            for index in range(0, 6):
                first = driver.wait.until(EC.presence_of_element_located(
                    (By.XPATH,
                     f'/html/body/div[1]/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[{index + 1}]/span[1]/div/button')))
                second = driver.wait.until(EC.presence_of_element_located(
                    (By.XPATH,
                     f'/html/body/div[1]/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div[{index + 1}]/span[2]/div/button')))
                if first.text == self.backup_array[0]:
                    first_word = first
                elif first.text == self.backup_array[-1]:
                    second_word = first
                if second.text == self.backup_array[0]:
                    first_word = second
                elif second.text == self.backup_array[-1]:
                    second_word = second
            first_word.click()
            second_word.click()
        except TimeoutException:
            print('No Words')
        try:
            driver.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[3]/button'))).click()
        except TimeoutException:
            pass


    def generatePassword(self):
        password = []

        for i in range(10):
            randomchar = random.choice(string.digits + string.ascii_letters + string.digits)
            password.append(randomchar)
        print("".join(password))
        self.password = "".join(password)
        print(self.backup_array)

    def StepThree(self, driver):
        try:
            password_input = driver.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div[1]/div[1]/div['
                 '1]/div/div/span/input')))
            verify_input = driver.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div[1]/div['
                 '2]/div/div/div/span/input')))
            password_input.send_keys(self.password)
            verify_input.send_keys(self.password)
            driver.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/label/div[1]/input'))).click()
            time.sleep(1)
            driver.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[1]/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div[2]'))).click()
        except TimeoutException:
            pass
