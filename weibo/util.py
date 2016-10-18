# -*- encoding=utf-8 -*-

import datetime
from sqlalchemy.orm import sessionmaker
from weibo.models import db_connect, Sina_id

def process_ctime(ct):
	# 处理评论的创建时间
	if ct:
		temp = ct.extract_first().split(u'\xa0')[0]
		month = int(temp.find(u'\u6708')) # 找到含有中文“月”的日期
		today = int(temp.find(u'\u4eca\u5929')) # 找到含有中文 "今" 的日期
		minBefore = int(temp.find(u'\u5206\u949f')) # 找到含有中文 "分钟" 的日期
		if minBefore>=0: # 几分钟前发的评论
			if minBefore>1:
				minc = temp[minBefore-2] + temp[minBefore-1]
			else:
				minc = temp[minBefore-1]
			return str(datetime.datetime.now()-datetime.timedelta(seconds=(int(minc)*60))).split('.')[0]
		elif today >=0: # 今天发的评论
			hour = temp[today+3]+temp[today+4]
			minute = temp[today+6]+temp[today+7]
			return str(datetime.datetime.now()).split(' ')[0]+' '+hour+':'+minute+":00"
		elif month >=0: # 今年发的评论
			# 转换时间格式
			monC = temp[month-2] + temp[month-1]
			day = temp[month+1] + temp[month+2]
			return str(datetime.datetime.now().year)+'-'+monC+'-'+day+' '+temp.split(' ')[1]+":00"
		else:
			return temp

def getSeed():
	# return a list of seed sina_id
	engine = db_connect()
	Session = sessionmaker(bind=engine)
	session = Session()
	seed = session.query(Sina_id.id).filter()
	return seed