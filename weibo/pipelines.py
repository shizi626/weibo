# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import csv
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

from weibo.items import userItem,weiboItem,commentItem,idItem
from weibo.models import db_connect,create_table,\
								Sina_users,Sina_weibos,Sina_comments,Sina_id

from scrapy.exceptions import DropItem
from scrapy import signals

@contextmanager
def session_scope(Session):
	"""Provide a transactional scope around a series of operations."""
	session = Session()
	try:
		yield session
		session.commit()
	except:
		session.rollback()
		raise
	finally:
		session.close()

# 待修改，要去重！
class DuplicatesPipeline(object):

	def __init__(self):
		engine = db_connect()
		create_table(engine)
		self.Session = sessionmaker(bind=engine)
		self.session = self.Session()

	def process_item(self, item, spider):
		if self.session.query(Sina_users.id).filter(Sina_users.id == item['id']) or \
			self.session.query(Sina_weibos.id).filter(Sina_weibos.id == item['id']) or \
			self.session.query(Sina_comments.id).filter(Sina_comments.id == item['id']):
			raise DropItem("Duplicate item found: %s" % item)
		else:
			return item

class WeiboPipeline(object):

	def __init__(self):
		engine = db_connect()
		create_table(engine)
		self.Session = sessionmaker(bind=engine)

	@classmethod
	def from_crawler(cls, crawler):
		pipeline = cls()
		crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
		crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
		return pipeline

	def spider_opened(self, spider):
		pass

	def spider_closed(self, spider):
		pass
		
	def process_item(self, item, spider):
		if isinstance(item, userItem):
			u = Sina_users(
				id = item['id'],
				name = item['name'].encode("utf-8"),
				province = item['province'].encode("utf-8"),
				city = item['city'].encode("utf-8"),
				collectTime = item['collectTime'],
				gender = item['gender'],
				verified = item['verified'],
				followsCount = item['followsCount'],
				fansCount = item['fansCount'],
				weibosCount = item['weibosCount'],
				bokeUrl = item['bokeUrl'],
				discription = item['discription'].encode("utf-8"),
				profileImageUrl = item['profileImageUrl']
				)
			with session_scope(self.Session) as session:
				session.add(u)
		elif isinstance(item, commentItem):
			c = Sina_comments(
				weiboId = item['weiboId'],
				id = item['id'],
				createdAt = item['createdAt'],
				text = item['text'],
				name = item['name'],
			)
			with session_scope(self.Session) as session:
				session.add(c)
		elif isinstance(item, weiboItem):
			w = Sina_weibos(
				id = item['id'],
				uID = item['uID'],
				weiboText = item['weiboText'].encode("utf-8"),
				zfcount = item['zfcount'],
				commentCount = item['commentCount'],
				commentLink = item['commentLink'],
				dzcount = item['dzcount'],
				)
			with session_scope(self.Session) as session:
				session.add(w)
		elif isinstance(item, idItem):
			i = Sina_id(id = item['id'])
			with session_scope(self.Session) as session:
				session.add(i)