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
import datetime
from Managers import DBManager, TypeManager
from Utilities import LogThread

class StackOverflow (object):
	def __init__(self):
		self.__version = ''
		self.__name = ''
		self.__aliases = []
		self.__tags = []
		self.__keyword = ''
		self.__icon = None
		self.__id = ''
		self.__path = None
		self.__status = ''
		self.__stats = ''
		self.__onlineid = ''
		self.__type = ''
		
	@property
	def onlineid(self):
		return self.__onlineid
	
	@onlineid.setter
	def onlineid(self, id):
		self.__onlineid = id	
		
	@property
	def version(self):
		return self.__version
	
	@version.setter
	def version(self, version):
		self.__version = version
	
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
	def tags(self):
		return self.__aliases
	
	@tags.setter
	def tags(self, tags):
		self.__tags = tags
	
	@property
	def keyword(self):
		return self.__keyword
	
	@keyword.setter
	def keyword(self, keyword):
		self.__keyword = keyword
		
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
	def type(self):
		return self.__type
	
	@type.setter
	def type(self, type):
		self.__type = type
	
		
class StackOverflowManager (object):
	def __init__(self, serverManager, iconPath, typeIconPath):
		self.typeManager = TypeManager.TypeManager(typeIconPath)
		self.serverManager = serverManager
		self.iconPath = iconPath
		self.typeIconPath = typeIconPath
		self.localServer = None
		self.jsonServerLocation = 'zzz/stackoverflow/index.json'
		self.downloadServerLocation = 'zzz/stackoverflow/%@_%v.tgz'
		self.plistPath = 'Contents/Info.plist'
		self.indexPath = 'Contents/Resources/docSet.dsidx'
		self.stackoverflowFolder = 'Docsets/StackOverflow'
		self.headers = {'User-Agent': 'PyDoc-Pythonista'}
		self.stackoverflows = None
		self.downloading = []
		self.workThreads = []
		self.downloadThreads = []
		self.uiUpdateThreads = []
		self.__createStackOverflowFolder()
	
	def getAvailableStackOverflows(self):
		stackoverflows = self.__getOnlineStackOverflows()
		for d in self.__getDownloadedStackOverflows():
			for s in stackoverflows:
				if s.name+s.type == d.name:
					s.status = 'installed'
					s.path = d.path
					s.id = d.id
		for d in self.__getDownloadingStackOverflows():
			for s in stackoverflows:
				if s.name+s.type == d.name:
					s.status = d.status
					try:
						s.stats = d.stats
					except KeyError:
						s.stats = 'downloading'
		return stackoverflows
	
	def __getOnlineStackOverflows(self):
		if self.stackoverflows == None:
			self.stackoverflows = self.__getStackOverflows()
		return self.stackoverflows
	
	def __getDownloadedStackOverflows(self):
		ds = []
		dbManager = DBManager.DBManager()
		t = dbManager.InstalledDocsetsByType('stackoverflow')
		ds = []
		for d in t:
			aa = StackOverflow()
			aa.name = d[1]
			aa.id = d[0]
			aa.path = os.path.join(os.path.abspath('.'),d[2])
			aa.image = self.__getIconWithName(d[4])
			aa.type = d[6]
			ds.append(aa)
		return ds
	
	def __getDownloadingStackOverflows(self):
		return self.downloading
		
	def getDownloadedStackOverflows(self):
		return self.__getDownloadedStackOverflows()
		
	def __getStackOverflows(self):
		server = self.serverManager.getDownloadServer(self.localServer)
		url = server.url
		if not url[-1] == '/':
			url = url + '/'
		url = url + self.jsonServerLocation
		data = requests.get(url).text
		data = ast.literal_eval(data)
		stackoverflows = []
		onlineIcon = self.__getIconWithName('soonline')
		offlineIcon = self.__getIconWithName('sooffline')
		for k,d in data['docsets'].items():
			if 'online' in d['variants'].keys():
				s = StackOverflow()
				s.name = d['name']
				s.aliases = d['aliases']
				s.version = d['version']
				s.tags = d['tags']
				s.keyword = d['keyword']
				s.image = onlineIcon
				s.onlineid = k
				s.status = 'online'
				s.type = 'Online'
				stackoverflows.append(s)
			if 'offline' in d['variants'].keys():
				so = StackOverflow()
				so.name = d['name']
				so.aliases = d['aliases']
				so.version = d['version']
				so.tags = d['tags']
				so.keyword = d['keyword']
				so.image = offlineIcon
				so.onlineid = k
				so.status = 'online'
				so.type = 'Offline'
				stackoverflows.append(so)
		return sorted(stackoverflows, key=lambda x: x.name.lower())
	
	def __getIconWithName(self, name):
		imgPath = os.path.join(os.path.abspath('.'), self.iconPath, name+'.png')
		if not os.path.exists(imgPath):
			imgPath = os.path.join(os.path.abspath('.'), self.iconPath, 'Other.png')
		return ui.Image.named(imgPath)
	
	def __createStackOverflowFolder(self):
		if not os.path.exists(self.stackoverflowFolder):
			os.mkdir(self.stackoverflowFolder)
		
	def downloadStackOverflow(self, stackoverflow, action, refresh_main_view):
		if not stackoverflow in self.downloading:
			stackoverflow.status = 'downloading'
			self.downloading.append(stackoverflow)
			action()
			workThread = LogThread.LogThread(target=self.__determineUrlAndDownload, args=(stackoverflow,action,refresh_main_view,))
			self.workThreads.append(workThread)
			workThread.start()
	
	def __determineUrlAndDownload(self, stackoverflow, action, refresh_main_view):
		stackoverflow.stats = 'getting download link'
		action()
		downloadLink = self.__getDownloadLink(stackoverflow.onlineid, stackoverflow.type)
		downloadThread = LogThread.LogThread(target=self.downloadFile, args=(downloadLink,stackoverflow,refresh_main_view,))
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
	
	def __getDownloadLink(self, id, type):
		server = self.serverManager.getDownloadServer(self.localServer)
		url = server.url
		if not url[-1] == '/':
			url = url + '/'
		url = url + self.downloadServerLocation
		url = url.replace('%@', id)
		url = url.replace('%v', type)
		return url
	
	def downloadFile(self, url, stackoverflow, refresh_main_view):
		local_filename = self.__downloadFile(url, stackoverflow)
		stackoverflow.status = 'waiting for install'
		self.installStackOverflow(local_filename, stackoverflow, refresh_main_view)
	
	def __downloadFile(self, url, stackoverflow):
		local_filename = self.stackoverflowFolder+'/'+url.split('/')[-1]
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
							stackoverflow.stats = str(round(done,2)) + '% ' + str(self.convertSize(dl)) + ' / '+ str(self.convertSize(float(total_length)))
						else:
							 stackoverflow.stats = str(self.convertSize(dl))
		r.close()	
		return ret		
		
	def installStackOverflow(self, filename, stackoverflow, refresh_main_view):
		extract_location = self.stackoverflowFolder
		stackoverflow.status = 'Preparing to install: This might take a while.'
		tar = tarfile.open(filename, 'r:gz')
		n = [name for name in tar.getnames() if '/' not in name][0]
		m = os.path.join(self.stackoverflowFolder, n)
		tar.extractall(path=extract_location, members = self.track_progress(tar, stackoverflow, len(tar.getmembers())))
		tar.close()
		os.remove(filename)
		dbManager = DBManager.DBManager()
		icon = 'soonline'
		if stackoverflow.type == 'Offline':
			icon = 'sooffline'
		dbManager.DocsetInstalled(stackoverflow.name+stackoverflow.type, m, 'stackoverflow', icon, stackoverflow.version, stackoverflow.type)
		if stackoverflow in self.downloading:
			self.downloading.remove(stackoverflow)
		self.indexStackOverflow(stackoverflow, refresh_main_view, m)
	
	def track_progress(self, members, stackoverflow, totalFiles):
		i = 0
		for member in members:
			i = i + 1
			done = 100 * i / totalFiles
			stackoverflow.status = 'installing: ' + str(round(done,2)) + '% ' + str(i) + ' / '+ str(totalFiles) 
			yield member
	
	def indexStackOverflow(self, stackoverflow, refresh_main_view, path):
		stackoverflow.status = 'indexing'
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
		conn.close()
		self.postProcess(stackoverflow, refresh_main_view)
		
	def postProcess(self, stackoverflow, refresh_main_view):
		stackoverflow.status = 'installed'
		refresh_main_view()

	def convertSize(self, size):
		if (size == 0):
			return '0B'
		size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
		i = int(math.floor(math.log(size,1024)))
		p = math.pow(1024,i)
		s = round(size/p,2)
		return '%s %s' % (s,size_name[i])
	
	def deleteStackOverflow(self, stackoverflow, post_action):
		but = console.alert('Are you sure?', 'Would you like to delete the docset, ' +  stackoverflow.name, 'Ok')
		if but == 1:
			dbmanager = DBManager.DBManager()
			dbmanager.DocsetRemoved(stackoverflow.id)
			shutil.rmtree(stackoverflow.path)
			stackoverflow.status = 'online'
			post_action()
			stackoverflow.path = None
	
	def getTypesForStackOverflow(self, stackoverflow):
		types = []
		path = stackoverflow.path
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type FROM searchIndex GROUP BY type ORDER BY type COLLATE NOCASE'
		c = conn.execute(sql)
		data = c.fetchall()
		conn.close()
		for t in data:
			types.append(self.typeManager.getTypeForName(t[0]))
		return types
	
	def getIndexesbyTypeForStackOverflow(self, stackoverflow, type):
		indexes = []
		path = stackoverflow.path
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type, name, path FROM searchIndex WHERE type = (?) ORDER BY name COLLATE NOCASE'
		c = conn.execute(sql, (type.name,))
		data = c.fetchall()
		conn.close()
		for t in data:
			indexes.append({'type':self.typeManager.getTypeForName(t[0]), 'name':t[1],'path':t[2]})
		return indexes
	
	def getIndexesbyTypeAndNameForDocset(self, stackoverflow, typeName, name):
		indexes = []
		path = stackoverflow.path
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type, name, path FROM searchIndex WHERE type = (?) AND name LIKE (?) ORDER BY name COLLATE NOCASE'
		c = conn.execute(sql, (typeName, name,))
		data = c.fetchall()
		conn.close()
		for t in data:
			indexes.append({'type':self.typeManager.getTypeForName(t[0]), 'name':t[1],'path':t[2]})
		return indexes
		
	def getIndexesByNameForDocset(self, stackoverflow, name):
		indexes = []
		path = stackoverflow.path
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type, name, path FROM searchIndex WHERE name LIKE (?) ORDER BY name COLLATE NOCASE'
		c = conn.execute(sql, (name,))
		data = c.fetchall()
		conn.close()
		for t in data:
			indexes.append({'type':self.typeManager.getTypeForName(t[0]), 'name':t[1],'path':t[2]})
		return indexes
	
	def getIndexesForStackOverflow(self, stackoverflow):
		indexes = []
		path = stackoverflow.path
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type, name, path FROM searchIndex ORDER BY name COLLATE NOCASE'
		c = conn.execute(sql)
		data = c.fetchall()
		conn.close()
		for i in data:
			indexes.append({'type':self.typeManager.getTypeForName(t[0]), 'name':t[1],'path':t[2]})
		return types
		
	def getIndexesbyNameForAllStackOverflow(self, name):
		if name == None or name == '':
			return []
		else:
			name = '%'+name+'%'
			docsets = self.getDownloadedStackOverflows()
			indexes = []
			for d in docsets:
				ind = []
				path = d.path
				indexPath = os.path.join(path, self.indexPath)
				conn = sqlite3.connect(indexPath)
				sql = 'SELECT type, name, path FROM searchIndex WHERE name LIKE (?) OR name LIKE (?) ORDER BY name COLLATE NOCASE'
				c = conn.execute(sql, (name, name.replace(' ','%'),))
				data = c.fetchall()
				conn.close()
				dTypes = {}
				for t in data:
					callbackOverride = ''
					if d.type == 'Online':
						url = t[2]
						url = url.replace(' ', '%20')
					else:
						url = t[2]
						callbackOverride = 'sooffline'
					type = None
					if t[0] in dTypes.keys():
						type= dTypes[t[0]]
					else:
						type = self.typeManager.getTypeForName(t[0])
						dTypes[t[0]] = type
					head, _sep, tail = d.name.rpartition(d.type)
					ind.append({'name':t[1], 'path':url, 'icon':d.image,'docsetname':head+tail,'type':type, 'callbackOverride': callbackOverride, 'docset': d})
				indexes.extend(ind)
			return indexes
			
	def getIndexesbyNameForDocset(self, docset, name):
		if name == None or name == '':
			return []
		else:
			name = '%'+name+'%'
			ind = []
			path = docset.path
			indexPath = os.path.join(path, self.indexPath)
			conn = sqlite3.connect(indexPath)
			sql = 'SELECT type, name, path FROM searchIndex WHERE name LIKE (?) OR name LIKE (?) ORDER BY name COLLATE NOCASE'
			c = conn.execute(sql, (name, name.replace(' ','%'),))
			data = c.fetchall()
			conn.close()
			dTypes = {}
			for t in data:
				callbackOverride = ''
				if docset.type == 'Online':
					url = t[2]
					url = url.replace(' ', '%20')
				else:
					url = t[2]
					callbackOverride = 'sooffline'
				type = None
				if t[0] in dTypes.keys():
					type= dTypes[t[0]]
				else:
					type = self.typeManager.getTypeForName(t[0])
					dTypes[t[0]] = type
				head, _sep, tail = docset.name.rpartition(docset.type)
				ind.append({'name':t[1], 'path':url, 'icon':docset.image,'docsetname':head + tail,'type':type, 'callbackOverride':callbackOverride, 'docset': docset})
			return ind
	
	def buildOfflineDocsetHtml(self, entry, docset):
		indexPath = os.path.join(docset.path, self.indexPath)
		id = entry['path'].split('#',1)[0].replace('dash-stack://','')
		conn = sqlite3.connect(indexPath)
		questionSql = 'SELECT body, score, owneruserid, creationdate, acceptedanswerid FROM Posts WHERE ID = (?)'
		c = conn.execute(questionSql, (id,))
		question = c.fetchall()[0]

		questionUserSql = 'SELECT DisplayName, AccountId FROM Users WHERE ID = (?)'
		c = conn.execute(questionUserSql, (question[2],))
		questionUser = c.fetchall()[0]		

		acceptedAnswerSql = 'SELECT body, id, score, owneruserid, creationdate FROM Posts WHERE Id = (?)'
		c = conn.execute(acceptedAnswerSql, (question[4],))
		acceptedAnswer = c.fetchall()
		
		
		answerSql = 'SELECT body, id, score, owneruserid, creationdate FROM Posts WHERE ParentId = (?) and id != (?)'
		c = conn.execute(answerSql, (id,question[4],))
		answers = c.fetchall()
		
		commentsSql = 'SELECT text, creationdate, userid FROM comments WHERE PostId = (?) ORDER BY creationdate'
		
		with open('Resources/header.html', 'rb') as f:
			header = f.read().decode('utf8')

		with open('Resources/body.html', 'rb') as f:
			bodyTemplate = f.read().decode('utf8')
		
		with open('Resources/answers.html', 'rb') as f:
			answerTemplate = f.read().decode('utf8')
		
		with open('Resources/AcceptedAnswer.html', 'rb') as f:
			acceptedAnswerTemplate = f.read().decode('utf8')
		
		with open('Resources/comments.html', 'rb') as f:
			commentsTemplate = f.read().decode('utf8')
		
		questionTime = time.strftime('%d-%b-%Y at %H:%M:%S', time.gmtime(question[3]))
			
		body = header
		body += bodyTemplate.replace('{{{PostBody}}}', question[0]).replace('{{{Title}}}', entry['name']).replace('{{{AnswerCount}}}', str(len(answers)+len(acceptedAnswer))).replace('{{{Id}}}', str(id)).replace('{{{PostScore}}}', str(question[1])).replace('{{{PostOwnerDisplayName}}}', str(questionUser[0])).replace('{{{PostOwnerId}}}', str(question[2])).replace('{{{PostDateTime}}}', str(questionTime))
		
		answerData = ''
		if len(acceptedAnswer) > 0:
			aad = acceptedAnswer[0]
			acceptedAnswerTime = time.strftime('%d-%b-%Y at %H:%M:%S', time.gmtime(aad[4]))
			c = conn.execute(questionUserSql, (aad[3],))
			acceptedAnswerUser = c.fetchall()[0]
			c = conn.execute(commentsSql, (aad[1],))
			comments = c.fetchall()
			commentData = ''
			for comment in comments:
				c = conn.execute(questionUserSql, (comment[2],))
				commentUser = c.fetchall()[0]
				commentTime = time.strftime('%d-%b-%Y at %H:%M:%S', time.gmtime(comment[1]))
				commentData += commentsTemplate.replace('{{{CommentBody}}}', comment[0]).replace('{{{CommentOwnerId}}}', str(comment[2])).replace('{{{CommentDisplayname}}}',commentUser[0]).replace('{{{CommentDateTime}}}',str(commentTime))
			aa = answerTemplate.replace('{{{AnswerScore}}}', str(aad[2])).replace('{{{AcceptedAnswer}}}', acceptedAnswerTemplate).replace('{{{AnswerDateTime}}}', str(acceptedAnswerTime)).replace('{{{AnswerBody}}}', aad[0]).replace('{{{AnswerDisplayName}}}',acceptedAnswerUser[0]).replace('{{{AnswerOwnerId}}}', str(aad[3])).replace('{{{Comments}}}', commentData)
			answerData = aa
		for answer in answers:
			answerTime = time.strftime('%d-%b-%Y at %H:%M:%S', time.gmtime(answer[4]))
			c = conn.execute(questionUserSql, (answer[3],))
			answerUser = c.fetchall()[0]
			c = conn.execute(commentsSql, (answer[1],))
			comments = c.fetchall()
			commentData = ''
			for comment in comments:
				c = conn.execute(questionUserSql, (comment[2],))
				commentUser = c.fetchall()[0]
				commentTime = time.strftime('%d-%b-%Y at %H:%M:%S', time.gmtime(comment[1]))
				commentData += commentsTemplate.replace('{{{CommentBody}}}', comment[0]).replace('{{{CommentOwnerId}}}', str(comment[2])).replace('{{{CommentDisplayname}}}',commentUser[0]).replace('{{{CommentDateTime}}}',str(commentTime))
			answerData += answerTemplate.replace('{{{AnswerScore}}}', str(answer[2])).replace('{{{AcceptedAnswer}}}', ' ').replace('{{{AnswerDateTime}}}', str(answerTime)).replace('{{{AnswerBody}}}', answer[0]).replace('{{{AnswerDisplayName}}}',answerUser[0]).replace('{{{AnswerOwnerId}}}', str(answer[3])).replace('{{{Comments}}}', commentData)
			
			
		body += answerData
		body += '</body></html>'
		conn.close()
		# return '<html><body>' + body + '</body</html>' 
		return body
		
if __name__ == '__main__':
	import ServerManager
	c = StackOverflowManager(ServerManager.ServerManager(), '../Images/icons')
		
