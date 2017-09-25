import os
import json 
from glob import glob

class Theme (object):
	def __init__(self, j = None):
		self.__backgroundColour = ''
		self.__tintColour = ''
		self.__toolbarBackgroundColour = ''
		self.__invertWebView = False
		self.__themeName = ''
		self.__textColour = ''
		self.__subTextColour = ''
		if not j == None:
			self.backgroundColour = j['BackgroundColour']
			self.tintColour = j['TintColour']
			self.toolbarBackgroundColour = j['ToolbarBackgroundColour']
			self.invertWebView = j['InvertWebView']
			self.themeName = j['ThemeName']
			self.textColour = j['TextColour']
			self.subTextColour = j['SubTextColour']

	@property
	def textColour(self):
		return self.__textColour
	
	@textColour.setter
	def textColour(self, obj):
		self.__textColour = obj

	@property
	def subTextColour(self):
		return self.__subTextColour
	
	@subTextColour.setter
	def subTextColour(self, obj):
		self.__subTextColour = obj
														
	@property
	def backgroundColour(self):
		return self.__backgroundColour
	
	@backgroundColour.setter
	def backgroundColour(self, obj):
		self.__backgroundColour = obj
		
	@property
	def tintColour(self):
		return self.__tintColour
	
	@tintColour.setter
	def tintColour(self, obj):
		self.__tintColour = obj
	
	@property
	def toolbarBackgroundColour(self):
		return self.__toolbarBackgroundColour
	
	@toolbarBackgroundColour.setter
	def toolbarBackgroundColour(self, obj):
		self.__toolbarBackgroundColour = obj
		
	@property
	def invertWebView(self):
		return self.__invertWebView

	@invertWebView.setter
	def invertWebView(self, obj):
		self.__invertWebView = obj

	@property
	def themeName(self):
		return self.__themeName
	
	@themeName.setter
	def themeName(self, obj):
		self.__themeName = obj

class ThemeManager (object):
	def __init__(self, themesfolder):
		self.themes = self.getThemes(themesfolder)
		self.themeFileName = self.getThemeToUse(themesfolder) 
		self.currentTheme = self.themes[self.themeFileName]
	
	def setThemeToUse(self, themeFileName):
		self.themeFileName = themeFileName
		self.currentTheme = self.themes[themeFileName]
		self.saveCurrentThemeToUse()
		
	def getThemeToUse(self, themesfolder):
		themeConfigPath = os.path.join(themesfolder, '.themesConfig')
		if not os.path.exists(themeConfigPath):
			self.saveThemeToUse('Midnight.json')
		with open(themeConfigPath, 'r') as config:
			name = config.read()
		return name
	
	def saveCurrentThemeToUse(self, themesfolder):
		themeConfigPath = os.path.join(themesfolder, '.themesConfig')
		if os.path.exists(themeConfigPath):
			os.remove(themeConfigPath)
		with open(themeConfigPath, 'w') as config:
			config.write(self.themeFileName)
	
	def saveThemeToUse(self, themesfolder, themeFileName):
		themeConfigPath = os.path.join(themesfolder, '.themesConfig')
		if os.path.exists(themeConfigPath):
			os.remove(themeConfigPath)
		with open(themeConfigPath, 'w') as config:
			config.write(themeFileName)

	def getThemes(self, folder):
		themes = {}
		folders = glob(os.path.join(folder, '*.json')) 
		for fullFilePath in folders:
			if os.path.isfile(fullFilePath):
				with open(fullFilePath , 'r') as data_file:
					data = json.load(data_file)
					themes[os.path.basename(fullFilePath)] = Theme(data)
		return themes
		
if __name__ == '__main__':
	tm = ThemeManager('../Themes')	
	
	
