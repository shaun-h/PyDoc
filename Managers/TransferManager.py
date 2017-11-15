from werkzeug.serving import make_server 
from flask import Flask, render_template, request, current_app
from Utilities import LogThread
import threading
import time
import socket
import sqlite3
import os
import plistlib
import console
import shutil
import ui
from zipfile import ZipFile
from Managers import DBManager, TypeManager

app = Flask('myapp')
app.debug = True

@app.route('/')
def index():
	return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_f():
	if request.method == 'POST':
		f = request.files['file']
		loc = current_app.config['fileuploaddir']
		f.save(os.path.join(loc, f.filename))
		return 'file uploaded successfully'
	
class ServerThread(threading.Thread):

	def __init__(self, app, template_directory, file_upload_directory, port, callback):
		threading.Thread.__init__(self)
		app.config['fileuploaddir'] = file_upload_directory
		app.template_folder = template_directory
		self.srv = make_server('', port, app)
		self.ctx = app.app_context()
		self.ctx.push()

	def run(self):
		self.srv.serve_forever()
		
	def shutdown(self):
		self.srv.shutdown()

class Transfer (object):
	def __init__(self):
		self.__name = ''
		self.__status = ''
		self.__path = None
		self.__zipPath = None
		self.__stats = ''
		self.__id = ''
		self.__image = None
		
	@property
	def name(self):
		return self.__name
	
	@name.setter
	def name(self, data):
		self.__name = data
		
	@property
	def status(self):
		return self.__status
	
	@status.setter
	def status(self, data):
		self.__status = data	
	
	@property
	def path(self):
		return self.__path
	
	@path.setter
	def path(self, data):
		self.__path = data
	
	@property
	def zipPath(self):
		return self.__zipPath
	
	@zipPath.setter
	def zipPath(self, data):
		self.__zipPath = data

	@property
	def stats(self):
		return self.__stats
	
	@stats.setter
	def stats(self, data):
		self.__stats = data
	
	@property
	def id(self):
		return self.__id
	
	@id.setter
	def id(self, id):
		self.__id = id
	
	@property
	def image(self):
		return self.__image
	
	@image.setter
	def image(self, data):
		self.__image = data
	
		
