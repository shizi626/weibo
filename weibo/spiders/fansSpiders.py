# -*- encoding=utf-8 -*-

import re
import datetime
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

			url_follows = "http://weibo.cn/%s/follow" % ID
			url_fans = "http://weibo.cn/%s/fans" % ID
			yield Request(url=url_follows, callback=self.parse4)  # 去爬关注人
			yield Request(url=url_fans, callback=self.parse4)  # 去爬粉丝

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