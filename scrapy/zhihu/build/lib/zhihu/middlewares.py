# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from scrapy.http import HtmlResponse   #直接返回response，不需要downloader取下载
import re
import time
import logging

class JSPageDownloaderMiddleware(object):

    logger = logging.getLogger(__name__)

    def process_request(self, request, spider):
        if re.search('activities$', request.url):
            try:
                self.logger.info("vist %s using JS" % request.url)

                browser = webdriver.PhantomJS()       #不会share settings的参数设置
                browser.set_window_size(1400, 900)
                wait = WebDriverWait(browser, 5)
                browser.get(request.url)
                button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.ProfileHeader-expandButton')))     #有时候是没有这些元素的，只能等待超时
                button.click()
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.RichText:nth-child(2)")))
                # time.sleep(5)

                return HtmlResponse(url=browser.current_url, body=browser.page_source, encoding="utf-8", request=request)
            except TimeoutException:
                return HtmlResponse(url=browser.current_url, body=browser.page_source, encoding="utf-8", request=request) #超时也必须返回数据，否则callback没有意义
                self.logger.warning("visit failed: " %request.url)