class TransferManager (object):
	def __init__(self, iconPath, typeIconPath):
		self.server = None
		self.running = False
		self.typeManager = TypeManager.TypeManager(typeIconPath)
		self.iconPath = iconPath
		self.docsetFolder = 'Docsets/Transfer'
		self.plistPath = 'Contents/Info.plist'
		self.indexPath = 'Contents/Resources/docSet.dsidx'
		self.installThreads = []
		self.uiUpdateThreads = []
		self.__installingDocsets = []
		
		self.__createDocsetFolder()
	def __createDocsetFolder(self):
		if not os.path.exists(self.docsetFolder):
			os.mkdir(self.docsetFolder)
	
	def startTransferService(self, template_directory, file_upload_directory, port, callback):
		self.server = ServerThread(app, template_directory, file_upload_directory, port, callback)
		self.server.start()
		self.running = True
		return {'hostname':socket.gethostbyname(socket.gethostname()), 'port':port}

	def stopTransferService(self, action):
		self.server.shutdown()
		self.server = None
		self.running = False
		action()

	def __installDocset(self, docset, refresh):
		extract_location = self.docsetFolder
		docset.stats = 'Preparing to install: This might take a while.'
		refresh()
		zip = ZipFile(docset.zipPath, mode='r')
		ll = [name for name in zip.namelist() if '.docset' in name]
		if len(ll) > 0:
			n = ll[0]
			m = os.path.join(self.docsetFolder, n)
			docset.stats = 'Preparing to extract'
			refresh()
			l = zip.infolist()
			zip.extractall(path=extract_location, members = self.track_progress(l, docset, len(l), refresh))
			zip.close()
			os.remove(docset.zipPath)
			plistpath = os.path.join(m, self.plistPath)
			name = docset.name
			image = ''
			with open(plistpath, 'rb') as f:
				pp = plistlib.load(f)
				if 'CFBundleName' in pp.keys():
					name = pp['CFBundleName']
				if 'CFBundleIdentifier' in pp.keys():
					image = pp['CFBundleIdentifier']
			dbManager = DBManager.DBManager()
			dbManager.DocsetInstalled(name, m, 'transfer', image, 0.0)
			if docset in self.__installingDocsets:
				self.__installingDocsets.remove(docset)
			docset.status = 'Cleaning up...'
			refresh() 
			cleanup_path = os.path.join(self.docsetFolder,'__MACOSX') 
			if os.path.exists(cleanup_path):
				shutil.rmtree(cleanup_path)
			docset.status = 'Installed'
			refresh()
		else:
			raise Exception('Unknown docset structure')
	
	def track_progress(self, members, docset, totalFiles, refresh):
		i = 0
		for member in members:
			i = i + 1
			done = 100 * i / totalFiles
			docset.stats = 'installing: ' + str(round(done,2)) + '% ' + str(i) + ' / '+ str(totalFiles) 
			if i % 100 == 0:
				refresh()
			yield member
		refresh()
	
	def installDocset(self, docset, action, refresh_main_view):
		self.__installingDocsets.append(docset)
		docset.status = 'Installing'
		action()
		installThread = LogThread.LogThread(target=self.__installDocset, args=(docset,refresh_main_view,))
		self.installThreads.append(installThread)
		installThread.start()
		# updateThread = LogThread.LogThread(target=self.updateUi, args=(action,installThread,))
		# self.uiUpdateThreads.append(updateThread)
		# updateThread.start()
	
	def deleteDocset(self, docset, post_action, confirm = True):
		but = 1
		if confirm:
			but = console.alert('Are you sure?', 'Would you like to delete the docset, ' +  docset.name, 'Ok')
		if but == 1:
			dbmanager = DBManager.DBManager()
			dbmanager.DocsetRemoved(docset.id)
			shutil.rmtree(docset.path)
			docset.status = 'Not Installed'
			if not post_action == None:
				post_action()
			docset.path = None
	
	def __getIconWithName(self, name):
		imgPath = os.path.join(os.path.abspath('.'), self.iconPath, name+'.png')
		if not os.path.exists(imgPath):
			imgPath = os.path.join(os.path.abspath('.'), self.iconPath, 'Other.png')
		return ui.Image.named(imgPath)
	
	def __getAvailableDocsets(self):
		d = []
		for file in os.listdir(self.docsetFolder):
			if file.endswith('.zip') or file.endswith('.ZIP'):
				doc = Transfer()
				doc.name = file
				doc.status = 'Not Installed'
				doc.zipPath = os.path.join(os.path.abspath('.'), self.docsetFolder, file)
				d.append(doc)
		return d
	
	def __getInstallingDocsets(self):
		return self.__installingDocsets
		
	def __getInstalledDocsets(self):
		ds = []
		dbManager = DBManager.DBManager()
		t = dbManager.InstalledDocsetsByType('transfer')
		ds = []
		for d in t:
			aa = Transfer()
			aa.name = d[1]
			aa.id = d[0]
			aa.path = os.path.join(os.path.abspath('.'),d[2])
			aa.image = self.__getIconWithName(d[4])
			aa.status = 'Installed'
			# aa.version = d[5]
			ds.append(aa)
		return ds
		
	def getInstalledDocsets(self):
		return self.__getInstalledDocsets()
	
	def getAvailableDocsets(self):
		dic = {}
		ava = self.__getAvailableDocsets()
		ins = self.__getInstallingDocsets()
		inst = self.getInstalledDocsets()
		if len(ins) > 0:
			for i in ins:
				for a in ava:
					if i.name == a.name:
						a.status = 'Installing'
						a.stats = i.stats
		if len(ava) > 0:
			dic['Available'] = ava
		if len(inst) > 0:
			dic['Installed'] = inst
		return dic
	
	def getIndexesbyTypeForDocset(self, docset, type):
		indexes = []
		path = docset.path
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type, name, path FROM searchIndex WHERE type = (?) ORDER BY name COLLATE NOCASE'
		c = conn.execute(sql, (type.name,))
		data = c.fetchall()
		conn.close()
		dTypes ={}
		type = None		
		for t in data:
			if t[0] in dTypes.keys():
				type= dTypes[t[0]]
			else:
				type = self.typeManager.getTypeForName(t[0])
				dTypes[t[0]] = type
			indexes.append({'type':type, 'name':t[1],'path':t[2]})
		return indexes
	
	def getTypesForDocset(self, docset):
		types = []
		path = docset.path
		indexPath = os.path.join(path, self.indexPath)
		conn = sqlite3.connect(indexPath)
		sql = 'SELECT type FROM searchIndex GROUP BY type ORDER BY type COLLATE NOCASE'
		c = conn.execute(sql)
		data = c.fetchall()
		conn.close()
		for t in data:
			types.append(self.typeManager.getTypeForName(t[0]))
		return types
	
	def updateUi(self, action, t):
		while t.is_alive():
			action()
			time.sleep(0.5)
		action()
	
	def getIndexesbyNameForAllDocsets(self, name):
		if name == None or name == '':
			return {}
		else:
			docsets = self.getInstalledDocsets()
			indexes = {}
			for d in docsets:
				ind = self.getIndexesbyNameForDocsetSearch(d, name)
				for k in ind:
					if not k in indexes.keys():
						indexes[k] = []
					indexes[k].extend(ind[k])
			return indexes
			
	def getIndexesbyNameForDocsetSearch(self, docset, name):
		if name == None or name == '':
			return []
		else:
			ind = {}
			path = docset.path
			indexPath = os.path.join(path, self.indexPath)
			conn = sqlite3.connect(indexPath)
			sql = 'SELECT type, name, path FROM searchIndex WHERE name LIKE (?) ORDER BY name COLLATE NOCASE'
			c = conn.execute(sql, (name, ))
			data = {'first' : c.fetchall()}

			sql = 'SELECT type, name, path FROM searchIndex WHERE name LIKE (?) AND name NOT LIKE (?) ORDER BY name COLLATE NOCASE'
			c = conn.execute(sql, (name.replace(' ','%'), name, ))
			data['second'] = c.fetchall()
						
			sql = 'SELECT type, name, path FROM searchIndex WHERE name LIKE (?) AND name NOT LIKE (?) AND name NOT LIKE (?) ORDER BY name COLLATE NOCASE'
			c = conn.execute(sql, (name.replace(' ','%')+'%', name.replace(' ','%'), name, ))
			data['third'] = c.fetchall()
			
			sql = 'SELECT type, name, path FROM searchIndex WHERE name LIKE (?) AND name NOT LIKE (?) AND name NOT LIKE (?) AND name NOT LIKE (?) ORDER BY name COLLATE NOCASE'
			c = conn.execute(sql, ('%'+name.replace(' ','%')+'%',name.replace(' ','%')+'%',name.replace(' ','%'), name, ))
			data['fourth'] = c.fetchall()
						
									
			conn.close()
			dTypes = {}
			for k in data:
				ind[k] = []
				for t in data[k]:
					url = 'file://' + os.path.join(path, 'Contents/Resources/Documents', t[2])
					
					url = url.replace(' ', '%20').replace('<', '%3E').replace('>', '%3C')
					type = None
					if t[0] in dTypes.keys():
						type= dTypes[t[0]]
					else:
						type = self.typeManager.getTypeForName(t[0])
						dTypes[t[0]] = type
					ind[k].append({'name':t[1], 'path':url, 'icon':None,'docsetname':docset.name,'type':type, 'callbackOverride':'', 'docset': docset})
			return ind
	
		
if __name__ == '__main__':
	tm = TransferManager()
	print(tm.startTransferService('../Resources', '.', 8080))
	time.sleep(15)
	tm.stopTransferService()
	print('stopped')
