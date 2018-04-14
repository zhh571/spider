#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: ec


from scrapy.cmdline import execute

import sys
import os

sys.path.append((os.path.dirname(os.path.abspath(__file__))))  # 注意没有main函数时，将这个加到setting文件中，这个是最早初始化入口
# sys.path.insert(0,(os.path.dirname(os.path.abspath(__file__))))

execute(["scrapy", "crawl", "zhihu"])
