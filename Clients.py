from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ChromeOptions #规避服务器检测


"""账户管理基类"""
class Clients():
    def __init__(self,headless=True,home_url=None,user_name=None,passwd=None):

        #实现规避检测
        option=ChromeOptions()
        option.add_experimental_option('excludeSwitches',['enable-automation'])
        self.home_url=home_url
        self.user_name=user_name
        self.passwd=passwd

        if headless:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头浏览器，不显示浏览器操作界面
            chrome_options.add_argument('--disable-gpu')
            self.browser = webdriver.Chrome(executable_path='/Users/jayn/Applications/chromedriver',
                                            options=option,
                                            chrome_options=chrome_options)
        else:
            self.browser=webdriver.Chrome(executable_path='/Users/jayn/Applications/chromedriver',
                                          options=option)

    def login(self):
        pass