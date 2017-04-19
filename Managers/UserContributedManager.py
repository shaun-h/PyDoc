import requests
import re
import json
import ast
import os
import ui
import threading
import tarfile
import math
import time
import plistlib
import console
import shutil
import sqlite3
import base64
import clipboard

class UserContributed (object):
	def __init__(self):
		self.__version = ''
		self.__globalversion = ''
		self.__name = ''
		self.__aliases = []
		self.__icon = None
		self.__id = ''
		self.__path = None
		self.__status = ''
		self.__stats = ''
		self.__archive = ''
		self.__authorName = ''
		
	@property
	def version(self):
		return self.__version
	
	@version.setter
	def version(self, version):
		self.__version = version
	
	@property
	def globalversion(self):
		return self.__globalversion
	
	@globalversion.setter
	def globalversion(self, globalversion):
		self.__globalversion = globalversion
	
	@property
	def name(self):
		return self.__name
	
	@name.setter
	def name(self, name):
		self.__name = name
		
	@property
	def aliases(self):
		return self.__aliases
	
	@aliases.setter
	def aliases(self, aliases):
		self.__aliases = aliases
		
	@property
	def image(self):
		return self.__icon
	
	@image.setter
	def image(self, icon):
		self.__icon = icon
	
	@property
	def id(self):
		return self.__id
	
	@id.setter
	def id(self, id):
		self.__id = id	
	
	@property
	def path(self):
		return self.__path
	
	@path.setter
	def path(self, path):
		self.__path = path
		
	@property
	def status(self):
		return self.__status
	
	@status.setter
	def status(self, status):
		self.__status = status
		
	@property
	def stats(self):
		return self.__stats
	
	@stats.setter
	def stats(self, stats):
		self.__stats = stats
	
	@property
	def archive(self):
		return self.__archive
	
	@archive.setter
	def archive(self, archive):
		self.__archive = archive
	
	@property
	def authorName(self):
		return self.__authorName
	
	@authorName.setter
	def authorName(self, an):
		self.__authorName = an
		
