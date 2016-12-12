from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())

# process.crawl('weibo')	# crawling weibo content
# process.crawl('info')	# crawling user info
# process.crawl('comment')# crawling weibo comments
process.crawl('fans')	# crawling user fans and followers

process.start()