import os
import sqlite3
import urllib
import requests
import ui
from PIL import Image


from Managers import TypeManager
class WebSearchManager (object):
	def __init__(self, typeIconPath):
		self.docsetFolder = 'Docsets/WebSearch'
		self.docsetIndexFileName = os.path.join(self.docsetFolder, 'WebSearch.db')
		self.typeManager = TypeManager.TypeManager(typeIconPath)
		self.connection = None
		self.__createDocsetFolder()
		self.__createInitialIndex()
	
	def __createDocsetFolder(self):
		if not os.path.exists(self.docsetFolder):
			os.mkdir(self.docsetFolder)
	
	def __createInitialIndex(self):
		initCreate = not os.path.exists(self.docsetIndexFileName)
		self.connection = sqlite3.connect(self.docsetIndexFileName)
		c = self.connection.cursor()
		c.execute('CREATE TABLE IF NOT EXISTS websearch(ID INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT NOT NULL, Url TEXT NOT NULL, Enabled Integer NOT NULL);')
		self.connection.commit()
		if initCreate:
			self.AddWebSearch('Google','https://www.google.com/search?q={query}')
			self.AddWebSearch('DuckDuckGo','https://duckduckgo.com/?q={query}&ia=web')
			self.AddWebSearch('Stack Overflow','https://stackoverflow.com/search?q={query}')
	
	def AddWebSearch(self, name, url):
		searches = self.GetWebSearches()
		for search in searches:
			if search[1] == name:
				return False, 'Name ' +name+' already exists in database, please choose another name.'
		parsedurl = urllib.parse.urlparse(url)
		scheme = parsedurl.scheme
		if scheme == '':
			return False, 'Invalid URL ' + url + ', No scheme found, please include a scheme, eg http://'
		hostName = parsedurl.netloc
		if hostName == '':
			return False, 'Invalid URL ' + url + ' no host name could be determined'
		faviconurl = scheme + '://' + hostName + '/favicon.ico'
		qurl = scheme + '://' + hostName + parsedurl.path +'?' + urllib.parse.quote(parsedurl.query,'/=&')
		qurl = qurl.replace('%7Bquery%7D','{query}')
		c = self.connection.cursor()
		c.execute('INSERT INTO websearch (Name, Url, Enabled) VALUES (?,?,?)',(name,qurl,1,))
		self.connection.commit()
		path = os.path.join(self.docsetFolder, str(c.lastrowid)+'.ico')
		try:
			r = requests.get(faviconurl, stream=True)
			if r.status_code == 200:
				with open(path, 'wb') as f:
					for chunk in r:
						f.write(chunk)
				basewidth = 48
				img = Image.open(path)
				wpercent = (basewidth/float(img.size[0]))
				hsize = int((float(img.size[1])*float(wpercent)))
				img = img.resize((basewidth,hsize), Image.ANTIALIAS)
				pathx = path.replace('.ico','')
				pathx = pathx + '@3x.ico'
				basewidth = 32
				img.save(pathx)
				img = Image.open(path)
				wpercent = (basewidth/float(img.size[0]))
				hsize = int((float(img.size[1])*float(wpercent)))
				img = img.resize((basewidth,hsize), Image.ANTIALIAS)
				pathx = path.replace('.ico','')
				pathx = pathx + '@2x.ico'
				img.save(pathx) 
				basewidth = 16
				img = Image.open(path)
				wpercent = (basewidth/float(img.size[0]))
				hsize = int((float(img.size[1])*float(wpercent)))
				img = img.resize((basewidth,hsize), Image.ANTIALIAS)
				img.save(path)
		except requests.RequestException as e:
			pass
		return True, ''
	
	def RemoveWebSearch(self, id):
		c = self.connection.cursor()
		c.execute('DELETE FROM websearch WHERE ID = (?)',(id,))
		self.connection.commit()
		path = os.path.join(self.docsetFolder, str(id))
		if os.path.exists(path+'.ico'):
			os.remove(path+'.ico')
		if os.path.exists(path+'@2x.ico'):
			os.remove(path+'@2x.ico')
		if os.path.exists(path+'@3x.ico'):
			os.remove(path+'@3x.ico')
	
	def GetWebSearches(self, OnlyEnabled=False):
		connection = sqlite3.connect(self.docsetIndexFileName)
		if not OnlyEnabled:
			return connection.execute('SELECT * FROM websearch').fetchall()
		else:
			return connection.execute('SELECT * FROM websearch WHERE Enabled = 1')
	
	def EnableWebSearch(self, id):
		c = self.connection.cursor()
		c.execute('UPDATE websearch SET Enabled = 1 WHERE id = (?)',(id,))
		self.connection.commit()
	
	def DisableWebSearch(self, id):
		c = self.connection.cursor()
		c.execute('UPDATE websearch SET Enabled = 0 WHERE id = (?)',(id,))
		self.connection.commit()
	
	def GetAllWebSearches(self, name):
		if name == None or name == '':
			return []
		else:
			searches = self.GetWebSearches(True)
			indexes = []
			for s in searches:
				ind = []
				n = urllib.parse.quote(name)
				url = s[2].replace('{query}', n)
				#url = url.replace(' ', '%20')
				type = None
				dTypes={}
				img = None
				imgPath = os.path.join(self.docsetFolder, str(s[0])+'.ico')
				if os.path.exists(imgPath):
					img = ui.Image.named(imgPath)
				if 'Entry' in dTypes.keys():
					type= dTypes['Entry']
				else:
					type = self.typeManager.getTypeForName('Entry')
					dTypes['Entry'] = type
				ind.append({'name':s[1], 'path':url, 'icon':img,'docsetname':s[1],'type':type, 'callbackOverride':'', 'docset': None})
				indexes.extend(ind)
			return indexes
		
