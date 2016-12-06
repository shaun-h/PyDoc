import json
import os

class Docset(object):
	def __init__(self):
		self.displayName = ''
		self.downloaded = False
		
class DocsetManager (object):
	def __init__(self):
		self.docsets = []
		self.downloading = []
		self.docsetFolder = 'Docsets'
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
				feeds.append(f)
			return feeds
		
	def getAvailableDocsets(self):
		docsets = self.__getDownloadedDocsets()
		for d in self.__getDownloadingDocsets():
			add = True
			for c in docsets:
				if c['name'] == d['name']:
					add = False
			if add:
				docsets.append(d)
		for d in self.__getOnlineDocsets():
			add = True
			for c in docsets:
				if c['name'] == d['name']:
					add = False
			if add:
				docsets.append(d)
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
	
	def downloadDocset(self, docset):
		if not docset in self.downloading:
			docset['status'] = 'downloading'
			self.downloading.append(docset)
		
				
if __name__ == '__main__':
	dm = DocsetManager()
	print(dm.getAvailableDocsets())
	

