# -*- encoding=utf-8 -*-

import re
import datetime
from scrapy.spider import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request

from weibo.items import userItem, weiboItem, commentItem, idItem
from weibo.util import process_ctime, getSeed, process_emoji

# 最开始的整合版，现在已经分为4个爬虫

class Spider(CrawlSpider):
	name = "comment"
	host = "http://weibo.cn"

	scrawlid = set(getSeed()) # 记录待爬的微博ID
	finishid = set()  # 记录已爬的微博ID

	def start_requests(self):
		while True:

			ID = self.scrawlid.pop()
			ID = int(str(ID).split('\'')[1])
			self.finishid.add(ID)  # 加入已爬队列

			url_information0 = "http://weibo.cn/u/%s" % ID
			url_weibo = "http://weibo.cn/%s/profile?filter=1&page=1" % ID
			url_follows = "http://weibo.cn/%s/follow" % ID
			url_fans = "http://weibo.cn/%s/fans" % ID
			# yield Request(url=url_information0, meta={"ID": ID}, callback=self.parseInfo0)  # 去爬个人信息
			yield Request(url=url_weibo, meta={"ID": ID}, callback=self.parseWeibo)  # 通过微博跳转爬评论
			# yield Request(url=url_follows, callback=self.parseFans_Follows)  # 去爬关注人
			# yield Request(url=url_fans, callback=self.parseFans_Follows)  # 去爬粉丝

	# def parseInfo0(self, response):
	# 	""" 抓取个人信息0 """
	# 	userItems = userItem()
	# 	userItems["id"] = response.meta["ID"] # 用户ID
	# 	selector = Selector(response)
	# 	text0 = selector.xpath('body/div[@class="u"]/div[@class="tip2"]').extract_first()
	# 	if text0:
	# 		weibosCount = re.findall(u'\u5fae\u535a\[(\d+)\]', text0)  # 微博数
	# 		followsCount = re.findall(u'\u5173\u6ce8\[(\d+)\]', text0)  # 关注数
	# 		fansCount = re.findall(u'\u7c89\u4e1d\[(\d+)\]', text0)  # 粉丝数
	# 		if weibosCount:
	# 			userItems["weibosCount"] = int(weibosCount[0])
	# 		if followsCount:
	# 			userItems["followsCount"] = int(followsCount[0])
	# 		if fansCount:
	# 			userItems["fansCount"] = int(fansCount[0])

	# 	userItems["id"] = response.meta["ID"]
	# 	url_information1 = "http://weibo.cn/%s/info" % response.meta["ID"]
	# 	yield Request(url=url_information1, meta={"item": userItems}, callback=self.parseInfo1)

	# def parseInfo1(self, response):
	# 	""" 抓取个人信息1 """
	# 	userItems = response.meta["item"]
	# 	selector = Selector(response)
	# 	text1 = ";".join(selector.xpath('body/div[@class="c"]/text()').extract())  # 获取标签里的所有text()
	# 	nickname = "".join(re.findall(u'\u6635\u79f0[:|\uff1a](.*?);', text1))  # 昵称
	# 	place = re.findall(u'\u5730\u533a[:|\uff1a](.*?);', text1)  # 地区（包括省份和城市）
	# 	gender = re.findall(u'\u6027\u522b[:|\uff1a](.*?);', text1)  # 性别
	# 	verified = re.findall(u'\u8ba4\u8bc1[:|\uff1a](.*?);', text1) # 认证情况
	# 	discription = "".join(re.findall(u'\u7b80\u4ecb[:|\uff1a](.*?);', text1))  # 用户描述
		
	# 	url = response.url  # 首页链接，即外部链接
	# 	image = u"\u5934\u50cf"
	# 	profileImageUrl = "".join(response.xpath('//img[@alt = "%s"]/@src'%(image)).extract())

		
	# 	userItems["name"] = nickname
	# 	if place:
	# 		userItems["province"] = place[0]
	# 	else:
	# 		userItems["province"] = ''

	# 	userItems['collectTime'] = datetime.datetime.now()

	# 	if gender:
	# 		if gender[0] == u"\u7537":
	# 			userItems["gender"] = 'm'
	# 		else:
	# 			userItems["gender"] = 'f'
	# 	else:
	# 		userItems["gender"] = ''

	# 	if verified:
	# 		userItems['verified'] = 0
	# 	else:
	# 		userItems['verified'] = 1

	# 	userItems["bokeUrl"] = url

	# 	userItems['discription'] = process_emoji(discription)

	# 	userItems['profileImageUrl'] = profileImageUrl

	# 	yield userItems


	# 抓取思路：
	#   首先抓取某个人的微博的数据，并将这个人微博的评论链接传给第二个爬虫
	#   第二个爬虫接收评论列表的链接后，爬取评论内容，并递归爬取后面页数的评论
	#	必须使用parseWeibo中的某些项目(commentLink和weiboId)
	#	才能在之后启动parseComment，因此选择保留完整的parseWeibo
	def parseWeibo(self, response):
		""" 抓取微博数据 """

		selector = Selector(response)
		weibo = selector.xpath('body/div[@class="c" and @id]')
		for one in weibo:
			# weiboitem = weiboItem()
			weiboId = one.xpath('@id').extract_first().replace("M_","")  # 微博ID
			# weiboText = "".join(one.xpath('div/span[@class="ctt"]/text()').extract())  # 微博内容
			# zfreason = "".join(one.xpath('div[2]/text()').extract())  # 转发微博的原因
			# zfcount = "".join(re.findall(u'\u8f6c\u53d1\[(\d+)\]', one.extract()))  # 转发数
			# commentCount = "".join(re.findall(u'\u8bc4\u8bba\[(\d+)\]', one.extract()))  # 评论数
			commentLink = "".join(one.xpath('div/a[@class = "cc"]/@href').extract()) #评论链接
			# dzcount = "".join(re.findall(u'\u8d5e\[(\d+)\]', one.extract()))  # 点赞数

			# weiboitem["uID"] = response.meta["ID"]
			# weiboitem["id"] = weiboId

			# (转发的)微博内容，去掉最后的"[位置]"和空格符
			# tempweibo = weiboText.strip(u"[\u4f4d\u7f6e]").replace(u'\xa0','')+zfreason.replace(u'\xa0','')  
			# weiboitem["weiboText"] = process_emoji(tempweibo)

			# weiboitem["zfcount"] = int(zfcount)
			# weiboitem["commentCount"] = int(commentCount)
			# weiboitem["commentLink"] = commentLink
			# weiboitem["dzcount"] = int(dzcount)

			# yield weiboitem
			yield Request(url=commentLink, meta={'weiboId':weiboId}, callback=self.parseComment)

		url_next = selector.xpath(u'body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()

		if url_next:
			yield Request(url=self.host + url_next[0], meta={"ID": response.meta["ID"]}, callback=self.parseWeibo)

	def parseComment(self, response):
		""" 抓取某条微博评论数据 """

		# print "start crawl comment"

		selector = Selector(response)
		comment = selector.xpath('body/div[@class="c" and @id]')
		
		weiboId = response.meta['weiboId']
		for one in comment[1:]:
			citem = commentItem()
			cTime = one.xpath('span[@class="ct"]/text()')
			cId = "".join(re.findall('id="C_(\d+)', one.extract())) #评论的id
			ctext = "".join(one.xpath('span[@class="ctt"]/text()').extract()) # 评论内容
			cAt = " ".join(one.xpath('span[@class="ctt"]/a/text()').extract()) # 评论中@其他用户的内容
			cname = "".join(one.xpath('a[1]/text()').extract()) #评论者昵称

			if weiboId:
				citem['weiboId'] = weiboId

			citem['createdAt'] = process_ctime(cTime)
			citem['id'] = cId

			# 去掉评论中的 "回复:" 一词
			citem['text'] = process_emoji(ctext.replace(u"\u56de\u590d:","")+cAt)
			citem['name'] = cname

			yield citem

		url_next = selector.xpath(
			u'body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()

		if url_next:
			yield Request(url=self.host + url_next[0], meta={'weiboId':weiboId}, callback=self.parseComment)    

	# def parseFans_Follows(self, response):
	# 	""" 抓取关注或粉丝 """
	# 	selector = Selector(response)
	# 	text2 = selector.xpath(u'body//table/tr/td/a[text()="\u5173\u6ce8\u4ed6" or text()="\u5173\u6ce8\u5979"]/@href').extract()
	# 	for elem in text2:
	# 		iditem = idItem()
	# 		elem = re.findall('uid=(\d+)', elem)
	# 		if elem:
	# 			ID = str(elem[0])
	# 			iditem["id"] = ID
	# 			if ID not in self.finishid:
	# 				self.scrawlid.add(ID)
	# 			yield iditem

	# 	url_next = selector.xpath(
	# 		u'body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()

	# 	if url_next:
	# 		yield Request(url=self.host + url_next[0], callback=self.parseFans_Follows)