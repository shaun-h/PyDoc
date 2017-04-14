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
from urllib.parse import urlparse
from os.path import splitext, basename
from objc_util import ns, ObjCClass

class Docset(object):
	def __init__(self):
		self.displayName = ''
		self.downloaded = False
		
class DocsetManager (object):
	def __init__(self, iconPath, typeIconPath, serverManager):
		self.localServer = None
		self.docsets = []
		self.downloading = []
		self.docsetFolder = 'Docsets'
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
		
	def getAvailableDocsets(self):
		docsets = self.__getOnlineDocsets()
		for d in self.__getDownloadedDocsets():
			for c in docsets:
				if c['name'] == d['name']:
					c['status'] = 'installed'
					c['path'] = d['path']
		for d in self.__getDownloadingDocsets():
			for c in docsets:
				if c['name'] == d['name']:
					c['status'] = d['status']
					try:
						c['stats'] = d['stats']
					except KeyError:
						c['stats'] = 'downloading'
		return docsets
	
	def getDownloadedDocsets(self):
		ds = []
		for dd in self.__getDownloadedDocsets():
			for feed in self.docsetFeeds:
				if dd['name'] == feed['name']:
					feed['path'] = dd['path']
					ds.append(feed)
		return ds
	
	def __docsetFeedToDocset(self, feed):
		return feed
			
	def __getDownloadedDocsets(self):
		ds = []
		folder = os.path.join(os.path.abspath('.'), self.docsetFolder)
		for dir in os.listdir(folder):
			if os.path.isdir(os.path.join(folder,dir)):
				pl = plistlib.readPlist(
				os.path.join(folder,dir, self.plistPath))
				name = pl['CFBundleName']
				print(name)
				if name == 'Sails.js':
					name = 'SailsJS'
				elif name == 'Backbone.js':
					name = 'BackboneJS'
				elif name == 'AngularDart':
					name = 'Angular.dart'
				elif name == 'D3.js':
					name = 'D3JS'
				elif name == 'Lodash':
					name = 'Lo-Dash'
				elif name == 'Marionette':
					name = 'MarionetteJS'
				elif name == 'Matplotlib':
					name = 'MatPlotLib'
				elif name == 'Moment.js':
					name = 'MomentJS'
				elif name == 'Node.js':
					name = 'NodeJS'
				elif name == 'Underscore.js':
					name = 'UnderscoreJS'
				elif name == 'Vue.js':
					name = 'VueJS'
				elif name == 'Zepto.js':
					name = 'ZeptoJS'
				ds.append({'name':name,'path':os.path.join(folder,dir)})
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
	
	def __getIconWithName(self, name):
		
		imgPath = os.path.join(os.path.abspath('.'), self.iconPath, name+'.png')
		return ui.Image.named(imgPath)
		
	def __getTypeIconWithName(self, name):
		
		imgPath = os.path.join(os.path.abspath('.'), self.typeIconPath , name+'.png')
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
			message = 'To install the Apple API Reference docset you need to:\n\n1. Use Dash for macOS to install the Apple API Reference docset from Preferences > Downloads\n2. Go to Preferences > Docsets, right click the Apple API Reference docset and select \"Generate iOS Compatible Docset\"\n3. Transfer the resulting docset using iTunes File Sharing'
		elif feed == 'Apple_Guides_and_Sample_Code.xml':
			cont = False
			title = 'Apple Guides and Sample Code'
			message = 'To install the Apple Guides and Sample Code docset you need to:\n\n1. Download the docset in Xcode 8\'s Preferences > Components > Documentation\n2.Transfer it to Dash for iOS using iTunes File Sharing'
		elif feed == 'OS_X.xml' or feed == 'macOS.xml' or feed == 'watchOS.xml' or feed == 'iOS.xml' or feed == 'tvOS.xml':
			cont = False
			title = 'Apple API Reference'
			name = docset['name']
			message = 'There is no '+name+' docset. The documentation for '+name+' can be found inside the Apple API Reference docset. \n\nTo install the Apple API Reference docset you need to:\n\n1. Use Dash for macOS to install the docset from Preferences > Downloads\n2. Go to Preferences > Docsets, right click the Apple API Reference docset and select \"Generate iOS-compatible Docset\"\n3. Transfer the resulting docset using iTunes File Sharing'
				
		if cont == False:
			console.alert(title, message,'Ok', hide_cancel_button=True)
		return cont
	
	def downloadDocset(self, docset, action, refresh_main_view):
		cont = self.__checkDocsetCanDownload(docset)
		if cont and not docset in self.downloading:
			docset['status'] = 'downloading'
			self.downloading.append(docset)
			action()
			workThread = threading.Thread(target=self.__determineUrlAndDownload, args=(docset,action,refresh_main_view,))
			self.workThreads.append(workThread)
			workThread.start()
			
	def __determineUrlAndDownload(self, docset, action, refresh_main_view):
		docset['stats'] = 'getting download link'
		action()
		downloadLink = self.__getDownloadLink(docset['feed'])
		downloadThread = threading.Thread(target=self.downloadFile, args=(downloadLink,docset,refresh_main_view,))
		self.downloadThreads.append(downloadThread)
		downloadThread.start()
		updateThread = threading.Thread(target=self.updateUi, args=(action,downloadThread,))
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
			for atype in e.findall('url'):
				return atype.text
		server = self.serverManager.getDownloadServer(self.localServer)
		data = requests.get(server.url+link).text
		e = xml.etree.ElementTree.fromstring(data)
		for atype in e.findall('url'):
			if not self.localServer == None:
				disassembled = urlparse(atype.text)
				filename, file_ext = splitext(basename(disassembled.path))
				url = self.localServer
				if not url[-1] == '/':
					url = url + '/'
				url = url + filename + file_ext
				return url
			if atype.text.find(server.url) >= 0:
				return atype.text
	
	def downloadFile(self, url, docset, refresh_main_view):
		local_filename = self.__downloadFile(url, docset)
		#self.__downloadFile(url+'.tarix', docset)
		docset['status'] = 'waiting for install'
		self.installDocset(local_filename, docset, refresh_main_view)
	
	def __downloadFile(self, url, docset):
		local_filename = self.docsetFolder+'/'+url.split('/')[-1]
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
		extract_location = self.docsetFolder
		if docset['name'] == 'Drupal 7':
			extract_location = os.path.join(self.docsetFolder, 'drupal7install')
		elif docset['name'] == 'Drupal 8':
			extract_location = os.path.join(self.docsetFolder, 'drupal8install')
		elif docset['name'] == 'Java SE6':
			extract_location = os.path.join(self.docsetFolder, 'javase6install')
		elif docset['name'] == 'Java SE7':
			extract_location = os.path.join(self.docsetFolder, 'javase7install')
		elif docset['name'] == 'Java SE8':
			extract_location = os.path.join(self.docsetFolder, 'javase8install')
		elif docset['name'] == 'Lua 5.1':
			extract_location = os.path.join(self.docsetFolder, 'lua51install')
		elif docset['name'] == 'Lua 5.2':
			extract_location = os.path.join(self.docsetFolder, 'lua52install')
		elif docset['name'] == 'Lua 5.3':
			extract_location = os.path.join(self.docsetFolder, 'lua53install')
		elif docset['name'] == 'Qt 4':
			extract_location = os.path.join(self.docsetFolder, 'qt4install')
		elif docset['name'] == 'Qt 5':
			extract_location = os.path.join(self.docsetFolder, 'qt5install')
		elif docset['name'] == 'Ruby':
			extract_location = os.path.join(self.docsetFolder, 'rubyinstall')
		elif docset['name'] == 'Ruby 2':
			extract_location = os.path.join(self.docsetFolder, 'ruby2install')
		elif docset['name'] == 'Ruby on Rails 3':
			extract_location = os.path.join(self.docsetFolder, 'rubyonrails3install')
		elif docset['name'] == 'Ruby on Rails 4':
			extract_location = os.path.join(self.docsetFolder, 'rubyonrails4install')
		elif docset['name'] == 'Ruby on Rails 5':
			extract_location = os.path.join(self.docsetFolder, 'rubyonrails5install')
		elif docset['name'] == 'Zend Framework 1':
			extract_location = os.path.join(self.docsetFolder, 'zendframework1install')
		elif docset['name'] == 'Zend Framework 2':
			extract_location = os.path.join(self.docsetFolder, 'zendfrmework2install')
		elif docset['name'] == 'Zend Framework 3':
			extract_location = os.path.join(self.docsetFolder, 'zendframework3install')
		docset['status'] = 'Preparing to install: This might take a while.'
		tar = tarfile.open(filename, 'r:gz')
		tar.extractall(path=extract_location, members = self.track_progress(tar, docset, len(tar.getmembers())))
		tar.close()
		os.remove(filename)
		if docset['name'] == 'Drupal 7':
			p = os.path.join(extract_location, 'Drupal.docset')
			n = 'Drupal7.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Drupal 8':
			p = os.path.join(extract_location, 'Drupal.docset')
			n = 'Drupal8.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Java SE6':
			p = os.path.join(extract_location, 'Java.docset')
			n = 'JavaSE6.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Java SE7':
			p = os.path.join(extract_location, 'Java.docset')
			n = 'JavaSE7.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Java SE8':
			p = os.path.join(extract_location, 'Java.docset')
			n = 'JavaSE8.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Lua 5.1':
			p = os.path.join(extract_location, 'Lua.docset')
			n = 'Lua51.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Lua 5.2':
			p = os.path.join(extract_location, 'Lua.docset')
			n = 'Lua52.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Lua 5.3':
			p = os.path.join(extract_location, 'Lua.docset')
			n = 'Lua53.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Qt 4':
			p = os.path.join(extract_location, 'Qt.docset')
			n = 'Qt4.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Qt 5':
			p = os.path.join(extract_location, 'Qt.docset')
			n = 'Qt5.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Ruby':
			p = os.path.join(extract_location, 'Ruby.docset')
			n = 'Ruby1.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Ruby 2':
			p = os.path.join(extract_location, 'Ruby.docset')
			n = 'Ruby2.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Ruby on Rails 3':
			p = os.path.join(extract_location, 'Ruby on Rails.docset')
			n = 'Ruby on Rails3.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Ruby on Rails 4':
			p = os.path.join(extract_location, 'Ruby on Rails.docset')
			n = 'Ruby on Rails4.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Ruby on Rails 5':
			p = os.path.join(extract_location, 'Ruby on Rails.docset')
			n = 'Ruby on Rails5.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Zend Framework 1':
			p = os.path.join(extract_location, 'Zend_Framework.docset')
			n = 'Zend_Framework1.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Zend Framework 2':
			p = os.path.join(extract_location, 'Zend_Framework.docset')
			n = 'Zend_Framework2.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		elif docset['name'] == 'Zend Framework 3':
			p = os.path.join(extract_location, 'Zend_Framework.docset')
			n = 'Zend_Framework3.docset'
			m = os.path.join(self.docsetFolder, n)
			b = os.path.join(extract_location, n)
			os.rename(p, b)
			shutil.move(b, m)
			shutil.rmtree(extract_location)
		
		self.indexDocset(docset, refresh_main_view)
	
	def track_progress(self, members, docset, totalFiles):
		i = 0
		for member in members:
			i = i + 1
			done = 100 * i / totalFiles
			docset['status'] = 'installing: ' + str(round(done,2)) + '% ' + str(i) + ' / '+ str(totalFiles) 
			yield member
	
	
	
	def indexDocset(self, docset, refresh_main_view):
		docset['status'] = 'indexing'
		self.postProcess(docset, refresh_main_view)
		
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
		sql = 'SELECT type FROM searchIndex GROUP BY type'
		c = conn.execute(sql)
		data = c.fetchall()
		conn.close()
		for t in data:
			types.append({'name':t[0], 'image':self.__getTypeIconWithName(t[0])})
		return types
	
	def getIndexesbyTypeForDocset(self, docset, type):
		indexes = []
		path = docset['path']
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type, name, path FROM searchIndex WHERE type = \'' + type['name'] + '\''
		c = conn.execute(sql)
		data = c.fetchall()
		conn.close()
		for t in data:
			indexes.append({'type':{'name':t[0], 'image':self.__getTypeIconWithName(t[0])}, 'name':t[1],'path':t[2]})
		return indexes
	
	def getIndexesForDocset(self, docset):
		indexes = []
		path = docset['path']
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type, name, path FROM searchIndex'
		c = conn.execute(sql)
		data = c.fetchall()
		conn.close()
		for i in data:
			indexes.append({'type':{'name':t[0], 'image':self.__getTypeIconWithName(t[0])}, 'name':t[1],'path':t[2]})
		return types
	
	def deleteDocset(self, docset, post_action):
		but = console.alert('Are you sure?', 'Would you like to delete the docset, ' + docset['name'], 'Ok')
		if but == 1:
			shutil.rmtree(docset['path'])
			docset['status'] = 'online'
			post_action()
			docset['path'] = None
		
if __name__ == '__main__':
	dm = DocsetManager()
	print((dm.getAvailableDocsets()))
	

