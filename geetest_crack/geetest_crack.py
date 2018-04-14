#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: ec

from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from urllib.request import urlretrieve
from selenium import webdriver
from bs4 import BeautifulSoup
import PIL.Image as image
import time
import random
from PIL import Image
from io import BytesIO

#http://cuijiahua.com/blog/2017/11/spider_2_geetest.html
#PIL库操作
#https://blog.csdn.net/dimkang/article/details/78149127
#https://blog.csdn.net/mingzznet/article/details/54288288 轨迹操作
#https://www.urlteam.org/2016/09/%E7%A0%B4%E8%A7%A3%E6%9F%90%E6%BB%91%E5%8A%A8%E8%A1%8C%E4%B8%BA%E9%AA%8C%E8%AF%81%E9%AA%8C%E8%AF%81%E7%A0%81/

class Crack():
    def __init__(self):
        self.url = 'https://account.geetest.com/register'  #'http://gd.gsxt.gov.cn/index.html'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 10)
        self.email = 'zxde@163.com'
        self.BORDER = 6

    def open(self):
        """
        打开浏览器,并输入查询内容
        """
        self.browser.get(self.url)
        keyword = self.wait.until(EC.presence_of_element_located((By.ID, 'email')))
        bowton = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_radar_tip_content')))
        keyword.send_keys(self.email)
        bowton.click()
        try:
            button = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_slider_button'))) #滑动条
            img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_img')))  # 滑动条
            time.sleep(5)
            image1 = self.get_image(img)
            image1.save("001.jpg")
            button.click()
            time.sleep(5)
            image2 = self.get_image(img)
            image2.save("002.jpg")

            top, bottom, left, right = self.get_position(button)
            left = right -left

            # print("button size", right - left)
            return (image1, image2, left)
        except TimeoutException:
            print('未出现验证码')
            return None

    def get_position(self,obj):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        location = obj.location
        size = obj.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        print("快照")
        return screenshot

    def get_image(self, obj): #内部调用 get_position+get_screenshot 扣图
        """
        获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position(obj)
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        image = screenshot.crop((left, top, right, bottom))
        return image



    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 20
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def get_gap(self, img1, img2, left):
        """
        获取缺口偏移量
        :param img1: 不带缺口图片
        :param img2: 带缺口图片
        :return:
        """
        # count = 2
        # left = 60     # 滑块宽度，不计算滑块这一边（左边）,镂空前还有障碍阴影gap会出错，同时行为轨迹也有问题，老是被吃掉
        for i in range(left, img1.size[0]):
            for j in range(img1.size[1]):
                if not self.is_pixel_equal(img1, img2, i, j):
                    left = i
                    return left
        return left

    def get_track(self, distance):           # 这个需要改写
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        tracks = []

        #   间隔通过随机范围函数来获得
        x = random.randint(1, 3)

        while distance - x >= 5:
            tracks.append(x)

            distance = distance - x
            x = random.randint(1, 3)

        for i in range(distance):
            tracks.append(1)

        return tracks


    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        while True:
            try:
                slider = self.browser.find_element_by_css_selector('.geetest_slider_button')
                break
            except:
                time.sleep(0.5)
        return slider

    def move_to_gap(self, slider, tracks):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        for track in tracks:
            ActionChains(self.browser).move_by_offset(xoffset=track, yoffset=0).perform()
            time.sleep(0.1)
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()

    def crack(self):
        image1, image2, left = self.open()
        if image1:
            gap = self.get_gap(image1,image2, left)
            print('gap, left', gap, left)
            track = self.get_track(gap - self.BORDER)     #
            print('滑动滑块')
            print(track)
        # 点按呼出缺口
            slider = self.get_slider()
        # 拖动滑块到缺口处
            self.move_to_gap(slider, track)


if __name__ == '__main__':
    print('开始验证')
    crack = Crack()
    crack.crack()
    # print('验证成功')