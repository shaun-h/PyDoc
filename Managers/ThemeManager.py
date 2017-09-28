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
		self.__settingsCellColour = ''
		self.__borderColour = ''
		self.__separatorColor = ''
		self.__settingsBackgroundColour = ''
		self.__searchTintColour = ''
		self.__searchBackgroundColour = ''
		self.__cellSelectionColour = ''
		self.__settingsCellSelectionColour = ''
		self.__showCellSelection = True
		self.__showSettingsCellSelection = True
		
		if not j == None:
			self.backgroundColour = j['BackgroundColour']
			self.tintColour = j['TintColour']
			self.toolbarBackgroundColour = j['ToolbarBackgroundColour']
			self.invertWebView = j['InvertWebView']
			self.themeName = j['ThemeName']
			self.textColour = j['TextColour']
			self.subTextColour = j['SubTextColour']
			self.settingsCellColour = j['SettingsCellColour']
			self.borderColour = j['BorderColour']
			self.separatorColour = j['SeparatorColour']
			self.settingsBackgroundColour = j['SettingsBackgroundColour']
			self.searchTintColour = j['SearchTintColour']
			self.searchBackgroundColour = j['SearchBackgroundColour']
			self.cellSelectionColour = j['CellSelectionColour']
			self.settingsCellSelectionColour = j['SettingsCellSelectionColour']
			self.showCellSelection = j['ShowCellSelection']
			self.showSettingsCellSelection = j['ShowSettingsCellSelection']
			
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

	@property
	def settingsCellColour(self):
		return self.__settingsCellColour
	
	@settingsCellColour.setter
	def settingsCellColour(self, obj):
		self.__settingsCellColour = obj

	@property
	def borderColour(self):
		return self.__borderColour
	
	@borderColour.setter
	def borderColour(self, obj):
		self.__borderColour = obj

	@property
	def separatorColour(self):
		return self.__separatorColour
	
	@separatorColour.setter
	def separatorColour(self, obj):
		self.__separatorColour = obj
		
	@property
	def settingsBackgroundColour(self):
		return self.__settingsBackgroundColour
	
	@settingsBackgroundColour.setter
	def settingsBackgroundColour(self, obj):
		self.__settingsBackgroundColour = obj
		
	@property
	def searchTintColour(self):
		return self.__searchTintColour
	
	@searchTintColour.setter
	def searchTintColour(self, obj):
		self.__searchTintColour = obj
		
	@property
	def searchBackgroundColour(self):
		return self.__searchBackgroundColour
	
	@searchBackgroundColour.setter
	def searchBackgroundColour(self, obj):
		self.__searchBackgroundColour = obj

	@property
	def cellSelectionColour(self):
		return self.__cellSelectionColour
	
	@cellSelectionColour.setter
	def cellSelectionColour(self, obj):
		self.__cellSelectionColour = obj
		
	@property
	def settingsCellSelectionColour(self):
		return self.__settingsCellSelectionColour
	
	@settingsCellSelectionColour.setter
	def settingsCellSelectionColour(self, obj):
		self.__settingsCellSelectionColour = obj
		
	@property
	def showSettingsCellSelection(self):
		return self.__showSettingsCellSelection
	
	@showSettingsCellSelection.setter
	def showSettingsCellSelection(self, obj):
		self.__showSettingsCellSelection = obj
		
	@property
	def showCellSelection(self):
		return self.__showCellSelection
	
	@showCellSelection.setter
	def showCellSelection(self, obj):
		self.__showCellSelection = obj

class ThemeManager (object):
	def __init__(self, themesfolder):
		self.themesFolder = themesfolder
		self.themes = self.getThemes(themesfolder)
		self.themeFileName = self.getThemeToUse(themesfolder)
		try:
			self.currentTheme = self.themes[self.themeFileName]
		except KeyError:
			self.setThemeToUse('Default.json')
			self.themeFileName = self.getThemeToUse(themesfolder)	
			self.currentTheme = self.themes[self.themeFileName]
	
	def setThemeToUse(self, themeFileName):
		self.themeFileName = themeFileName
		self.currentTheme = self.themes[themeFileName]
		self.saveCurrentThemeToUse()
		
	def getThemeToUse(self, themesfolder):
		themeConfigPath = os.path.join(themesfolder, '.themesConfig')
		if not os.path.exists(themeConfigPath):
			self.saveThemeToUse('Default.json')
		with open(themeConfigPath, 'r') as config:
			name = config.read()
		return name
	
	def saveCurrentThemeToUse(self):
		themeConfigPath = os.path.join(self.themesFolder, '.themesConfig')
		if os.path.exists(themeConfigPath):
			os.remove(themeConfigPath)
		with open(themeConfigPath, 'w') as config:
			config.write(self.themeFileName)
	
	def saveThemeToUse(self, themeFileName):
		themeConfigPath = os.path.join(self.themesFolder, '.themesConfig')
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
	
	
