import urllib.request as req
import sys
import os
import numpy
import re
import io
from html.parser import HTMLParser

__WIKI__ = 'https://en.wikipedia.org/w/index.php?search='
__QUERY__ = 'Death+Wish+2018' #  ' ' -> '+'

__URL__ = __WIKI__+__QUERY__ #  https://en.wikipedia.org/w/index.php?search=Death+Wish+2018


class Entry():
	def __init__(self):
		self.title = ''	#  <meta property="og:title" content="Meet Me In St. Gallen" />		|		<h2 class="21">Meet Me In St. Gallen</h2>
		self.year = ''	#  <span class="release_date">(2018)</span>
		self.language = ''	#  <p><strong><bdi>Original Language</bdi></strong> English</p>
		self.time = ''	#  <p><strong><bdi>Runtime</bdi></strong> 1h 34m</p>
		self.scores = ''	#  <div class="user_score_chart" data-percent="52.0"
		self.genres = set([])
		'''<section class="genres right_column">
		  <h4><bdi>Genres</bdi></h4>
		  
			<ul>
			  
				<li><a href="/genre/18-drama/movie">Drama</a></li>
			  
				<li><a href="/genre/10749-romance/movie">Romance</a></li>
			  
			</ul>
		  
		</section>
		'''
	def toCSV_labels(self):
		pack = ['title', 'year', 'language', 'time in minutes', 'scores (in %)', 'genres']
		out = '"' + ('";"'.join(pack)) + '"'
		return out
	def toCSV(self):
		title = self.title.replace('"','\\"').lstrip().rstrip()
		time = self.time.split(' ')
		hours = [int(h[:-1]) for h in time if len(h) > 0 and h[-1].lower()=='h']
		hours = hours[0] if len(hours) > 0 else 0
		minutes = [int(m[:-1]) for m in time if len(m) > 0 and  m[-1].lower()=='m']
		minutes = minutes[0] if len(minutes) > 0 else 0
		time = str(hours*60 + minutes)
		genres = ",".join(self.genres).lstrip().rstrip()
		genres = genres.replace('"','\\"')
		lang = self.language.lstrip().rstrip()
		year = self.year
		if len(year) > 0:
			if year[0] == '(' and year[-1] == ')':
				year = year[1:-1]
		
		pack = [title, year, lang, time, self.scores, genres]
		out = '"' + ('";"'.join(pack)) + '"'
		return out
		

#  przygotowany pod stronę themoviedb do uzyskiwania:
#	- wiadomości ze stron z wpisami
class Parser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.item = Entry()
		self.key = ''
		self.value = ''
	def getEntry(self):
		return self.item
	def handle_endtag(self, tag):
		if tag == 'strong' and self.key == 'Original Language':
			self.key = 'lang'
		elif tag == 'strong' and self.key == 'Runtime':
			self.key = 'dura'
		elif tag == 'bdi':
			pass
		else:
			if self.key == 'genre':
				self.item.genres.add(self.value.lower())
			elif self.key == 'dura':
				self.item.time = self.value
			elif self.key == 'lang':
				self.item.language = self.value
			elif self.key == 'year':
				self.item.year = self.value
			self.key = ''
			self.value = ''
	def handle_data(self, data):
		if self.key == 'check':
			if data == 'Original Language':
				self.key = data
			elif data == 'Runtime':
				self.key = data
		elif self.key != '':
			self.value = data
		pass
	def handle_starttag(self, tag, attrs):
		if tag == 'a':
			attr = dict(attrs)
			if 'href' in attr.keys():
				href = attr['href']
				if href.startswith('/genre/'):
					self.key = 'genre'
		elif tag == 'div':
			attr = dict(attrs)
			if 'data-percent' in attr.keys() and 'class' in attr.keys():
				if 'user_score_chart' == attr['class']:
					self.item.scores = attr['data-percent']
		elif tag == 'meta':
			attr = dict(attrs)
			if 'property' in attr.keys() and attr['property'] == 'og:title':
				self.item.title = attr['content']
		elif tag == 'span':
			attr = dict(attrs)
			#<span class="release_date">(2018)</span>
			if 'class' in attr.keys() and attr['class'].find('release_date') != -1:
				if self.item.year == '':
					self.key = 'year'
					self.value = ''
		elif tag == 'bdi':
			self.key = 'check'
				
csv = []
for fn in os.listdir('raw'):
	if fn.endswith('.html'):
		parser = Parser()
		with io.open('raw/'+fn, 'r', encoding='utf8') as f:
			content = f.read()
		parser.feed(content)
		entry = parser.getEntry()
		if entry.title != '' and len(entry.title) > 2:
			if len(csv) == 0:
				csv.append(entry.toCSV_labels())
			csv.append(entry.toCSV())
with io.open('CSV.csv', 'w', encoding='utf8', errors='ignore') as f:
	for line in csv:
		f.write(line)
		f.write('\n')
	