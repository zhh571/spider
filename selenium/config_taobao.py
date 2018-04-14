#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: ec

#搜索关键字
KEYWORD = '电子书'

#MongoDB配置信息
MONGO_URL = 'localhost'
MONGO_DB = 'taobao'
MONGO_TABLE = 'product_' + KEYWORD

#phantomJS配置信息
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
Dcap = dict(DesiredCapabilities.PHANTOMJS)
Dcap['phantomjs.page.settings.userAgent'] = ('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36')

ARGS = ['--load-images=false' ]

