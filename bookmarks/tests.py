from django.test import TestCase
from django.test.client import Client


class ViewTest(TestCase):
    fixtures = ['test_data.json']
    def setUp(self):
        self.client = Client()

    def test_register_page(self):
        data = {
            'username': 'Pablo',
            'email': 'Badman@gmail.com',
            'password1': 'Badass',
            'password2' : 'Badass',     
        }
        response = self.client.post('/register/', data)
        self.assertEqual(response.status_code, 302)
        
        
    def test_bookmark_save(self):
        c = Client()
        response = c.post('/save/',{'username': 'Storm', 'password': 'Badass'})
        self.assertTrue(response)
        data = {
            'url': 'http://www.example.com/',
            'title': 'Test URL',
            'tags': 'test-tag',
        }
        response = self.client.post('/save/', data)
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/user/Storm/')
        self.assertTrue("http://www.example.com/" in response.content)
        self.assertTrue("Test URL" in response.content)
        self.assertTrue("test-tag" in response.content)
        
























# from urllib import response
# from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# from selenium.webdriver.common.by import By
# from selenium import webdriver
# from django.test import LiveServerTestCase
# from selenium.webdriver.common.keys import Keys
# import time


# class Hottest(LiveServerTestCase):

#     def testhomepage(self):
#         driver = webdriver.Chrome(executable_path=r"chromedriver.exe")


#         driver.get('http://127.0.0.1:8000/')
#         assert "Welcome to Django Bookmarks" in driver.title

    
# class LoginFormTest(LiveServerTestCase):

#     def testform(self):

#         driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
#         driver.get('http://localhost:8000/login/')

#         time.sleep(5)


#         user_name = driver.find_element('name','username')
#         user_password = driver.find_element('name','password')

#         time.sleep(5)

#         submit = driver.find_element('name','continue')


#         time.sleep(10)
        

#         user_name.send_keys('Storm')
#         user_password.send_keys('Badass')
        
#         submit.send_keys(Keys.RETURN)


#         assert 'admin' in driver.page_source