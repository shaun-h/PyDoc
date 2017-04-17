import requests
import re
import json
import ast
import os
import ui

class Cheatsheet (object):
	def __init__(self):
		self.__version = ''
		self.__globalversion = ''
		self.__name = ''
		self.__aliases = []
		self.__icon = None
		
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
		
class CheatsheetManager (object):
	def __init__(self, serverManager, iconPath):
		self.serverManager = serverManager
		self.iconPath = iconPath
		self.localServer = None
		self.jsonServerLocation = 'zzz/cheatsheets/cheat.json'
		self.headers = {'User-Agent': 'PyDoc-Pythonista'}
		self.cheatsheets = None
	
	def getAvailableCheatsheets(self):
		if self.cheatsheets == None:
			self.cheatsheets = self.__getCheatsheets()
		return self.cheatsheets
		
	def __getCheatsheets(self):
		server = self.serverManager.getDownloadServer(self.localServer)
		url = server.url
		if not url[-1] == '/':
			url = url + '/'
		url = url + self.jsonServerLocation
		data = requests.get(url).text
		data = ast.literal_eval(data)
		
		cheatsheets = []
		icon = self.__getIconWithName('cheatsheet')
		for k,d in data['cheatsheets'].items():
			c = Cheatsheet()
			c.name = d['name']
			c.aliases = d['aliases']
			c.globalversion = data['global_version']
			c.version = d['version']
			c.image = icon
			cheatsheets.append(c)
		return cheatsheets
	
	def __getIconWithName(self, name):
		imgPath = os.path.join(os.path.abspath('.'), self.iconPath, name+'.png')
		return ui.Image.named(imgPath)
				
if __name__ == '__main__':
	import ServerManager
	c = CheatsheetManager(ServerManager.ServerManager(), '../Images/icons')
		
