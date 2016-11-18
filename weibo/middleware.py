# encoding=utf-8
import random
from cookies import cookies
from user_agents import agents
from ipproxy import proxies
from weibo import settings


class UserAgentMiddleware(object):
	""" 换User-Agent """

	def process_request(self, request, spider):
		agent = random.choice(agents)
		request.headers["User-Agent"] = agent


class CookiesMiddleware(object):
	""" 换Cookie """

	def process_request(self, request, spider):
		cookie = random.choice(cookies)
		request.cookies = cookie

class ProxyMiddleware(object):
	""" 换ip """

	def process_request(self, request, spider):
		# proxy = random.choice(proxies)
		# request.meta['proxy'] = 'http://{}'.format(proxy)

		# using Tor
		request.meta['proxy'] = settings.HTTP_PROXY