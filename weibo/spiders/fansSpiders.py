# -*- encoding=utf-8 -*-

import re
import datetime
import random
from scrapy.spider import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request

from weibo.items import userItem, weiboItem, commentItem, idItem
from weibo.util import process_ctime, getSeed, process_emoji

class Spider(CrawlSpider):
	name = "fans"
	host = "http://weibo.cn"

	scrawlid = set(getSeed()) # 记录待爬的微博ID
	finishid = set()  # 记录已爬的微博ID

	def start_requests(self):
		while True:
			ID = self.scrawlid.pop()
			ID = int(str(ID).split('\'')[1])
			self.finishid.add(ID)  # 加入已爬队列

			url_follows = "http://weibo.cn/%s/follow?page=1" %(ID)
			url_fans = "http://weibo.cn/%s/fans?page=1" % (ID)
			url_weibo = "http://weibo.cn/%s/profile?filter=1&page=1" % ID

			yield Request(url=url_follows, callback=self.parse4)  # 去爬关注人
			yield Request(url=url_fans, callback=self.parse4)  # 去爬粉丝
			yield Request(url=url_weibo, meta={"ID": ID}, callback=self.parse5) # 通过微博的转发和评论爬取粉丝

	def parse4(self, response):
		""" 抓取关注或粉丝 """
		selector = Selector(response)
		text2 = selector.xpath(u'body//table/tr/td/a[text()="\u5173\u6ce8\u4ed6" or text()="\u5173\u6ce8\u5979"]/@href').extract()
		for elem in text2:
			iditem = idItem()
			elem = re.findall('uid=(\d+)', elem)
			if elem:
				ID = str(elem[0])
				iditem["id"] = ID
				if ID not in self.finishid:
					self.scrawlid.add(ID)
				yield iditem

		url_next = selector.xpath(
			u'body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()

		if url_next:
			yield Request(url=self.host + url_next[0], callback=self.parse4)

	def parse5(self, response):
		"""通过微博的转发和评论链接跳转爬取粉丝"""
		selector = Selector(response)
		weibo = selector.xpath('body/div[@class="c" and @id]')
		for one in weibo:
			commentLink = "".join(one.xpath('div/a[@class = "cc"]/@href').extract()) #评论链接
			repostLink = "".join(one.xpath(u'div[1]/a[3]/@href').extract())	 #转发链接
			weiboId = one.xpath('@id').extract_first().replace("M_","")  # 微博ID		
			zfcount = "".join(re.findall(u'\u8f6c\u53d1\[(\d+)\]', one.extract()))  # 转发数
			commentCount = "".join(re.findall(u'\u8bc4\u8bba\[(\d+)\]', one.extract()))  # 评论数
			uid = response.meta["ID"]
			# 小于一定量的评论数和转发数不去爬取
			if (int(zfcount)>10):
				yield Request(url=commentLink, callback=self.parse6)
			if(int(commentCount)>10):
				yield Request(url='http://weibo.cn/repost/%s?uid=%s&rl=0' %(weiboId, uid), callback=self.parse7)
		
		url_next = selector.xpath(u'body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()

		if url_next:
			yield Request(url=self.host + url_next[0], meta={"ID": response.meta["ID"]}, callback=self.parse5)

	def parse6(self, response):
		"""爬取评论的用户id"""
		selector = Selector(response)
		comment = selector.xpath('body/div[@class="c" and @id]')
		for one in comment[1:]:
			# 评论者的id，可以将其加到数据库的用户id中
			c_user_id = "".join(re.findall('href="/u/(\d+)"', one.extract())) 
			iditem = idItem()
			iditem["id"] = c_user_id
			print 'crawl from comment user id'
			yield iditem

		url_next = selector.xpath(
			u'body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()

		if url_next:
			yield Request(url=self.host + url_next[0], callback=self.parse6)    

	def parse7(self, response):
		"""爬取转发的用户id"""
		selector = Selector(response)
		repost = selector.xpath('//span[@class="cc"]/..')
		for one in repost:
			# 转发者的id，可以将其加到数据库的用户id中
			c_user_id = "".join(re.findall('href="/u/(\d+)"', one.extract())) 
			iditem = idItem()
			iditem["id"] = c_user_id
			print 'crawl from repost user id'
			yield iditem

		url_next = selector.xpath(
			u'body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()

		if url_next:
			yield Request(url=self.host + url_next[0], callback=self.parse7)   			
