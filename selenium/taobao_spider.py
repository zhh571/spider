#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: ec
import re
import pymongo

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver import PhantomJS
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from urllib.parse import urljoin
from taobao.config_taobao import *

URL= 'https://www.taobao.com/'

client = pymongo.MongoClient(MONGO_URL, connect=False)
table = client[MONGO_DB][MONGO_TABLE]

# browser = Chrome()
browser = PhantomJS(desired_capabilities=Dcap, service_args=ARGS)    #参数配置在config.py中
browser.set_window_size(1400,900)

wait = WebDriverWait(browser,10)

def search():
    print('正在搜索...')
    try:
        browser.get(URL)
        #搜索框
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#q')))       #EC.presence_of_element_located()里面传入的是元组
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        input.send_keys(KEYWORD)
        submit.click()
        #共？页
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        pattern = re.compile('(\d+)')
        total = int(re.search(pattern,total.text).group(1))
        return total
    except TimeoutException:
        return search()

def next_page(page_number):
    print('正在打开%d页...' % page_number)
    try:
        #页码框
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()
        input.send_keys(page_number)
        submit.click()
        #等待页面高亮显示
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number)))
    except TimeoutException:
        return next_page(page_number)

def get_prodct_info():
    print('正在提取当前页产品信息...')
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
    doc = pq(browser.page_source)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product_info = {
            'shop': item('.shopname').text(),
            'title': item('.title').text().replace('\n', ' '),
            'price': item('.price').text().replace('¥\n', ' '),
            'deal': item('.deal-cnt').text()[:-3],
            'image': urljoin(URL,item('.pic .img').attr.src),
            'location': item('.location').text()
        }
        # print(product_info)
        save_to_mogo(product_info)


def save_to_mogo(product_info):
    try:
        if table.insert_one(product_info):
            print('存储到MONGODB成功～', product_info)
    except Exception:             #直接调用父类异常
        print('存储到MONGODB失败～', product_info)




def main():
    try:
        total = search()
        # print('正在打开1页...')
        # get_prodct_info()
        for i in range(1, total+1):
            next_page(i)
            get_prodct_info()
    except Exception as e:
        print(e)
    finally:
        browser.close()


if __name__ == '__main__':
    main()

