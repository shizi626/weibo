# -*- encoding=utf-8 -*-

import re
import datetime
import random
from scrapy.spider import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request

from weibo.items import userItem, weiboItem, commentItem, idItem, relationItem
from weibo.util import getSeed

class Spider(CrawlSpider):
	"""
	a special spider for crawling users' fans relationship
	and for a tuple of (userID, userFans1, userFans2, ..., userFans200)
	the number of fans is up to 200 because the mechanism of weibo.cn
	"""
	name = "relation"
	host = "http://weibo.cn"

	scrawlid = set(getSeed()) # 记录待爬的微博ID
	finishid = set()  # 记录已爬的微博ID

	def start_requests(self):
		while True:
			ID = self.scrawlid.pop()
			ID = int(str(ID).split('\'')[1])
			self.finishid.add(ID)  # 加入已爬队列

			url_fans = "http://weibo.cn/%s/fans?page=1" % (ID)
			yield Request(url=url_fans,meta={"ID": ID},callback=self.parseRelation)  # 去爬粉丝

	def parseRelation(self,response):
		"""抓取用户的粉丝"""
		selector = Selector(response)
		text2 = selector.xpath(
			u'body//table/tr/td/a[text()="\u5173\u6ce8\u4ed6" or text()="\u5173\u6ce8\u5979"]/@href').extract()
		uid = response.meta["ID"]

		# initialize item
		relationitem = relationItem()
		relationitem["id"] = uid
		relationitem["relationList"] = []

		for elem in text2:
			# read the first page of fans
			elem = re.findall('uid=(\d+)', elem)
			if elem:
				ID = str(elem[0])
				relationitem["relationList"].append(ID)

		url_next = selector.xpath(
			u'body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()
		if url_next:
			yield Request(url=self.host + url_next[0],meta={"relationitem":relationitem},callback=self.parse_add_relation)

		
	def parse_add_relation(self,response):
		"""
		抓取‘下一页’的用户粉丝
		直至最后一页，然后 yield item
		"""
		selector = Selector(response)
		relationitem = response.meta["relationitem"]
		text2 = selector.xpath(
			u'body//table/tr/td/a[text()="\u5173\u6ce8\u4ed6" or text()="\u5173\u6ce8\u5979"]/@href').extract()

		for elem in text2:
			# read the first page of fans
			elem = re.findall('uid=(\d+)', elem)
			if elem:
				ID = str(elem[0])
				relationitem["relationList"].append(ID)

		url_next = selector.xpath(
			u'body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()
		if url_next:
			# crawling the fans of "next" page 
			yield Request(url=self.host + url_next[0],meta={"relationitem":relationitem},callback=self.parse_add_relation)
		else:
			# convert the content of relationitem["relationList"] to string
			relationitem["relationList"] = ','.join(relationitem["relationList"])
			yield relationitem