import requests
from time import time

class Server (object):
	def __init__(self):
		self.__url = ''
		self.__latency = 1000
		
	@property
	def url(self):
		return self.__url
	
	@url.setter
	def url(self, url):
		self.__url = url
		
	@property
	def latency(self):
		return self.__latency
	
	@latency.setter
	def latency(self, latency):
		self.__latency = latency
	
	
		
class ServerManager (object):
	def __init__(self):
		self.headers = {
    'User-Agent': 'PyDoc-Pythonista'
    }
		self.__servers = []
		self.__dynamicServers = []
		self.__setupDefaultServers()
	
	def __setupDefaultServers(self):
		serverList = ['http://newyork.kapeli.com/feeds/', 'http://sanfrancisco.kapeli.com/feeds/', 'http://london.kapeli.com/feeds/']
		for server in serverList:
			s = Server()
			s.url = server
			self.__servers.append(s)
	
	def __addDynamicServers(self, serversUrls):
		for dynamicServerUrl in serversUrls:
			add = True
			for server in self.__dynamicServers:
				if dynamicServerUrl == server.url:
					add = False
			if add:
				s = Server()
				s.url = dynamicServerUrl
				self.__dynamicServers.append(s)
	
	def getDownloadServer(self, server = None):
		if not server == None:
			s = Server()
			s.url = server
			return s
		downloadServer = None
		self.updateServerLatency()
		for server in self.__servers:
			if downloadServer == None or server.latency < downloadServer.latency:
				downloadServer = server
		for server in self.__dynamicServers:
			if downloadServer == None or server.latency < downloadServer.latency:
				downloadServer = server
		return downloadServer
		
	def updateServerLatency(self):
		for server in self.__servers:
			server.latency = self.getServerLatency(server.url)
			#print(server.url)
			#print(server.latency)
		for server in self.__dynamicServers:
			server.latency = self.getServerLatency(server.url)
			#print(server.url)
			#print(server.latency)
	
	def getServerLatency(self, url):
		timebefore = time()
		urlToTest = url
		if not urlToTest.endswith('/'):
			urlToTest=urlToTest+'/'
		urlToTest = urlToTest+'latencyTest_v2.txt'
		req = requests.get(urlToTest, headers=self.headers)
		timeafter = time()
		if req.status_code == 200:
			loc = req.text.find('Extra mirrors: ') 
			if loc >= 0:
				extra = req.text[loc+15:].split(', ')
				self.__addDynamicServers(extra)
			return timeafter-timebefore
		else:
			return 1000
