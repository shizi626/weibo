# -*- encoding=utf-8 -*-

import re
import datetime
from scrapy.spider import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request

from weibo.items import userItem, weiboItem, commentItem, idItem
from weibo.util import process_ctime, getSeed, process_emoji

class Spider(CrawlSpider):
	name = "info"
	host = "http://weibo.cn"

	scrawlid = set(getSeed()) # 记录待爬的微博ID
	finishid = set()  # 记录已爬的微博ID

	def start_requests(self):
		while True:
			ID = self.scrawlid.pop()
			ID = int(str(ID).split('\'')[1])
			self.finishid.add(ID)  # 加入已爬队列

			url_information0 = "http://weibo.cn/u/%s" % ID
			yield Request(url=url_information0, meta={"ID": ID}, callback=self.parse0)  # 去爬个人信息

	def parse0(self, response):
		""" 抓取个人信息0 """
		userItems = userItem()
		userItems["id"] = response.meta["ID"] # 用户ID
		selector = Selector(response)
		text0 = selector.xpath('body/div[@class="u"]/div[@class="tip2"]').extract_first()
		if text0:
			weibosCount = re.findall(u'\u5fae\u535a\[(\d+)\]', text0)  # 微博数
			followsCount = re.findall(u'\u5173\u6ce8\[(\d+)\]', text0)  # 关注数
			fansCount = re.findall(u'\u7c89\u4e1d\[(\d+)\]', text0)  # 粉丝数
			if weibosCount:
				userItems["weibosCount"] = int(weibosCount[0])
			if followsCount:
				userItems["followsCount"] = int(followsCount[0])
			if fansCount:
				userItems["fansCount"] = int(fansCount[0])

		userItems["id"] = response.meta["ID"]
		url_information1 = "http://weibo.cn/%s/info" % response.meta["ID"]
		yield Request(url=url_information1, meta={"item": userItems}, callback=self.parse1)

	def parse1(self, response):
		""" 抓取个人信息1 """
		userItems = response.meta["item"]
		selector = Selector(response)
		text1 = ";".join(selector.xpath('body/div[@class="c"]/text()').extract())  # 获取标签里的所有text()
		nickname = "".join(re.findall(u'\u6635\u79f0[:|\uff1a](.*?);', text1))  # 昵称
		place = re.findall(u'\u5730\u533a[:|\uff1a](.*?);', text1)  # 地区（包括省份和城市）
		gender = re.findall(u'\u6027\u522b[:|\uff1a](.*?);', text1)  # 性别
		verified = re.findall(u'\u8ba4\u8bc1[:|\uff1a](.*?);', text1) # 认证情况
		discription = "".join(re.findall(u'\u7b80\u4ecb[:|\uff1a](.*?);', text1))  # 用户描述
		
		url = response.url  # 首页链接，即外部链接
		image = u"\u5934\u50cf"
		profileImageUrl = "".join(response.xpath('//img[@alt = "%s"]/@src'%(image)).extract())

		
		userItems["name"] = nickname
		if place:
			userItems["province"] = place[0]
		else:
			userItems["province"] = ''

		userItems['collectTime'] = datetime.datetime.now()

		if gender:
			if gender[0] == u"\u7537":
				userItems["gender"] = 'm'
			else:
				userItems["gender"] = 'f'
		else:
			userItems["gender"] = ''

		if verified:
			# 是否认证 0-认证 1-没有
			userItems['verified'] = 0
		else:
			userItems['verified'] = 1

		userItems["bokeUrl"] = url

		userItems['discription'] = process_emoji(discription)

		userItems['profileImageUrl'] = profileImageUrl

		yield userItems