from Clients import Clients
from lxml import etree
from pandas.io.parsers import TextParser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re
import pickle
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

        fund_df=pd.DataFrame(fund_list,columns=['基金代码','基金名称','基金持仓'])
        print('爬取基金持仓信息完毕！')
        return fund_df






class DataAnalyser():
    def __init__(self,excel_path,pd_df):
        self.excel_writer = pd.ExcelWriter(excel_path, engine="xlsxwriter")
        self.excel_path = excel_path
        self.pd_df=pd_df
        self.processed_df=None
        self.total_asset_val=None

    def analysis(self):
        # 数据统计
        print('统计分析持仓数据.....')
        group = self.pd_df.groupby('基金代码').agg({'基金持仓': 'sum'})
        fund_name_with_code_df = self.pd_df.iloc[:, 0:2]
        grouped_fund_info = fund_name_with_code_df.merge(group, how='right', on='基金代码').drop_duplicates(subset=['基金代码'],keep='first')
        self.total_asset_val=grouped_fund_info['基金持仓'].sum()

        sorted_grouped_fund_info = grouped_fund_info.sort_values(by='基金持仓', ascending=False)  # 按持仓市值降序排列
        ratio = sorted_grouped_fund_info['基金持仓'] / self.total_asset_val  # 计算持仓比例
        ratio.rename('持仓占比', inplace=True)
        self.processed_df = pd.concat([sorted_grouped_fund_info, ratio], axis=1)  # 按列合并持仓占比信息
        self._save()

    def _save(self,startrow=0):
        sheet_name='且慢持仓汇总'
        rows, cols = self.processed_df.shape
        self.processed_df.to_excel(self.excel_writer,sheet_name=sheet_name,startrow=startrow,index=False,header=True)

        # 高亮显示账户总市值
        bold = self.excel_writer.book.add_format({
            'bold': True,  # 字体加粗
            'border': 1,  # 单元格边框宽度
            'align': 'right',  # 水平对齐方式
            'valign': 'vcenter',  # 垂直对齐方式
            'fg_color': '#F4B084',  # 单元格背景颜色
            'text_wrap': True,  # 是否自动换行
        })

        percent_format = self.excel_writer.book.add_format({'num_format': '0.00000%'}) #设置百分数格式
        worksheet = self.excel_writer.sheets[sheet_name]
        worksheet.set_column(2, 2, width=15)  # 设置表格宽度
        worksheet.set_column(3, 3, width=15, cell_format=percent_format)  # 设置百分数格式
        worksheet.set_column(1, 1, 30)  # 设置基金名称表格宽度
        worksheet.write(startrow + rows + 1, 1, '账户持仓总市值', bold)
        worksheet.write(startrow + rows + 1, 2, self.total_asset_val, bold)

        self.excel_writer.save()




if __name__=='__main__':
    #账户信息
    home_url = 'https://qieman.com/'
    user_name = 'xxxxxxx'
    passwd = 'xxxxxx'

    qieman=QiemanClient(headless=True,home_url=home_url,user_name=user_name,passwd=passwd)
    qieman.login()
    fund_df=qieman.getAssets()#获取基金持仓信息

    #with open('fund_df.pkl','wb') as df_data_file:
    #    pickle.dump(fund_df,df_data_file)

    # with open('fund_df.pkl','rb') as df_data_file:
    #     fund_df=pickle.load(df_data_file)

    data_analyser=DataAnalyser('且慢基金持仓v7.xlsx',fund_df)
    data_analyser.analysis()

    print('Done!')
