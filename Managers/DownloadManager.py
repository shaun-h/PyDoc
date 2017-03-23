#!/usr/bin/env python3
from objc_util import *
import os

NSFileHandle = ObjCClass('NSFileHandle')
NSFileManager = ObjCClass('NSFileManager')
NSURLRequest = ObjCClass('NSURLRequest')
NSURLConnection = ObjCClass('NSURLConnection')

def connection_didReceiveResponse_(_self, _cmd, connection, response):
	sel = ObjCInstance(_self)
	sel.total_to_download = ObjCInstance(response).expectedContentLength()
	sel.total_downloaded = 0
	sel.update = 0

def connection_didReceiveData_(_self, _cmd, connection, data):
	sel = ObjCInstance(_self)
	sel.total_downloaded += ObjCInstance(data).length()
	sel.filehandle.writeData_(ObjCInstance(data))
	sel.update += 1
	if sel.update % 100 == 0 and not sel.updateCallback == None:
		print(sel.update)
		done = 100 * sel.total_downloaded / int(sel.total_to_download)
		sel.updateCallback(str(round(done,2)) + '% ' + str(self.convertSize(sel.total_downloaded)) + ' / '+ str(self.convertSize(float(sel.total_to_download))))
	
def connection_willCacheResponse_(_self, _cmd, connection, cachedResponse):
	return None

def connectionDidFinishLoading_(_self, _cmd, connection):
	sel = ObjCInstance(_self)
	sel.filehandle = None
	sel.finishedCallback()
	print('finished')
	
def connection_didFailWithError_(_self, _cmd, connection, error):
	pass


methods = [connection_didReceiveResponse_, connection_didReceiveData_, connection_willCacheResponse_, connectionDidFinishLoading_, connection_didFailWithError_]
protocols = ['NSURLConnectionDelegate']
try:
	MyNSUrlDelegate = ObjCClass('MyNSUrlDelegate')
except:
	MyNSUrlDelegate = create_objc_class('MyNSUrlDelegate', NSObject, methods=methods, protocols=protocols)

def downloadFileToPath(url, path, received_response_callback = None, update_callback = None, finished_callback = None, error_callback= None):
	local_filename = path
	fileMan = NSFileManager.defaultManager()
	if os.path.exists(local_filename):
		os.remove(local_filename)
	fileMan.createFileAtPath_contents_attributes_(local_filename,None,None)
	delegate = MyNSUrlDelegate.alloc().init().autorelease()
	delegate.filehandle = NSFileHandle.fileHandleForUpdatingAtPath_(local_filename).autorelease()
	delegate.updateCallback = update_callback
	delegate.finishedCallback = finished_callback
	request = NSURLRequest.requestWithURL_(NSURL.URLWithString(ns(url))).autorelease()
	conn = NSURLConnection.alloc().initWithRequest_delegate_(request,delegate).autorelease()
	print('yuiop')
	print(conn)
	return local_filename
	
if '__main__' == __name__:
	downloadFileToPath('http://sydney.kapeli.com/feeds/NET_Framework.tgz', os.path.join(os.path.curdir, 'NET_Framework.tgz'))
