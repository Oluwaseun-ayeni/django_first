from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium import webdriver
from django.test import LiveServerTestCase
from selenium.webdriver.common.keys import Keys
import time


class Hottest(LiveServerTestCase):

    def testhomepage(self):
        driver = webdriver.Chrome(executable_path=r"chromedriver.exe")


        driver.get('http://127.0.0.1:8000/')
        assert "Welcome to Django Bookmarks" in driver.title

    
class LoginFormTest(LiveServerTestCase):

    def testform(self):

        driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
        driver.get('http://localhost:8000/login/')

        time.sleep(5)


        user_name = driver.find_element('name','username')
        user_password = driver.find_element('name','password')

        time.sleep(5)

        submit = driver.find_element('name','continue')


        time.sleep(10)
        

        user_name.send_keys('Storm')
        user_password.send_keys('Tempete001')
        
        submit.send_keys(Keys.RETURN)


        assert 'admin' in driver.page_source



        