class UserContributedManager (object):
	def __init__(self, serverManager, iconPath, typeIconPath):
		self.serverManager = serverManager
		self.iconPath = iconPath
		self.typeIconPath = typeIconPath
		self.localServer = None
		self.jsonServerLocation = 'zzz/user_contributed/build/index.json'
		self.downloadServerLocation = 'zzz/user_contributed/build/%@/%$'
		self.plistPath = 'Contents/Info.plist'
		self.indexPath = 'Contents/Resources/docSet.dsidx'
		self.userContributedFolder = 'Docsets/UserContributions'
		self.headers = {'User-Agent': 'PyDoc-Pythonista'}
		self.usercontributed = None
		self.downloading = []
		self.workThreads = []
		self.downloadThreads = []
		self.uiUpdateThreads = []
		self.__createUserContributedFolder()
	
	def getAvailableUserContributed(self):
		usercontributed = self.__getOnlineUserContributed()
		for d in self.__getDownloadedUserContributed():
			for c in usercontributed:
				if c.name == d['name']:
					c.status = 'installed'
					c.path = d['path']
		for d in self.__getDownloadingUserContributed():
			for c in usercontributed:
				if c.name == d.name:
					c.status = d.status
					try:
						c.stats = d.stats
					except KeyError:
						c.stats = 'downloading'
		return usercontributed
	
	def __getOnlineUserContributed(self):
		if self.usercontributed == None:
			self.usercontributed = self.__getUserContributed()
		return self.usercontributed
		
	def __getDownloadedUserContributed(self):
		ds = []
		folder = os.path.join(os.path.abspath('.'), self.userContributedFolder)
		for dir in os.listdir(folder):
			if os.path.isdir(os.path.join(folder,dir)):
				pl = plistlib.readPlist(
				os.path.join(folder,dir, self.plistPath))
				name = pl['CFBundleName']
				ds.append({'name':name,'path':os.path.join(folder,dir)})
		return ds
	
	def __getDownloadingUserContributed(self):
		return self.downloading
		
	def getDownloadedUserContributed(self):
		ds = []
		for dd in self.__getDownloadedUserContributed():
			for feed in self.__getOnlineUserContributed():
				if dd['name'] == feed.name:
					feed.path = dd['path']
					ds.append(feed)
		return ds
		
	def __getUserContributed(self):
		server = self.serverManager.getDownloadServer(self.localServer)
		url = server.url
		if not url[-1] == '/':
			url = url + '/'
		url = url + self.jsonServerLocation
		data = requests.get(url).text
		data = ast.literal_eval(data)
		usercontributed = []
		defaultIcon = self.__getIconWithName('Other')
		for k,d in data['docsets'].items():
			u = UserContributed()
			u.name = d['name']
			if 'aliases' in d.keys():
				u.aliases = d['aliases']
			u.version = d['version']
			u.archive = d['archive']
			u.authorName = d['author']['name']
			if 'icon' in d.keys():
				imgdata = base64.standard_b64decode(d['icon'])
				u.image = ui.Image.from_data(imgdata)
			else:
				u.image = defaultIcon
			u.id = k
			u.status = 'online'
			usercontributed.append(u)
		return usercontributed
	
	def __getIconWithName(self, name):
		imgPath = os.path.join(os.path.abspath('.'), self.iconPath, name+'.png')
		if not os.path.exists(imgPath):
			imgPath = os.path.join(os.path.abspath('.'), self.iconPath, 'Other.png')
		return ui.Image.named(imgPath)
	
	def __getTypeIconWithName(self, name):
		imgPath = os.path.join(os.path.abspath('.'), self.typeIconPath, name+'.png')
		if not os.path.exists(imgPath):
			imgPath = os.path.join(os.path.abspath('.'), self.typeIconPath, 'Unknown.png')
		return ui.Image.named(imgPath)
	
	def __createUserContributedFolder(self):
		if not os.path.exists(self.userContributedFolder):
			os.mkdir(self.userContributedFolder)
		
	def downloadUserContributed(self, usercontributed, action, refresh_main_view):
		if not usercontributed in self.downloading:
			usercontributed.status = 'downloading'
			self.downloading.append(usercontributed)
			action()
			workThread = threading.Thread(target=self.__determineUrlAndDownload, args=(usercontributed,action,refresh_main_view,))
			self.workThreads.append(workThread)
			workThread.start()
	
	def __determineUrlAndDownload(self, usercontributed, action, refresh_main_view):
		usercontributed.stats = 'getting download link'
		action()
		downloadLink = self.__getDownloadLink(usercontributed.id, usercontributed.archive)
		downloadThread = threading.Thread(target=self.downloadFile, args=(downloadLink,usercontributed,refresh_main_view,))
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
	
	def __getDownloadLink(self, id, archive):
		server = self.serverManager.getDownloadServer(self.localServer)
		url = server.url
		if not url[-1] == '/':
			url = url + '/'
		url = url + self.downloadServerLocation
		url = url.replace('%@', id)
		url = url.replace('%$', archive)
		return url
	
	def downloadFile(self, url, usercontributed, refresh_main_view):
		local_filename = self.__downloadFile(url, usercontributed)
		#self.__downloadFile(url+'.tarix', cheatsheet)
		usercontributed.status = 'waiting for install'
		self.installUserContributed(local_filename, usercontributed, refresh_main_view)
	
	def __downloadFile(self, url, usercontributed):
		local_filename = self.userContributedFolder+'/'+url.split('/')[-1]
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
							usercontributed.stats = str(round(done,2)) + '% ' + str(self.convertSize(dl)) + ' / '+ str(self.convertSize(float(total_length)))
						else:
							 usercontributed.stats = str(self.convertSize(dl))
		
		r.close()	
		return ret		
		
	def installUserContributed(self, filename, usercontributed, refresh_main_view):
		extract_location = self.userContributedFolder
		usercontributed.status = 'Preparing to install: This might take a while.'
		tar = tarfile.open(filename, 'r:gz')
		tar.extractall(path=extract_location, members = self.track_progress(tar, usercontributed, len(tar.getmembers())))
		tar.close()
		os.remove(filename)		
		self.indexUserContributed(usercontributed, refresh_main_view)
	
	def track_progress(self, members, usercontributed, totalFiles):
		i = 0
		for member in members:
			i = i + 1
			done = 100 * i / totalFiles
			usercontributed.status = 'installing: ' + str(round(done,2)) + '% ' + str(i) + ' / '+ str(totalFiles) 
			yield member
	
	def indexUserContributed(self, usercontributed, refresh_main_view):
		usercontributed.status = 'indexing'
		self.postProcess(usercontributed, refresh_main_view)
		
	def postProcess(self, usercontributed, refresh_main_view):
		usercontributed.status = 'installed'
		refresh_main_view()

	def convertSize(self, size):
		if (size == 0):
			return '0B'
		size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
		i = int(math.floor(math.log(size,1024)))
		p = math.pow(1024,i)
		s = round(size/p,2)
		return '%s %s' % (s,size_name[i])
	
	def deleteUserContributed(self, usercontributed, post_action):
		but = console.alert('Are you sure?', 'Would you like to delete the docset, ' +  usercontributed.name, 'Ok')
		if but == 1:
			shutil.rmtree(usercontributed.path)
			usercontributed.status = 'online'
			post_action()
			usercontributed.path = None
	
	def getTypesForUserContributed(self, usercontributed):
		types = []
		path = usercontributed.path
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type FROM searchIndex GROUP BY type'
		c = conn.execute(sql)
		data = c.fetchall()
		conn.close()
		for t in data:
			types.append({'name':t[0], 'image':self.__getTypeIconWithName(t[0])})
		return types
	
	def getIndexesbyTypeForUserContributed(self, usercontributed, type):
		indexes = []
		path = usercontributed.path
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type, name, path FROM searchIndex WHERE type = \'' + type['name'] + '\''
		c = conn.execute(sql)
		data = c.fetchall()
		conn.close()
		img = self.__getTypeIconWithName(type['name'])
		for t in data:
			indexes.append({'type':{'name':t[0], 'image':img}, 'name':t[1],'path':t[2]})
		return indexes
	
	def getIndexesForUserContributed(self, usercontributed):
		indexes = []
		path = usercontributed.path
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type, name, path FROM searchIndex'
		c = conn.execute(sql)
		data = c.fetchall()
		conn.close()
		for i in data:
			indexes.append({'type':{'name':t[0], 'image':self.__getTypeIconWithName(t[0])}, 'name':t[1],'path':t[2]})
		return types
		
if __name__ == '__main__':
	import ServerManager
	c = UserContributedManager(ServerManager.ServerManager(), '../Images/icons', '../Images/types')
	print(c.getAvailableUserContributed())
		
