# -*- coding: utf-8 -*-
import json
import logging
import re
from scrapy import Spider, Request
from zhihu.items import UserItem_json, UserItem_page


#www.zhihu.com/people/excited-vczh/answers

class ZhihuSpider(Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    logger = logging.getLogger(__name__)

    user_page = "https://www.zhihu.com/people/{user}/activities"  #用户信息page抓取
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'  #用户部分信息json
    followees_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}' #关注的人
    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}' #粉丝

    start_user = 'excited-vczh'

    user_include = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'
    follows_include = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        yield Request(self.user_url.format(user=self.start_user, include=self.user_include),
                      callback=self.parse_user_json)

    def parse_user_page(self, response):
        item = UserItem_page()
        result = re.search('people/(.*?)/', response.url)
        if result:
            url_token = result.group(1)
        else:
            self.logger.warning("could not get url_token: ", response.url)
        locations = response.css("div.ProfileHeader-detailItem:nth-child(1) > div:nth-child(2) > span:nth-child(1)::text").extract()
        educations = response.css(".ProfileHeader-field::text").extract_first()
        description = "".join(response.css("div.RichText:nth-child(2)::text").extract())
        question_count = response.css("#ProfileMain > div.ProfileMain-header > ul > li:nth-child(3) > a > span::text").extract_first()

        pattern = re.compile("获得.*?<!-- /react-text --><!--.*?-->(.*?)<!--.*?次赞同", re.S)   #获得.*?-->(.*?)<!--.*?次赞同
        vote_from_count = re.search(pattern,response.text).group(1)

        thank_from_count = response.css(".Profile-sideColumnItemValue::text").extract() #div.Profile-sideColumnItem:nth-child(2) > div:nth-child(2)
        favorited_count = response.css(".Profile-sideColumnItemValue::text").extract()
        following_count = response.css("div.Card.FollowshipCard  a:nth-child(1) strong::text").extract_first()

        for field in item.fields:
            try:
                item[field] = eval(field)
            except NameError:
                self.logger.debug('Field is Not Defined ' + field)
        yield item


    def parse_user_json(self, response):
        item = UserItem_json()

        if response.status == 401:
            item["Flag"] = 1          #需要cookie登陆访问
            url_token = re.search('members/(.*?)\?', response.url).group(1)
            item["url_token"] = url_token
            self.logger.warning("user %s forbiden vist" %url_token )
            yield item

        else:
            result = json.loads(response.text)

            for field in item.fields:
                if field in result.keys():
                    item[field] = result.get(field)
            item["Flag"] = 0
            yield item

            yield Request(self.user_page.format(user=result.get('url_token')), callback=self.parse_user_page)

            yield Request(
                self.followees_url.format(user=result.get('url_token'), include=self.follows_include, limit=20, offset=0),
                callback=self.parse_follows)

            yield Request(
                self.followers_url.format(user=result.get('url_token'), include=self.follows_include, limit=20, offset=0),
                callback=self.parse_follows)


    def parse_follows(self, response):    # followees,followers可以共享（不需要构建不同的链接，直接paging next取值，不需构建）
        results = json.loads(response.text)

        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_include),
                              self.parse_user_json)  ####json

        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page,
                          callback=self.parse_follows)



