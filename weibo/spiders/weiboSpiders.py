# -*- encoding=utf-8 -*-

import re
import datetime
from scrapy.spider import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request

from weibo.items import userItem, weiboItem, commentItem, idItem
from weibo.util import process_ctime, getSeed, process_emoji

class Spider(CrawlSpider):
	name = "weibo"
	host = "http://weibo.cn"

	scrawlid = set(getSeed()) # 记录待爬的微博ID
	finishid = set()  # 记录已爬的微博ID

	def start_requests(self):
		while True:
			ID = self.scrawlid.pop()
			ID = int(str(ID).split('\'')[1])
			self.finishid.add(ID)  # 加入已爬队列

			url_weibo = "http://weibo.cn/%s/profile?filter=0&page=1" % ID
			yield Request(url=url_weibo, meta={"ID": ID}, callback=self.parse2)  # 去爬微博

	# 抓取思路：
	#   首先抓取某个人的微博的数据，并将这个人微博的评论链接传给第二个爬虫
	#   第二个爬虫接收评论列表的链接后，爬取评论内容，并递归爬取后面页数的评论
	def parse2(self, response):
		""" 抓取微博数据 """

		# print "start crawl weibo"
		selector = Selector(response)
		weibo = selector.xpath('body/div[@class="c" and @id]')
		for one in weibo:
			weiboitem = weiboItem()
			weiboId = one.xpath('@id').extract_first().replace("M_","")  # 微博ID
			weiboText = "".join(one.xpath('div/span[@class="ctt"]/text()').extract())  # 微博内容
			zfreason = "".join(one.xpath('div[2]/text()').extract())  # 转发微博的原因
			zfcount = "".join(re.findall(u'\u8f6c\u53d1\[(\d+)\]', one.extract()))  # 转发数
			commentCount = "".join(re.findall(u'\u8bc4\u8bba\[(\d+)\]', one.extract()))  # 评论数
			commentLink = "".join(one.xpath('div/a[@class = "cc"]/@href').extract()) #评论链接
			dzcount = "".join(re.findall(u'\u8d5e\[(\d+)\]', one.extract()))  # 点赞数

			weiboitem["uID"] = response.meta["ID"]
			weiboitem["id"] = weiboId

			# (转发的)微博内容，去掉最后的"[位置]"和空格符
			tempweibo = weiboText.strip(u"[\u4f4d\u7f6e]").replace(u'\xa0','')+zfreason.replace(u'\xa0','')  
			weiboitem["weiboText"] = process_emoji(tempweibo)

			weiboitem["zfcount"] = int(zfcount)
			weiboitem["commentCount"] = int(commentCount)
			weiboitem["commentLink"] = commentLink
			weiboitem["dzcount"] = int(dzcount)

			yield weiboitem
			# yield Request(url=commentLink, meta={'weiboId':weiboId}, callback=self.parse3)

		url_next = selector.xpath(u'body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()

		if url_next:
			yield Request(url=self.host + url_next[0], meta={"ID": response.meta["ID"]}, callback=self.parse2)	