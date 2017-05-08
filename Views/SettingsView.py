import ui
import console
import threading
import time
from objc_util import ObjCClass, NSURL, ns
	
class SettingsView (object):
	def __init__(self, show_docset_management_view, show_cheatsheet_management_view, show_usercontributed_management_view):
		self.data = ['Standard Docsets', 'Cheat Sheets', 'User Contributed Docsets']
		self.ack_data = [{'text':'Dash','url':'https://kapeli.com/dash'}]
		self.manage_docset_row = 0
		self.manage_cheatsheet_row = 1
		self.manage_usercontributed_row = 2
		self.show_docset_management_view = show_docset_management_view
		self.show_cheatsheet_management_view = show_cheatsheet_management_view
		self.show_usercontributed_management_view = show_usercontributed_management_view
		self.docset_section_number = 0
		self.ack_section_number = 1
		
	def tableview_did_select(self, tableview, section, row):
		if self.docset_section_number == section:
			if self.manage_docset_row == row:
				self.show_docset_management_view()
			elif self.manage_cheatsheet_row == row:
				console.show_activity('Loading Cheat Sheets...')
				uiThread = threading.Thread(target=self.show_cheatsheet_management_view)
				uiThread.start()
			elif self.manage_usercontributed_row == row:
				console.show_activity('Loading User Contributed Docsets...')
				uiThread = threading.Thread(target=self.show_usercontributed_management_view)
				uiThread.start()
		if self.ack_section_number == section:
			if row == 0:
				self.open_url(self.ack_data[row]['url'])			
		
	def tableview_number_of_sections(self, tableview):
		return 2
		
	def tableview_number_of_rows(self, tableview, section):
		if section == self.docset_section_number:
			return len(self.data)
		if section == self.ack_section_number:
			return len(self.ack_data)
		
	def tableview_cell_for_row(self, tableview, section, row):
		cell = ui.TableViewCell()
		if section == self.docset_section_number:
			cell.text_label.text = self.data[row]
			cell.accessory_type = 'disclosure_indicator'
		elif section == self.ack_section_number:
			cell.text_label.text = self.ack_data[row]['text']
		return cell
	
	def tableview_title_for_header(self, tableview, section):
		if section == self.docset_section_number:
			return 'Manage'
		if section == self.ack_section_number:
			return 'Docsets are provided by Dash the MacOS docset browser. Please checkout Dash please by clicking the link below.'
	
	def open_url(self, url):
		UIApplication = ObjCClass('UIApplication')
		sharedApplication = UIApplication.sharedApplication()
		internalurl = NSURL.URLWithString_(ns(url))
		sharedApplication.openURL_(internalurl)

tv = ui.TableView('grouped')
def get_view(show_docset_management_view, show_cheatsheet_management_view, show_usercontributed_management_view):
	w,h = ui.get_screen_size()
	tv.width = w
	tv.height = h
	tv.flex = 'WH'
	tv.name = 'Settings'
	data = SettingsView(show_docset_management_view, show_cheatsheet_management_view, show_usercontributed_management_view)
	tv.delegate = data
	tv.data_source = data
	return tv

