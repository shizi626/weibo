# -*- encoding: utf-8 -*-

"""
using sqlalchemy to build ORM models
"""

import datetime

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from weibo.settings import DATABASE

def db_connect():
	"""
	Performs database connection using database settings from settings.py.
	Returns sqlalchemy engine instance
	"""
	return create_engine(URL(**DATABASE))


def create_table(engine):
	""""""
	Base.metadata.create_all(engine)

Base = declarative_base()

class Sina_users(Base):
	__tablename__ = "sina_users"

	id = Column(String(20),primary_key = True)
	name = Column(String(50), default = "")
	province = Column(String(20), default = "")
	# city = Column(String(20), default = "")
	collectTime = Column(DateTime, default = "")
	gender = Column(String(2))
	verified = Column(Integer)
	followsCount = Column(Integer, default = 0)
	fansCount = Column(Integer, default = 0)
	weibosCount = Column(Integer, default = 0)
	bokeUrl = Column(String(200), default = "")
	discription = Column(String(200), default = "")
	profileImageUrl = Column(String(200), default = "")

class Sina_weibos(Base):
	__tablename__ = "sina_weibos"

	id = Column(String(20), primary_key = True) #微博ID
	uID = Column(String(20), default = "") #用户ID
	weiboText = Column(Text, default = "")
	zfcount = Column(Integer, default = 0)
	commentCount = Column(Integer, default = 0)
	commentLink = Column(String(200), default = "")
	dzcount = Column(Integer, default = 0)

class Sina_comments(Base):
	__tablename__ = "sina_comments"

	weiboId = Column(String(20), default = "")
	id = Column(String(20), primary_key = True) #评论id
	createdAt = Column(DateTime, default = "")
	text = Column(Text, default = "")
	name = Column(String(50), default = "")

class Sina_id(Base):
	"""
	a class for storing the seeds of crawling
	"""
	
	__tablename__ = "sina_id"

	id = Column(String(20), primary_key = True) #用户ID