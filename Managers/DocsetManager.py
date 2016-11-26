import json

class Docset(object):
	def __init__(self):
		self.displayName = ''
		self.downloaded = False
		
class DocsetManager (object):
	def __init__(self):
		self.docsets = []
		self.docsetFeeds = self.getDocsetFeeds()
		
	def getDocsetFeeds(self):
		with open('feeds.json') as json_data:
			data = json.load(json_data)
			feeds = []
			for feed in data:
				f = {'detailString':'',
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
		pass
	
	def getDownloadedDocsets(self):
		pass
		
	def getOnlineDocsets(self):
		pass
		
		
if __name__ == '__main__':
	dm = DocsetManager()
	

