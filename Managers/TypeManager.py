import json
import os
import ui

class Type (object):
	def __init__(self):
		self.__name = ''
		self.__plural = ''
		self.__aliases = []
		self.__icon = None

	@property
	def name(self):
		return self.__name
	
	@name.setter
	def name(self, data):
		self.__name = data

	@property
	def plural(self):
		return self.__plural
	
	@plural.setter
	def plural(self, data):
		self.__plural = data

	@property
	def aliases(self):
		return self.__aliases
	
	@aliases.setter
	def aliases(self, data):
		self.__aliases = data

	@property
	def icon(self):
		return self.__icon
	
	@icon.setter
	def icon(self, data):
		self.__icon = data

class TypeManager (object):
	def __init__(self, typeIconPath):
		self.typeIconPath = typeIconPath
		self.types = self.__setup()
		
	def __setup(self):
		with open('types.json') as json_data:
			data = json.load(json_data)
			types = []
			for ty in data:
				t = Type()
				t.name = ty['name']
				t.plural = ty['plural']
				if 'aliases' in ty:
					t.aliases = ty['aliases']
				t.icon = self.__getTypeIconWithName(ty['name'])
				types.append(t)
			return types
			
	def __getTypeIconWithName(self, name):
		imgPath = os.path.join(os.path.abspath('.'), self.typeIconPath, name+'.png')
		if not os.path.exists(imgPath):
			imgPath = os.path.join(os.path.abspath('.'), self.typeIconPath, 'Unknown.png')
		return ui.Image.named(imgPath)
	
	def getTypeForName(self, name):
		for type in self.types:
			if type.name == name:
				return type
		for type in self.types:
			if name in type.aliases:
				return type
