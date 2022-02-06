from Clients import Clients
from lxml import etree
from pandas.io.parsers import TextParser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re
import requests



class QiemanClient(Clients):
    def __init__(self,home_url,user_name,passwd,headless=True):
        super(QiemanClient,self).__init__(headless,home_url,user_name,passwd)


    def login(self):

        self.browser.get(self.home_url)
        self.browser.implicitly_wait(10)


        login_botton=self.browser.find_element(By.XPATH,'//*[@id="app"]/div[4]/div/div[3]/button')
        login_botton.click()

        passwd_login = self.browser.find_element(By.XPATH, '//*[@id="app"]/div[4]/main/div/div/div/form/div[3]/a[1]')
        passwd_login.click()

        #提交登录信息
        account_name=self.browser.find_element(By.ID,"phone")
        account_name.clear()
        account_name.send_keys(self.user_name)

        password = self.browser.find_element(By.ID, "password")
        password.clear()
        password.send_keys(self.passwd)

        #勾选确认协议
        check_btn=self.browser.find_element(By.XPATH,'//*[@id="app"]/div[4]/main/div/div/div/form/div[4]/label/span/span')
        check_btn.click()

        # 提交登录信息
        submit_botton = self.browser.find_element(By.XPATH, '//*[@id="app"]/div[4]/main/div/div/div/form/div[5]/button')
        submit_botton.click()
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'assets')))  # 页面加载出来总资产项后再继续执行
        print('logging account sucessful!')

    #检查该element是否为一个基金连接element
    def _check_fund_element(self,element):
        fund_url=element.get_attribute('href')
        if fund_url is None:return False
        #match_result=re.search(r"funds/\d{6}",fund_url)
        match_result = re.search(r"/\d{6}$", fund_url)
        return True if match_result else False

    def getStrategyInfo(self,fund_list):
        funds_elements_xpath = '//*[@id="app"]/div[4]/main/div/div/div'
        time.sleep(2)#强制等待2s
        #WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, funds_elements_xpath)))
        selected_elements = self.browser.find_element(By.XPATH, funds_elements_xpath).find_elements(By.TAG_NAME, 'a')

        funds_elements=[element for element in selected_elements if self._check_fund_element(element)]

        for fund in funds_elements:
            fund_infos = fund.text.split('\n')
            fund_url = fund.get_attribute('href')
            fund_code = fund_url.split('/')[-1]  # 获取基金代码
            fund_name = fund_infos[0]  # 获取基金名称

            chicang_info=''
            for fund_info in fund_infos:
                if fund_info.__contains__('持仓'):
                    chicang_info=fund_info
                    break

            print('基金名称:{}:{}'.format(fund_name,chicang_info))
            fund_val = re.findall(r"\d+\,?\d*\.?\d*", chicang_info)[0].replace(',', '')
            fund_list.append([fund_code, fund_name, float(fund_val)])


    def getChangyingStrategyInfo(self,fund_list):
        funds_elements_xpath = '//*[@id="app"]/div[4]/main/div/div/div/div[4]'
        time.sleep(2)#强制等待2s
        #WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, funds_elements_xpath)))
        fund_locator=(By.CSS_SELECTOR, "[class='sc-18axhri-5 u2shye-1 htsKsn dZoxFt section-with-link section__f1726']")
        selected_elements = self.browser.find_element(By.XPATH, funds_elements_xpath).find_elements(fund_locator[0],fund_locator[1])

        #funds_elements=[element for element in selected_elements if self._check_fund_element(element)]

        for fund_id in range(len(selected_elements)):
            if fund_id>0:
                selected_elements = self.browser.find_element(By.XPATH, funds_elements_xpath).find_elements(fund_locator[0], fund_locator[1])

            fund=selected_elements[fund_id]
            fund.click()
            amount_locator=(By.CSS_SELECTOR,"[class='qm-amount qm-amount-sm']")
            fund_name_locator=(By.CSS_SELECTOR,"[class='qm-link qm-link-external qm-link-sm']")
            time.sleep(0.5)
            #WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(fund_name_locator))
            #WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(amount_locator))

            fund_name_with_code=self.browser.find_element(fund_name_locator[0],fund_name_locator[1]).text
            start,end=re.search(r"\d{6}",fund_name_with_code).span()#匹配基金代码
            fund_code=fund_name_with_code[start:end]# 获取基金代码
            fund_name=fund_name_with_code[:start-1]# 获取基金名称

            chicang_info = self.browser.find_element(amount_locator[0],amount_locator[1]).text


            print('基金名称:{}:{}'.format(fund_name,chicang_info))
            fund_val = chicang_info.replace(',', '')
            fund_list.append([fund_code, fund_name, float(fund_val)])
            self.browser.back()
            time.sleep(0.5)

    def getAssets(self):

        self.browser.find_element(By.XPATH,'//*[@id="app"]/div[4]/div/div[2]/div/section/a').click()
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[4]/main/div/div/div/div[3]')))

        #获取投资账户信息
        asset_all=self.browser.find_element(By.XPATH, '//*[@id="app"]/div[4]/main/div/div/div/div[3]')
        asset_elements=asset_all.find_elements(By.TAG_NAME,'a')[1:] #第一个元素为账户管理的element

        #访问每个子账户
        fund_list = []
        for asset_id in range(len(asset_elements)):
            if asset_id>0:#第一次可以复用
                asset_all = self.browser.find_element(By.XPATH, '//*[@id="app"]/div[4]/main/div/div/div/div[3]')
                asset_elements = asset_all.find_elements(By.TAG_NAME, 'a')[1:]  # 第一个元素为账户管理的element
            asset_element=asset_elements[asset_id]
            asset_name=asset_element.find_element(By.CLASS_NAME,'medium-font').text
            print('++++++++++++++++++++++++{}+++++++++++++++++++++++++'.format(asset_name))
            asset_element.click()
            time.sleep(1)
            #WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[4]/div/main/div/div/div/div[3]/div[1]')))

            #定位子账户中的策略
            strategy_elements=self.browser.find_elements(By.CLASS_NAME,'ant-spin-container')
            #for strategy_element in strategy_elements:
            for strategy_id in range(len(strategy_elements)):
                if strategy_id>0:#第一次可以复用
                    strategy_elements = self.browser.find_elements(By.CLASS_NAME, 'ant-spin-container')
                stragegy_element=strategy_elements[strategy_id].find_element(By.CLASS_NAME,'medium-font')

                stragegy_name=stragegy_element.text
                stragegy_element.click()

                if stragegy_name.__contains__('长赢'):
                    #TODO:长赢计划页面与普通页面不同
                    print('=================={}处理中=================='.format(stragegy_name))
                    self.getChangyingStrategyInfo(fund_list)
                else:
                    # 获取策略中的基金持仓信息
                    print('=================={}================='.format(stragegy_name))
                    self.getStrategyInfo(fund_list)

                self.browser.back()#回退到策略页面
                time.sleep(0.5)  # 强制等待
                #WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ant-spin-container')))

            self.browser.back()#回退到账户页面
            time.sleep(1)#强制等待
            #WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, 'app')))

        fund_df=pd.DataFrame(fund_list,columns=['基金代码','基金名称','基金持仓'],dtype=float)

        return fund_df






class DataAnalyser():
    def __init__(self,excel_path):
        self.excel_writer = pd.ExcelWriter(excel_path, engine="xlsxwriter")
        self.excel_path = excel_path


    def save(self,data_frame,startrow=0):
        data_frame.to_excel(self.excel_writer,startrow=startrow,index=False,header=True)
        self.excel_writer.save()




if __name__=='__main__':
    html_save_path='efounds.html'#爬取的数据信息
    excel_save_path='账户持仓.xlsx'

    #账户信息
    home_url = 'https://qieman.com/'
    user_name = 'xxxxx'
    passwd = 'xxxxxxx'

    qieman=QiemanClient(headless=False,home_url=home_url,user_name=user_name,passwd=passwd)
    qieman.login()
    fund_df=qieman.getAssets()#获取基金持仓信息


    #数据存储
    data_analyser=DataAnalyser('且慢基金持仓.xlsx')
    data_analyser.save(fund_df)

    #数据加载
    #fund_df=pd.read_excel('且慢基金持仓.xlsx')
    #group=fund_df.groupby('基金代码').agg({'基金持仓':'sum'})

    #data_analyser=DataAnalyser('且慢基金持仓v2.xlsx')
    #data_analyser.save(group)


    print('Done!')
