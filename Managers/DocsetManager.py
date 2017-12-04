import json
import os
import ui
import requests
import xml.etree.cElementTree
import threading
import ui
import time
import math
import tarfile
import plistlib
import console
import sqlite3
import shutil	
import copy	
from urllib.parse import urlparse
from os.path import splitext, basename
from objc_util import ns, ObjCClass
from Managers import DBManager, TypeManager
from Utilities import LogThread
from distutils.version import LooseVersion

class Docset(object):
	def __init__(self):
		self.displayName = ''
		self.downloaded = False
		
class DocsetManager (object):
	def __init__(self, iconPath, typeIconPath, serverManager):
		self.typeManager = TypeManager.TypeManager(typeIconPath)
		# self.localServer = 'http://localhost/feeds/'
		self.localServer = None
		self.docsets = []
		self.downloading = []
		self.updateAvailable = []
		self.docsetFolder = 'Docsets/Standard'
		self.plistPath = 'Contents/Info.plist'
		self.indexPath = 'Contents/Resources/docSet.dsidx'
		self.iconPath = iconPath
		self.typeIconPath = typeIconPath
		self.headers = {
    'User-Agent': 'PyDoc-Pythonista'
    }
		self.__createDocsetFolder()
		self.docsetFeeds = self.__getDocsetFeeds()
		self.serverManager = serverManager
		self.downloadThreads = []
		self.uiUpdateThreads = []
		self.workThreads = []
		self.lastDocsetGroup = None
		self.createInitialSearchIndexAllDocsets()
		
	def __createDocsetFolder(self):
		if not os.path.exists(self.docsetFolder):
			os.mkdir(self.docsetFolder)
		
	def __getDocsetFeeds(self):
		with open('feeds.json') as json_data:
			data = json.load(json_data)
			feeds = []
			for feed in data:
				f = {'name':self.__getDocsetName(feed['feed']),'detailString':'',
				'feed':feed['feed'],
				'iconName':feed['icon'],
				'isCustom':False,
				'feedUrl':'http://kapeli.com/feeds/'+feed['feed'],
				'aliases':feed['aliases'],
				'hasVersions':feed['hasVersions']}
				if feed['feed'] == 'SproutCore.xml':
					f['isCustom'] = True
					f['feedUrl'] = 'http://docs.sproutcore.com/feeds/' + feed['feed']
				f['image'] = self.__getIconWithName(feed['icon'])
				feeds.append(f)
			return feeds
	
	def getOnlineVersions(self, d = None):
		docset = d
		if d == None:
			docset = self.lastDocsetGroup
		else:
			self.lastDocsetGroup = d
		link = docset['feed']
		if link == 'SproutCore.xml':
			data=requests.get('http://docs.sproutcore.com/feeds/' + link).text
			e = xml.etree.ElementTree.fromstring(data)
			version = e.findall('version')[0].text
			for atype in e.findall('url'):
				return {'url': atype.text, 'version':version}
		server = self.serverManager.getDownloadServer(self.localServer)
		data = requests.get(server.url+link).text
		e = xml.etree.ElementTree.fromstring(data)
		urlToUse = ''	
		url = ''
		for atype in e.findall('url'):	
			if not self.localServer == None:
				url = self.localServer
				urlToUse = atype.text
			if atype.text.find(server.url) >= 0:
				urlToUse = atype.text
				url = server.url
		versions = e.findall('other-versions')[0].findall('version')
		ret = []
		downloaded = self.getDownloadedDocsets()
		toCheck = []
		for down in downloaded:
			if down['name'] == docset['name']:
				toCheck.append(down)
		for v in versions:
			baseUrl = url
			onlineVersion = v.find('name').text
			disassembled = urlparse(urlToUse)
			filename, file_ext = splitext(basename(disassembled.path))
			if not baseUrl[-1] == '/':
				baseUrl = baseUrl + '/'
			baseUrl = baseUrl + 'zzz/versions/' + filename + '/' + onlineVersion + '/' + filename + file_ext
			f = copy.copy(docset)
			f['path'] = None
			f['downloadUrl'] = baseUrl
			f['version'] = onlineVersion
			f['status'] = 'online'
			for d in downloaded:
				if d['name'] == f['name'] and d['version'] == f['version']:
					f['status'] = 'installed'
					f['path'] = d['path']
					f['id'] = d['id']
					toCheck.remove(d)
			ret.append(f)
		for d in toCheck:
			d['status'] = 'installed'
			ret.append(d)
		return sorted(ret, key=lambda x: x['version'], reverse=True)
		
	def getAvailableDocsets(self):
		docsets = self.__getOnlineDocsets()
		for d in self.__getDownloadedDocsets():
			for c in docsets:
				if c['name'] == d['name']:
					c['status'] = 'installed'
					c['path'] = d['path']
					c['id'] = d['id']
					c['version'] = d['version']
		for d in self.updateAvailable:
			for c in docsets:
				if c['name'] == d['name']:
					c['status'] = 'Update Available'
		for d in self.__getDownloadingDocsets():
			for c in docsets:
				if c['name'] == d['name']:
					c['version'] = d['version']
					c['status'] = d['status']
					try:
						c['stats'] = d['stats']
					except KeyError:
						c['stats'] = 'downloading'
		return docsets
	
	def getDownloadedDocsets(self):
		return self.__getDownloadedDocsets()
	
	def __docsetFeedToDocset(self, feed):
		return feed
			
	def __getDownloadedDocsets(self):
		dbManager = DBManager.DBManager()
		t = dbManager.InstalledDocsetsByType('standard')
		ds = []
		for d in t:
			aa = {}
			aa['name'] = d[1]
			aa['id'] = d[0]
			aa['path'] = os.path.join(os.path.abspath('.'),d[2])
			aa['image'] = self.__getIconWithName(d[4])
			aa['version'] = d[5]
			ds.append(aa)
		return ds

	def __getDownloadingDocsets(self):
		return self.downloading
	
	def __getOnlineDocsets(self):
		feeds = self.__getDocsetFeeds()
		onlineDocsets = []
		for f in feeds:
			obj = self.__docsetFeedToDocset(f)
			obj['status'] = 'online'
			onlineDocsets.append(obj)
		return onlineDocsets
	
	def __getDocsetName(self, feed):
		name = feed.replace('.xml','')
		name = name.replace('_',' ')
		if name == 'NET Framework':
			name = '.NET Framework'
		return name
	
	def checkDocsetsForUpdates(self, docsets):
		console.show_activity('Checking for updates...')
		for d in docsets:
			if not d['hasVersions'] and d['status'] == 'installed':
				console.show_activity('Checking ' + d['name'] + ' for update...')
				f = self.__getDownloadLink(d['feed'])
				if LooseVersion(str(d['version']).replace('/','')) < LooseVersion(f['version'].replace('/','')):
					d['status'] = 'Update Available'
					d['version'] = f['version']
					self.updateAvailable.append(d)
					
	def __getIconWithName(self, name):
		imgPath = os.path.join(os.path.abspath('.'), self.iconPath, name+'.png')
		if not os.path.exists(imgPath):
			imgPath = os.path.join(os.path.abspath('.'), self.iconPath, 'Other.png')
		return ui.Image.named(imgPath)
	
	def __checkDocsetCanDownload(self, docset):
		cont = True
		feed = docset['feed']
		title = ''
		message = ''
		if feed == 'DOM.xml':
			cont = False
			title = 'DOM Documentation'
			message = 'There is no DOM docset. DOM documentation can be found in the JavaScript docset. Please install the JavaScript docset instead.'
		elif feed == 'RubyMotion.xml':
			cont = False
			title = 'RubyMotion Documentation'
			message = 'RubyMotion had to remove its API documentation due to legal reasons. Please contact the RubyMotion team for more details.\n\nIn the meantime, you can use the Apple API Reference docset instead.'
		elif feed == 'Apple_API_Reference.xml':
			cont = False
			title = 'Apple API Reference'
			message = 'To install the Apple API Reference docset you need to:\n\n1. Use Dash for macOS to install the Apple API Reference docset from Preferences > Downloads\n2. Go to Preferences > Docsets, right click the Apple API Reference docset and select \"Generate iOS Compatible Docset\"\n3. Transfer the resulting docset using the transfer function'
		elif feed == 'Apple_Guides_and_Sample_Code.xml':
			cont = False
			title = 'Apple Guides and Sample Code'
			message = 'To install the Apple Guides and Sample Code docset you need to:\n\n1. Download the docset in Xcode 8\'s Preferences > Components > Documentation\n2.Transfer the resulting docset using the transfer function'
		elif feed == 'OS_X.xml' or feed == 'macOS.xml' or feed == 'watchOS.xml' or feed == 'iOS.xml' or feed == 'tvOS.xml':
			cont = False
			title = 'Apple API Reference'
			name = docset['name']
			message = 'There is no '+name+' docset. The documentation for '+name+' can be found inside the Apple API Reference docset. \n\nTo install the Apple API Reference docset you need to:\n\n1. Use Dash for macOS to install the docset from Preferences > Downloads\n2. Go to Preferences > Docsets, right click the Apple API Reference docset and select \"Generate iOS-compatible Docset\"\n3. Transfer the resulting docset using the transfer function'
				
		if cont == False:
			console.alert(title, message,'Ok', hide_cancel_button=True)
		return cont
	
	def downloadDocset(self, docset, action, refresh_main_view):
		cont = self.__checkDocsetCanDownload(docset)
		if cont and not docset in self.downloading:
			self.downloading.append(docset)
			removeSoon = []
			for d in self.updateAvailable:
				if d['name'] == docset['name']:
					removeSoon.append(d)
			for d in removeSoon:
				self.updateAvailable.remove(d)
			docset['status'] = 'downloading'
			action()
			workThread = LogThread.LogThread(target=self.__determineUrlAndDownload, args=(docset,action,refresh_main_view,))
			self.workThreads.append(workThread)
			workThread.start()
			
	def __determineUrlAndDownload(self, docset, action, refresh_main_view):
		docset['stats'] = 'getting download link'
		action()
		if not 'downloadUrl' in docset.keys():
			data = self.__getDownloadLink(docset['feed'])
			docset['version'] = data['version']
			downloadLink = data['url']
		else:
			downloadLink = docset['downloadUrl']
		downloadThread = LogThread.LogThread(target=self.downloadFile, args=(downloadLink,docset,refresh_main_view,))
		self.downloadThreads.append(downloadThread)
		downloadThread.start()
		updateThread = LogThread.LogThread(target=self.updateUi, args=(action,downloadThread,))
		self.uiUpdateThreads.append(updateThread)
		updateThread.start()

	def updateUi(self, action, t):
		while t.is_alive():
			action()
			time.sleep(0.5)
		action()
		
	def __getDownloadLink(self, link):
		if link == 'SproutCore.xml':
			data=requests.get('http://docs.sproutcore.com/feeds/' + link).text
			e = xml.etree.ElementTree.fromstring(data)
			version = e.findall('version')[0].text
			for atype in e.findall('url'):
				return {'url': atype.text, 'version':version}
		server = self.serverManager.getDownloadServer(self.localServer)
		data = requests.get(server.url+link).text
		e = xml.etree.ElementTree.fromstring(data)
		version = e.findall('version')[0].text
		for atype in e.findall('url'):
			if not self.localServer == None:
				disassembled = urlparse(atype.text)
				filename, file_ext = splitext(basename(disassembled.path))
				url = self.localServer
				if not url[-1] == '/':
					url = url + '/'
				url = url + filename + file_ext
				return {'url': url, 'version':version}
			if atype.text.find(server.url) >= 0:
				return {'url': atype.text, 'version':version}
	
	def downloadFile(self, url, docset, refresh_main_view):
		local_filename = self.__downloadFile(url, docset)
		#self.__downloadFile(url+'.tarix', docset)
		docset['status'] = 'waiting for install'
		self.installDocset(local_filename, docset, refresh_main_view)
	
	def __downloadFile(self, url, docset):
		local_filename = self.docsetFolder+'/'+str(docset['version'])+url.split('/')[-1]
		r = requests.get(url, headers = self.headers, stream=True)
		ret = None
		if r.status_code == 200:
			ret = local_filename
			total_length = r.headers.get('content-length')
			dl = 0
			last = 0
			if os.path.exists(local_filename):
				os.remove(local_filename)
			with open(local_filename, 'wb') as f:
				for chunk in r.iter_content(chunk_size=1024): 
					if chunk: # filter out keep-alive new chunks
						dl += len(chunk)
						f.write(chunk)
						if not total_length == None:
							done = 100 * dl / int(total_length)
							docset['stats'] = str(round(done,2)) + '% ' + str(self.convertSize(dl)) + ' / '+ str(self.convertSize(float(total_length)))
						else:
							docset['stats'] = str(self.convertSize(dl))
		
		r.close()	
		return ret		
		
	def installDocset(self, filename, docset, refresh_main_view):
		extract_location = os.path.join(self.docsetFolder, '_'+docset['name'].replace('/','_'), '_'+docset['version'].replace('/','_'))
		docset['status'] = 'Preparing to install: This might take a while.'
		tar = tarfile.open(filename, 'r:gz')
		n = [name for name in tar.getnames() if '/' not in name][0]
		m = os.path.join(extract_location, n)
		tar.extractall(path=extract_location, members = self.track_progress(tar, docset, len(tar.getmembers())))
		tar.close()
		os.remove(filename)
		# if docset['name'] == 'Drupal 7':
		# 	p = os.path.join(extract_location, 'Drupal.docset')
		# 	n = 'Drupal7.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Drupal 8':
		# 	p = os.path.join(extract_location, 'Drupal.docset')
		# 	n = 'Drupal8.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Java SE6':
		# 	p = os.path.join(extract_location, 'Java.docset')
		# 	n = 'JavaSE6.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Java SE7':
		# 	p = os.path.join(extract_location, 'Java.docset')
		# 	n = 'JavaSE7.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Java SE8':
		# 	p = os.path.join(extract_location, 'Java.docset')
		# 	n = 'JavaSE8.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Java SE9':
		# 	p = os.path.join(extract_location, 'Java.docset')
		# 	n = 'JavaSE9.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Lua 5.1':
		# 	p = os.path.join(extract_location, 'Lua.docset')
		# 	n = 'Lua51.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Lua 5.2':
		# 	p = os.path.join(extract_location, 'Lua.docset')
		# 	n = 'Lua52.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Lua 5.3':
		# 	p = os.path.join(extract_location, 'Lua.docset')
		# 	n = 'Lua53.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Qt 4':
		# 	p = os.path.join(extract_location, 'Qt.docset')
		# 	n = 'Qt4.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Qt 5':
		# 	p = os.path.join(extract_location, 'Qt.docset')
		# 	n = 'Qt5.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Ruby':
		# 	p = os.path.join(extract_location, 'Ruby.docset')
		# 	n = 'Ruby1.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Ruby 2':
		# 	p = os.path.join(extract_location, 'Ruby.docset')
		# 	n = 'Ruby2.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Ruby on Rails 3':
		# 	p = os.path.join(extract_location, 'Ruby on Rails.docset')
		# 	n = 'Ruby on Rails3.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Ruby on Rails 4':
		# 	p = os.path.join(extract_location, 'Ruby on Rails.docset')
		# 	n = 'Ruby on Rails4.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Ruby on Rails 5':
		# 	p = os.path.join(extract_location, 'Ruby on Rails.docset')
		# 	n = 'Ruby on Rails5.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Zend Framework 1':
		# 	p = os.path.join(extract_location, 'Zend_Framework.docset')
		# 	n = 'Zend_Framework1.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Zend Framework 2':
		# 	p = os.path.join(extract_location, 'Zend_Framework.docset')
		# 	n = 'Zend_Framework2.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		# elif docset['name'] == 'Zend Framework 3':
		# 	p = os.path.join(extract_location, 'Zend_Framework.docset')
		# 	n = 'Zend_Framework3.docset'
		# 	m = os.path.join(self.docsetFolder, n)
		# 	b = os.path.join(extract_location, n)
		# 	os.rename(p, b)
		# 	shutil.move(b, m)
		# 	shutil.rmtree(extract_location)
		dbManager = DBManager.DBManager()
		dbManager.DocsetInstalled(docset['name'], m, 'standard', docset['iconName'], docset['version'])
		self.indexDocset(docset, refresh_main_view, m)
	
	def track_progress(self, members, docset, totalFiles):
		i = 0
		for member in members:
			i = i + 1
			done = 100 * i / totalFiles
			docset['status'] = 'installing: ' + str(round(done,2)) + '% ' + str(i) + ' / '+ str(totalFiles) 
			yield member
		
	def indexDocset(self, docset, refresh_main_view, path):
		docset['status'] = 'indexing'
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT count(*) FROM sqlite_master WHERE type = \'table\' AND name = \'searchIndex\''
		c = conn.execute(sql)
		data = c.fetchone()
		if int(data[0]) == 0:
			sql = 'CREATE TABLE searchIndex(rowid INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT)'
			c = conn.execute(sql)
			conn.commit()
			sql = 'SELECT f.ZPATH, m.ZANCHOR, t.ZTOKENNAME, ty.ZTYPENAME, t.rowid FROM ZTOKEN t, ZTOKENTYPE ty, ZFILEPATH f, ZTOKENMETAINFORMATION m WHERE ty.Z_PK = t.ZTOKENTYPE AND f.Z_PK = m.ZFILE AND m.ZTOKEN = t.Z_PK ORDER BY t.ZTOKENNAME'
			c = conn.execute(sql)
			data = c.fetchall()
			for t in data:
				conn.execute("insert into searchIndex values (?, ?, ?, ?)", (t[4], t[2], self.typeManager.getTypeForName(t[3]).name, t[0] ))
				conn.commit()
		else:
			sql = 'SELECT rowid, type FROM searchIndex'
			c = conn.execute(sql)
			data = c.fetchall()
			for t in data:
				newType = self.typeManager.getTypeForName(t[1])
				if not newType == None and not newType.name == t[1]:
					conn.execute("UPDATE searchIndex SET type=(?) WHERE rowid = (?)", (newType.name, t[0] ))
				conn.commit()
		indexSql = 'CREATE INDEX ix_searchIndex_name ON searchIndex(name)'
		conn.execute(indexSql)
		conn.close()
		self.postProcess(docset, refresh_main_view)

	def createInitialSearchIndexAllDocsets(self):
		docsets = self.getDownloadedDocsets()
		for d in docsets:
			indexPath = os.path.join(d['path'], self.indexPath)
			conn = sqlite3.connect(indexPath)
			conn = sqlite3.connect(indexPath)
			indexSql = 'CREATE INDEX IF NOT EXISTS ix_searchIndex_name ON searchIndex(name)'
			conn.execute(indexSql)
			conn.close()
		
		
	def postProcess(self, docset, refresh_main_view):
		docset['status'] = 'installed'
		refresh_main_view()

	def convertSize(self, size):
		if (size == 0):
			return '0B'
		size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
		i = int(math.floor(math.log(size,1024)))
		p = math.pow(1024,i)
		s = round(size/p,2)
		return '%s %s' % (s,size_name[i])
	
	def getTypesForDocset(self, docset):
		types = []
		path = docset['path']
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type FROM searchIndex GROUP BY type ORDER BY type COLLATE NOCASE'
		c = conn.execute(sql)
		data = c.fetchall()
		conn.close()
		for t in data:
			types.append(self.typeManager.getTypeForName(t[0]))
		return types
	
	def getIndexesbyTypeForDocset(self, docset, type):
		indexes = []
		path = docset['path']
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type, name, path FROM searchIndex WHERE type = (?) ORDER BY name COLLATE NOCASE'
		c = conn.execute(sql, (type.name,))
		data = c.fetchall()
		conn.close()
		dTypes = {}
		type = None
		for t in data:
			if t[0] in dTypes.keys():
				type= dTypes[t[0]]
			else:
				type = self.typeManager.getTypeForName(t[0])
				dTypes[t[0]] = type
			indexes.append({'type':type, 'name':t[1],'path':t[2]})
		return indexes
		
	def getIndexesbyTypeAndNameForDocset(self, docset, typeName, name):
		indexes = []
		path = docset['path']
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type, name, path FROM searchIndex WHERE type = (?) AND name LIKE (?) ORDER BY name COLLATE NOCASE'
		c = conn.execute(sql, (typeName, name))
		data = c.fetchall()
		conn.close()
		dTypes = {}
		type = None
		for t in data:
			if t[0] in dTypes.keys():
				type= dTypes[t[0]]
			else:
				type = self.typeManager.getTypeForName(t[0])
				dTypes[t[0]] = type
			indexes.append({'type':type, 'name':t[1],'path':t[2]})
		return indexes
	
	def getIndexesbyNameForDocset(self, docset, name):
		indexes = []
		path = docset['path']
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type, name, path FROM searchIndex WHERE name LIKE (?) ORDER BY name COLLATE NOCASE'
		c = conn.execute(sql, (name,))
		data = c.fetchall()
		conn.close()
		dTypes = {}
		type = None
		for t in data:
			if t[0] in dTypes.keys():
				type= dTypes[t[0]]
			else:
				type = self.typeManager.getTypeForName(t[0])
				dTypes[t[0]] = type
			indexes.append({'type':type, 'name':t[1],'path':t[2]})
		return indexes
	
	def getIndexesForDocset(self, docset):
		indexes = []
		path = docset['path']
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type, name, path FROM searchIndex ORDER BY name COLLATE NOCASE'
		c = conn.execute(sql)
		data = c.fetchall()
		conn.close()
		dTypes = {}
		type = None
		for i in data:
			if t[0] in dTypes.keys():
				type= dTypes[t[0]]
			else:
				type = self.typeManager.getTypeForName(t[0])
				dTypes[t[0]] = type
			indexes.append({'type':type, 'name':t[1],'path':t[2]})
		return types
	
	def getIndexesbyNameForAllDocset(self, name):
		if name == None or name == '':
			return {}
		else:
			docsets = self.getDownloadedDocsets()
			indexes = {}
			for d in docsets:
				ind = self.getIndexesbyNameForDocsetSearch(d, name)
				for k in ind:
					if not k in indexes.keys():
						indexes[k] = []
					indexes[k].extend(ind[k])
			return indexes
			
	
	def getIndexesbyNameForDocsetSearch(self, docset, name):
		if name == None or name == '':
			return []
		else:
			ind = {}
			path = docset['path']
			indexPath = os.path.join(path, self.indexPath)
			conn = sqlite3.connect(indexPath)
			sql = 'SELECT type, name, path FROM searchIndex WHERE name LIKE (?) ORDER BY name COLLATE NOCASE'
			c = conn.execute(sql, (name, ))
			data = {'first' : c.fetchall()}

			sql = 'SELECT type, name, path FROM searchIndex WHERE name LIKE (?) AND name NOT LIKE (?) ORDER BY name COLLATE NOCASE'
			c = conn.execute(sql, (name.replace(' ','%'), name, ))
			data['second'] = c.fetchall()
						
			sql = 'SELECT type, name, path FROM searchIndex WHERE name LIKE (?) AND name NOT LIKE (?) AND name NOT LIKE (?) ORDER BY name COLLATE NOCASE'
			c = conn.execute(sql, (name.replace(' ','%')+'%', name.replace(' ','%'), name, ))
			data['third'] = c.fetchall()
			
			sql = 'SELECT type, name, path FROM searchIndex WHERE name LIKE (?) AND name NOT LIKE (?) AND name NOT LIKE (?) AND name NOT LIKE (?) ORDER BY name COLLATE NOCASE'
			c = conn.execute(sql, ('%'+name.replace(' ','%')+'%',name.replace(' ','%')+'%',name.replace(' ','%'), name, ))
			data['fourth'] = c.fetchall()
						
									
			conn.close()
			dTypes = {}
			for k in data:
				ind[k] = []
				for t in data[k]:
					url = 'file://' + os.path.join(path, 'Contents/Resources/Documents', t[2])
					url = url.replace(' ', '%20')
					type = None
					if t[0] in dTypes.keys():
						type= dTypes[t[0]]
					else:
						type = self.typeManager.getTypeForName(t[0])
						dTypes[t[0]] = type
					ind[k].append({'name':t[1], 'path':url, 'icon':docset['image'],'docsetname':docset['name'],'type':type, 'callbackOverride':'', 'docset': docset})
			return ind
	
	
	def deleteDocset(self, docset, post_action, confirm=True):
		but = 1
		if confirm:
			but = console.alert('Are you sure?', 'Would you like to delete the docset, ' + docset['name'] + '\n This may take a while.', 'Ok')
		if but == 1:
			p = os.path.join(self.docsetFolder, '_'+docset['name'].replace('/','_'), '_'+docset['version'].replace('/','_'))
			dbmanager = DBManager.DBManager()
			dbmanager.DocsetRemoved(docset['id'])
			shutil.rmtree(p)
			docset['status'] = 'online'
			docset['path'] = None
			if not post_action == None:
				post_action()
		
if __name__ == '__main__':
	dm = DocsetManager()
	print((dm.getAvailableDocsets()))
	

