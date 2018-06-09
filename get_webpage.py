import urllib.request as req
import sys
import os
import numpy
import re
from html.parser import HTMLParser

#  przygotowany pod stronę themoviedb do uzyskiwania:
#	- kolejnych stron 'wyszukiwania'
#	- stron z wpisami
class Parser(HTMLParser):
	def __init__(self, pre, distinct):
		HTMLParser.__init__(self)
		self.out_list = []
		self.pre = pre
		self.dist = distinct
		self.re = re.compile('^/movie(\?page=|/)\d*$')
	def handle_starttag(self, tag, attrs):
		#print('[TAG]', tag)
		if tag == 'a':
			href = dict(attrs).get('href')
			if href is not None:
				if self.re.search(href):
					if not href.startswith('http:'):
						href = self.pre + href
					if href.startswith(self.dist):
						print('link:',href)
						self.out_list.append(href)
			
class Container:
	def __init__(self, root, link, pre, iterations=1):
		self.name = "Robobo"
		self.rootPage = root
		self.seedURLs = [link]
		self.doneURLs = set([])
		self.URLs = set([])
		self.toFetch = None
		self.iterations = iterations
		self.storeURLs = True
		self.storeDATA = True
		self.debug = False
		self.parser = Parser(pre, root)
	def pull_links(self):
		if self.debug:
			print('> pull links')
		for i in self.seedURLs:
			self.URLs.add(i)
		if self.debug:
			print('> links:',self.URLs)
		self.seedURLs = []
	def get_link(self):
		if self.debug:
			print('> get concrete link')
		self.toFetch = list(self.URLs)[0] if len(self.URLs) > 0 else None
		self.URLs = set([]) if len(self.URLs) == 0 else set(list(self.URLs)[1:])
		if self.debug:
			print('> to fetch:', self.toFetch)
			print('> urls:', self.URLs)
	def fetch_link(self):
		if self.debug:
			print('> fetch link')
		URL = self.toFetch
		self.doneURLs.add(URL)
		if self.debug:
			print('> url =',URL)
		try:
			opener = req.build_opener()
			opener.addheadders = [('User-Agent', self.name)]
			page = opener.open(URL)
			if self.debug:
				print('> page downloaded')
			return page
		except:
			if self.debug:
				print('> fail with page')
			return None
	def parse(self, page):
		if self.debug:
			print('> parse')
		html = page.read()
		self.parser.feed(str(html))
		urls = set(self.parser.out_list)
		return html, urls
	def store(self, name, content, type='wb'):
		if self.debug:
			print('> store for',name)
		dir = name
		if self.debug:
			print('> dir:',dir)
		with open('raw/'+str(name), type) as f:
			f.write(content)
			f.close()
	def work(self, i):
		if self.debug:
			print('work')
		self.pull_links()
		self.get_link()
		j = 0
		while self.toFetch is not None:
			page = self.fetch_link()
			j = j + 1
			if page is None:
				pass#self.get_link()
			else:
				html, urls = self.parse(page)
				self.store(str(i) + '_' + str(j) + '_html.html', html)
				urls = list(urls)
				print("root",self.rootPage)
				urls = [_url for _url in urls if _url not in self.doneURLs and _url not in self.seedURLs and _url is not None]
				self.seedURLs = list(self.seedURLs + list(urls))
			self.get_link()
	def done(self):
		urls = '\n' .join(self.doneURLs)
		self.store('links.txt', urls, type='w+')
		
def main():
	c = Container('https://www.themoviedb.org/movie', 'https://www.themoviedb.org/movie', pre='https://www.themoviedb.org', iterations=5)
	for i in range(c.iterations):
		c.work(i)
	c.done()

main()
