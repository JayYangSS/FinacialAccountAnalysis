from Clients import Clients
from lxml import etree
from pandas.io.parsers import TextParser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd



class EfoundsClient(Clients):
    def __init__(self,home_url,user_name,passwd,headless=True):
        super(EfoundsClient,self).__init__(headless,home_url,user_name,passwd)


    def login(self):

        self.browser.get(self.home_url)
        self.browser.implicitly_wait(10)

        user_name_botton=self.browser.find_element(By.ID,"certID")
        user_name_botton.clear()
        user_name_botton.send_keys(self.user_name)

        password_botton=self.browser.find_element(By.ID,"tradepassword")
        password_botton.clear()
        password_botton.send_keys(self.passwd)

        #提交登录信息
        submit_botton=self.browser.find_element(By.ID,"submitBtn")
        submit_botton.click()
        self.browser.implicitly_wait(5)  # 防止页面未加载出来就执行下一步操作
        print('logging account sucessful!')

    def getAccountHTML(self,html_save_path):
        #进入交易记录页面
        WebDriverWait(self.browser,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="m-header-nav"]/div/ul/li[6]/a')))
        trade_record_link=self.browser.find_element(By.XPATH,'//*[@id="m-header-nav"]/div/ul/li[6]/a')
        trade_record_link.click()

        #进入电子对账单
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/ul/li[2]/a')))
        trade_statement_link = self.browser.find_element(By.XPATH,'//*[@id="main"]/div/ul/li[2]/a')
        trade_statement_link.click()


        #查询持仓信息
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="statementsCommit"]')))
        trade_search_link = self.browser.find_element(By.XPATH,'//*[@id="statementsCommit"]')
        trade_search_link.click()
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, '//table'))) # 防止页面未加载出来就执行下一步操作

        #保存html页面
        with open(html_save_path,'w',encoding='utf-8') as f:
           f.write(self.browser.page_source)
        print('get HTML content sucessfully!')




class HTMLTableParser():
    def __init__(self,html_path,excel_path):
        parser = etree.HTMLParser(encoding='utf-8')
        self.tree = etree.parse(html_path, parser=parser)
        self.excel_writer = pd.ExcelWriter(excel_path, engine="xlsxwriter")
        self.excel_path=excel_path

    #若位数字，处理提取数值
    def _process_str(self,s):
        s=s.replace(",", "")
        try:  # 如果能运行float(s)语句，返回True（字符串s是浮点数）
            return float(s)
        except ValueError:  # ValueError为Python的一种标准异常，表示"传入无效的参数"
            return s  # 如果引发了ValueError这种异常，不做任何事情（pass：不做任何事情，一般用做占位语句）


    def _unpack(self,row, kind='td'):
        elts = row.xpath('.//%s' % kind)
        return [self._process_str(val.text) for val in elts]


    def parseAccountInfo(self):
        account_table=self.tree.xpath('//table')[0]
        rows = account_table.xpath('.//tr')
        header = self._unpack(rows[0], kind='th')
        data = [self._unpack(r) for r in rows[1:]]
        data_frame = TextParser(data, names=header).get_chunk()

        group=data_frame.groupby(u'销售机构')

        startrow=0
        sheet_name = u'账户持仓易方达基金统计'


        for account,info in group:

            #获取每支基金的持仓市值
            info.to_excel(self.excel_writer,sheet_name=sheet_name,startrow=startrow,index=False,header=True)
            account_sum = info[u'参考市值'].sum()  # 获取该账户持仓基金总和
            rows,cols=info.shape

            #高亮显示账户总市值
            bold = self.excel_writer.book.add_format({
                'bold': True,  # 字体加粗
                'border': 1,  # 单元格边框宽度
                'align': 'right',  # 水平对齐方式
                'valign': 'vcenter',  # 垂直对齐方式
                'fg_color': '#F4B084',  # 单元格背景颜色
                'text_wrap': True,  # 是否自动换行
            })
            worksheet = self.excel_writer.sheets[sheet_name]
            worksheet.set_column(cols - 2,cols-1,22)#设置表格宽度
            worksheet.set_column(0, 0, 40)  # 设置基金名称表格宽度
            worksheet.write(startrow + rows + 1, cols - 2, '{}账户持仓总市值'.format(account), bold)
            worksheet.write(startrow+rows+1,cols-1,account_sum,bold)
            startrow+=rows+4

            print('{}账户持仓总市值:{}'.format(account,account_sum))#.sum(axis=1))

        self.excel_writer.save()
        return data_frame







if __name__=='__main__':
    html_save_path='efounds.html'#爬取的数据信息
    excel_save_path='账户持仓.xlsx'

    #账户信息
    home_url = 'https://e.efunds.com.cn/'
    user_name = 'xxxxxxxx'
    passwd = 'xxxxxxxx'

    efounds=EfoundsClient(headless=True,home_url=home_url,user_name=user_name,passwd=passwd)
    efounds.login()
    account_info=efounds.getAccountHTML(html_save_path=html_save_path)
    html_parser=HTMLTableParser(html_path=html_save_path,excel_path=excel_save_path)
    html_parser.parseAccountInfo()


    print('Done!')
