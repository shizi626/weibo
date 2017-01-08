# encoding=utf-8
import random
from cookies import cookies
from user_agents import agents
from weibo import settings
from cookies import updateCookie
from scrapy.exceptions import IgnoreRequest


class UserAgentMiddleware(object):
	""" 换User-Agent """

	def process_request(self, request, spider):
		agent = random.choice(agents)
		request.headers["User-Agent"] = agent


class CookiesMiddleware(object):
	""" 换Cookie """

	def process_request(self, request, spider):
		cookie = random.choice(cookies.values())
		request.cookies = cookie
		# print request.cookies

	def process_response(self, request, response, spider):
		if response.status in [300, 301, 302, 303]:
			try:
				redirect_url = response.headers["location"]
				if "login.weibo" in redirect_url or "login.sina" in redirect_url:  # Cookie失效
					print("One Cookie need to be updating...")
					updateCookie(request.cookies)
			except Exception, e:
				raise IgnoreRequest
		else:
			return response


class ProxyMiddleware(object):
	""" 换ip """

	def process_request(self, request, spider):
		# proxy = random.choice(proxies)
		# request.meta['proxy'] = 'http://{}'.format(proxy)

		# using Tor
		request.meta['proxy'] = settings.HTTP_PROXY
		# print request.meta['proxy']