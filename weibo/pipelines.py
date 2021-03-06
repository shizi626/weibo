# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import csv
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

from weibo.items import userItem,weiboItem,commentItem,idItem,relationItem
from weibo.models import db_connect,create_table,\
								Sina_users,Sina_weibos,Sina_comments,Sina_id,Sina_relation

from scrapy.exceptions import DropItem
from scrapy import signals

import mysql

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
				# city = item['city'].encode("utf-8"),
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
				# add item to database through ORM model in models.py
				session.add(u)
		if isinstance(item, commentItem):
			c = Sina_comments(
				weiboId = item['weiboId'],
				id = item['id'],
				createdAt = item['createdAt'],
				text = item['text'],
				name = item['name'],
			)
			with session_scope(self.Session) as session:
				session.add(c)
		if isinstance(item, weiboItem):
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
		if isinstance(item, idItem):
			i = Sina_id(id = item['id'])
			with session_scope(self.Session) as session:
				session.add(i)
		if isinstance(item, relationItem):
			i = Sina_relation(
				id = item['id'],
				relationList = item['relationList'])
			with session_scope(self.Session) as session:
				session.add(i)
				