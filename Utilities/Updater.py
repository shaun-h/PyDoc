import requests
import json
from distutils.version import LooseVersion
import zipfile
import os
import shutil
from io import BytesIO
import console
import ui

class release (object):
	def __init__(self, j = None): 
		self.__url = '' 
		self.__assets_url = '' 
		self.__upload_url = '' 
		self.__html_url = '' 
		self.__id = 0 
		self.__tag_name = '' 
		self.__target_commitish = '' 
		self.__name = '' 
		self.__draft = True 
		self.__author = None 
		self.__prerelease = True 
		self.__created_at = '' 
		self.__published_at = '' 
		self.__assets = [] 
		self.__tarball_url = '' 
		self.__zipball_url = '' 
		self.__body = '' 

		if not j == None:
			self.url = j['url'] 
			self.assets_url = j['assets_url'] 
			self.upload_url = j['upload_url'] 
			self.html_url = j['html_url'] 
			self.id = j['id'] 
			self.tag_name = j['tag_name'] 
			self.target_commitish = j['target_commitish'] 
			self.name = j['name'] 
			self.draft = j['draft'] 
			self.author = j['author'] 
			self.prerelease = j['prerelease'] 
			self.created_at = j['created_at'] 
			self.published_at = j['published_at'] 
			self.assets = j['assets'] 
			self.tarball_url = j['tarball_url'] 
			self.zipball_url = j['zipball_url'] 
			self.body = j['body'] 

		@property
		def url(self):
			return self.__url

		@url.setter
		def url(self, obj):
			self.__url = obj

		@property
		def assets_url(self):
			return self.__assets_url

		@assets_url.setter
		def assets_url(self, obj):
			self.__assets_url = obj

		@property
		def upload_url(self):
			return self.__upload_url

		@upload_url.setter
		def upload_url(self, obj):
			self.__upload_url = obj

		@property
		def html_url(self):
			return self.__html_url

		@html_url.setter
		def html_url(self, obj):
			self.__html_url = obj

		@property
		def id(self):
			return self.__id

		@id.setter
		def id(self, obj):
			self.__id = obj

		@property
		def tag_name(self):
			return self.__tag_name

		@tag_name.setter
		def tag_name(self, obj):
			self.__tag_name = obj

		@property
		def target_commitish(self):
			return self.__target_commitish

		@target_commitish.setter
		def target_commitish(self, obj):
			self.__target_commitish = obj

		@property
		def name(self):
			return self.__name

		@name.setter
		def name(self, obj):
			self.__name = obj

		@property
		def draft(self):
			return self.__draft

		@draft.setter
		def draft(self, obj):
			self.__draft = obj

		@property
		def author(self):
			return self.__author

		@author.setter
		def author(self, obj):
			self.__author = author(obj)

		@property
		def prerelease(self):
			return self.__prerelease

		@prerelease.setter
		def prerelease(self, obj):
			self.__prerelease = obj

		@property
		def created_at(self):
			return self.__created_at

		@created_at.setter
		def created_at(self, obj):
			self.__created_at = obj

		@property
		def published_at(self):
			return self.__published_at

		@published_at.setter
		def published_at(self, obj):
			self.__published_at = obj

		@property
		def assets(self):
			return self.__assets

		@assets.setter
		def assets(self, obj):
			self.__assets = obj

		@property
		def tarball_url(self):
			return self.__tarball_url

		@tarball_url.setter
		def tarball_url(self, obj):
			self.__tarball_url = obj

		@property
		def zipball_url(self):
			return self.__zipball_url

		@zipball_url.setter
		def zipball_url(self, obj):
			self.__zipball_url = obj

		@property
		def body(self):
			return self.__body

		@body.setter
		def body(self, obj):
			self.__body = obj


