#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: ec

import requests
import re
import json
import pymongo
import os
import time
from requests.exceptions import RequestException
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from hashlib import md5
from multiprocessing import Pool
from config import *

#定义数据库
client = pymongo.MongoClient(IP, PORT, connect=False)
db = client[DB]

#定义spider头部


def open_url(url,encode=None,imgurl=False):    #
    '''定义网址打开方法'''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        # 'cookie': 'tt_webid=6540111108701783555; tt_webid=6540111108701783555; UM_distinctid=1628a46336e8b-0065ce3227e84b-3a614f0b-1fa400-1628a46336f350; uuid="w:d051a9241b924af08300c5bc3beafac6"; tt_webid=6540111108701783555; __tasessionId=fbxbmonsj1522771889642; CNZZDATA1259612802=184026154-1522734534-%7C1522772334'
    }

    if encode == None:
        response = requests.get(url, headers=headers)
    else:
        response = requests.get(url + urlencode(encode), headers=headers)
    try:
        if response.status_code == 200 and imgurl == False:
            return response.text
        elif response.status_code == 200 and imgurl == True:
            return response.content
            # save_images(response.content)                     #jpg download & save
            # print('%s 下载完成..' % url)
        return None
    except RequestException:
        print('请求失败..')
        return None

def page_index_setting(offset,keyword):
    '''POST的请求参数'''
    data = {
            'offset': offset,
            'format': 'json',
            'keyword': keyword,
            'autoload': 'true',
            'count': '20',
            'cur_tab': '3',
            'from':'gallery',
        }
    return data

def parse_page_index(html):
    '''获取详情页的URL'''
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            if item.get('article_url').startswith('http://toutiao.com'):
                yield item.get('article_url')

def get_pic_url(url):
    '''提取出图片地址'''
    # print(url)
    html = open_url(url.strip())                 #fuck
    soup = BeautifulSoup(html,'lxml')
    title = soup.title.string
    images_pattern = re.compile('gallery: JSON.parse\("(.*?)"\),',re.S)
    result = re.search(images_pattern,html).group(1).replace('\\','')
    url_pattern = re.compile('"url_list":\[{"url":"(.*?)"},',re.S)
    url_result = re.findall(url_pattern,result)
    # for imgurl in url_result:
    #     open_url(imgurl,imgurl=True)         # jpg download & save

    return {
        'title':title,
        'images':url_result,
        'url':url
    }

def save_to_mongo(result):
    '''存储到数据库'''
    if db[TABLE].insert(result):
        return True
    return False

def save_images(content, url):
    '''保存图片'''
    if os.path.exists(os.getcwd() + '/images'):
        file_path = '{0}/images/{1}.{2}'.format(os.getcwd(),md5(content).hexdigest(),'jpg')
    else:
        os.mkdir(os.getcwd() + '/images')
        file_path = '{0}/images/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')

    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            print('%s 下载完成..' % url)

def main(offset):
    jsondata = open_url(url='https://www.toutiao.com/search_content/?',encode=page_index_setting(offset,KEYWORD))
    for picurl in parse_page_index(jsondata):
        # print(picurl)
        data = get_pic_url(picurl)
        for url in data['images']:
            content = open_url(url, imgurl=True)
            save_images(content,url)
        save_to_mongo(data)


if __name__ == '__main__':
    # main(0)
    groups = [x*20 for x in range(GROUP_START,GROUP_STOP + 1)]
    pool = Pool()
    pool.map(main,groups)