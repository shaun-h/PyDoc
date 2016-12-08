import json
import os
import ui

class Docset(object):
	def __init__(self):
		self.displayName = ''
		self.downloaded = False
		
class DocsetManager (object):
	def __init__(self, iconPath):
		self.docsets = []
		self.downloading = []
		self.docsetFolder = 'Docsets'
		self.iconPath = iconPath
		self.__createDocsetFolder()
		self.docsetFeeds = self.__getDocsetFeeds()
		
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
		for d in self.__getDownloadingDocsets():
			for c in docsets:
				if c['name'] == d['name']:
					c['status'] = d['status']
		for d in self.__getDownloadedDocsets():
			for c in docsets:
				if c['name'] == d['name']:
					c['status'] = d['status']
		return docsets
	
	def __docsetFeedToDocset(self, feed):
		return feed
			
	def __getDownloadedDocsets(self):
		return []
	
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
	
	def downloadDocset(self, docset):
		if not docset in self.downloading:
			docset['status'] = 'downloading'
			self.downloading.append(docset)
		
				
if __name__ == '__main__':
	dm = DocsetManager()
	print(dm.getAvailableDocsets())
	