class author (object):
	def __init__(self, j = None): 
		self.__login = '' 
		self.__id = 0 
		self.__avatar_url = '' 
		self.__gravatar_id = '' 
		self.__url = '' 
		self.__html_url = '' 
		self.__followers_url = '' 
		self.__following_url = '' 
		self.__gists_url = '' 
		self.__starred_url = '' 
		self.__subscriptions_url = '' 
		self.__organizations_url = '' 
		self.__repos_url = '' 
		self.__events_url = '' 
		self.__received_events_url = '' 
		self.__type = '' 
		self.__site_admin = True 

		if not j == None:
			self.login = j['login'] 
			self.id = j['id'] 
			self.avatar_url = j['avatar_url'] 
			self.gravatar_id = j['gravatar_id'] 
			self.url = j['url'] 
			self.html_url = j['html_url'] 
			self.followers_url = j['followers_url'] 
			self.following_url = j['following_url'] 
			self.gists_url = j['gists_url'] 
			self.starred_url = j['starred_url'] 
			self.subscriptions_url = j['subscriptions_url'] 
			self.organizations_url = j['organizations_url'] 
			self.repos_url = j['repos_url'] 
			self.events_url = j['events_url'] 
			self.received_events_url = j['received_events_url'] 
			self.type = j['type'] 
			self.site_admin = j['site_admin'] 

		@property
		def login(self):
			return self.__login

		@login.setter
		def login(self, obj):
			self.__login = obj

		@property
		def id(self):
			return self.__id

		@id.setter
		def id(self, obj):
			self.__id = obj

		@property
		def avatar_url(self):
			return self.__avatar_url

		@avatar_url.setter
		def avatar_url(self, obj):
			self.__avatar_url = obj

		@property
		def gravatar_id(self):
			return self.__gravatar_id

		@gravatar_id.setter
		def gravatar_id(self, obj):
			self.__gravatar_id = obj

		@property
		def url(self):
			return self.__url

		@url.setter
		def url(self, obj):
			self.__url = obj

		@property
		def html_url(self):
			return self.__html_url

		@html_url.setter
		def html_url(self, obj):
			self.__html_url = obj

		@property
		def followers_url(self):
			return self.__followers_url

		@followers_url.setter
		def followers_url(self, obj):
			self.__followers_url = obj

		@property
		def following_url(self):
			return self.__following_url

		@following_url.setter
		def following_url(self, obj):
			self.__following_url = obj

		@property
		def gists_url(self):
			return self.__gists_url

		@gists_url.setter
		def gists_url(self, obj):
			self.__gists_url = obj

		@property
		def starred_url(self):
			return self.__starred_url

		@starred_url.setter
		def starred_url(self, obj):
			self.__starred_url = obj

		@property
		def subscriptions_url(self):
			return self.__subscriptions_url

		@subscriptions_url.setter
		def subscriptions_url(self, obj):
			self.__subscriptions_url = obj

		@property
		def organizations_url(self):
			return self.__organizations_url

		@organizations_url.setter
		def organizations_url(self, obj):
			self.__organizations_url = obj

		@property
		def repos_url(self):
			return self.__repos_url

		@repos_url.setter
		def repos_url(self, obj):
			self.__repos_url = obj

		@property
		def events_url(self):
			return self.__events_url

		@events_url.setter
		def events_url(self, obj):
			self.__events_url = obj

		@property
		def received_events_url(self):
			return self.__received_events_url

		@received_events_url.setter
		def received_events_url(self, obj):
			self.__received_events_url = obj

		@property
		def type(self):
			return self.__type

		@type.setter
		def type(self, obj):
			self.__type = obj

		@property
		def site_admin(self):
			return self.__site_admin

		@site_admin.setter
		def site_admin(self, obj):
			self.__site_admin = obj
	
		
class Updater (object):
	def __init__(self):
		self.latestReleaseUrl = 'https://api.github.com/repos/shaun-h/pydoc/releases/latest'
		self.releasesUrl = 'https://api.github.com/repos/shaun-h/pydoc/releases'
		if os.path.exists('.version'):
			f = open('.version', 'r')
			self.currentVersion = f.read()
			f.close()
		else:
			self.currentVersion = '0'
			f = open('.version', 'w')
			f.write(self.currentVersion)
			f.close()
	
	@ui.in_background
	def checkForUpdate(self):
		try:
			console.show_activity('Checking for update...')
			response = requests.get(self.latestReleaseUrl)
			data = json.loads(response.text)
			rel = release(data)
			console.hide_activity()
			if rel.prerelease == False:
				if LooseVersion(self.currentVersion) < LooseVersion(rel.tag_name.replace('v','')):
					ret = console.alert('Update available', rel.tag_name + ' is available, would you like to install it', hide_cancel_button=True, button1 = 'No', button2 = 'Yes')
					if ret == 2:
						self.install(rel)				
				else:
					console.alert('No update available', 'v' + self.currentVersion + 'is the current version.', hide_cancel_button=True, button1 = 'Ok')
		except requests.exceptions.ConnectionError as e:
			console.alert('Check your internet connection', 'Unable to check for update.', hide_cancel_button=True, button1 = 'Ok')
	
	def install(self, release):
		console.show_activity('Installing ' + release.tag_name)
		request = requests.get(release.zipball_url)
		file = zipfile.ZipFile(BytesIO(request.content))
		toRemove = file.namelist()[0]
			
		filelist = [f for f in os.listdir('.') if not f == 'Docsets']
		for f in filelist:
			if os.path.isdir(f):
				shutil.rmtree(f)
			else:
				os.remove(f)
		file.extractall()
		for filename in os.listdir(toRemove):
			shutil.move(os.path.join(toRemove, filename), filename)
		shutil.rmtree(toRemove)
		file.close()
		
		f = open('.version', 'w')
		f.write(release.tag_name.replace('v',''))
		f.close()
		console.hide_activity()
		console.alert('Installed', release.tag_name + ' installed, please restart PyDoc', hide_cancel_button=True, button1 = 'Ok')
		
	def ignoreUpdate(self):
		pass
	
	def reinstallCurrentVersion(self):
		print('Reinstall current version')
	
	def showAvailableVersions(self):
		print('Show available versions')
		
if __name__ == '__main__':
	if os.path.exists('.version'):
		os.remove('.version')
	
	u = Updater()
	u.checkForUpdate()
