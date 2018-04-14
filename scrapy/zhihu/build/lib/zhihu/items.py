# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html



from scrapy import Item, Field

class UserItem_json(Item):
    # define the fields for your item here like:
    id = Field()
    name = Field()
    avatar_url = Field()
    headline = Field()
    url = Field()
    url_token = Field()
    gender = Field()    #0female,1male
    type = Field()
    badge = Field()
    employments = Field()
    follower_count = Field()
    answer_count = Field()
    articles_count = Field()
    Flag = Field()  #

class UserItem_page(Item):
    url_token = Field()
    locations = Field()

    educations = Field()
    description = Field()
    question_count = Field()
    vote_from_count = Field()
    thank_from_count = Field()
    favorited_count = Field()
    following_count = Field()





