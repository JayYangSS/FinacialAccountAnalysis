# 账户统计说明

这个repo的初衷，是由于自己的基金，股票账户太多，没次统计都要挨个账户打开，
手动统计分散在不同账户的资产，太麻烦了，效率也太低了，因此开发了这个工具，用来自动登录
各个账户，爬取账户信息，进行自动统计和分析。


# 使用说明

### 依赖库安装
- 安装程序运行所需的依赖库：
```bash
pip install -r requirements.txt 
```

- 安装操作chrome所需的chromedriver，首先查看本地的chrome浏览器的版本(在浏览器右侧设置->关于chrome中)

在如下地址中，选择对应版本和对应平台的chromedriver进行下载：
>http://chromedriver.storage.googleapis.com/index.html


### 启动程序
- chromedriver下载完成后，在`Clients.py`中line21 将`executable_path`修改为chromedriver路径


#### 账户分析
- 易方达账户分析：修改efounds_client.py文件中的账户名和密码，直接运行即可得到分散在各个账户中的易方达基金的持仓信息
```python
python efounds_client.py
```

- 且慢账户分析：修改qieman_client.py文件中的账户名和密码，直接运行
```python
python qieman_client.py
```
运行上述程序后，会生成excel文件。
其他账户的分析待继续开发。



# TODO
- [x] 易方达账户信息统计
- [x] 且慢账户信息统计
- [ ] 广发账户信息统计

 