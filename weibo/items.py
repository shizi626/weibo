# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class userItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field(default='null') # 用户id
    name = scrapy.Field(default='null') # 用户昵称
    province = scrapy.Field(default='null')	# 省份
    # city = scrapy.Field(default='null')	# 城市
    collectTime = scrapy.Field(default='null') # 收录时间，即爬取的时间
    gender = scrapy.Field(default='null') # 性别 m f
    verified = scrapy.Field(default='null') # 是否认证 0-认证 1-没有
    followsCount = scrapy.Field(default='null') # 关注人数，原为friendsCount
    fansCount = scrapy.Field(default='null') # 粉丝数，原为followerCount
    weibosCount = scrapy.Field(default='null') # 微博数目，原为statusCount
    bokeUrl = scrapy.Field(default='null') # 外部url，原为--weibo.com/XXXX 现为--weibo.com/u/XXXX，XXXX为用户id
    discription = scrapy.Field(default='null') # 用户描述
    profileImageUrl = scrapy.Field(default='null') # 用户头像

class weiboItem(scrapy.Item):
    id = scrapy.Field(default='null')  # 微博ID
    uID = scrapy.Field(default='null')  # 用户ID
    weiboText = scrapy.Field(default='null') # 微博的内容
    zfcount = scrapy.Field(default='null') # 微博的转发量
    commentCount = scrapy.Field(default='null') # 微博的评论量
    commentLink = scrapy.Field(default='null') # 微博的评论链接
    dzcount = scrapy.Field(default='null') # 微博的点赞量

class commentItem(scrapy.Item):
    weiboId = scrapy.Field(default='null')  # 微博ID
    id = scrapy.Field(default='null') # 评论id
    createdAt = scrapy.Field(default='null') # 评论时间
    text = scrapy.Field(default='null') # 评论内容
    name = scrapy.Field(default='null') # 评论的作者名字
	#imgurl = scrapy.Field() # 评论的作者头像
	#polarity = scrapy.Field() # 不知道这是什么
	#polarity_strength = scrapy.Field() # 不知道这是什么

class idItem(scrapy.Item):
    """
    a class for storing the seeds of crawling
    """
    id = scrapy.Field() # 用户id