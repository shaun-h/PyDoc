from werkzeug.serving import make_server 
from flask import Flask, render_template, request, current_app
import threading
import time
import socket
import os

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

	def __init__(self, app, template_directory, file_upload_directory, port):
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

class TransferManager (object):
	def __init__(self):
		self.server = None
		self.running = False
		self.docsetFolder = 'Docsets/Transfer'
		
		self.__createDocsetFolder()
	def __createDocsetFolder(self):
		if not os.path.exists(self.docsetFolder):
			os.mkdir(self.docsetFolder)
	
	def startTransferService(self, template_directory, file_upload_directory, port):
		self.server = ServerThread(app, template_directory, file_upload_directory, port)
		self.server.start()
		self.running = True
		return {'hostname':socket.gethostbyname(socket.gethostname()), 'port':port}

	def stopTransferService(self):
		self.server.shutdown()
		self.server = None
		self.running = False

	
	def installDocset(self):
		pass
	
	def deleteDocset(self):
		pass
		
	def getAvailableDocsets(self):
		pass
		
if __name__ == '__main__':
	tm = TransferManager()
	print(tm.startTransferService('../Resources', '.', 8080))
	time.sleep(15)
	tm.stopTransferService()
	print('stopped')
