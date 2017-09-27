import ui
import dialogs
import console
import threading
import time
from objc_util import ObjCClass, NSURL, ns
from Utilities import Updater
	
class SettingsView (object):
	def __init__(self, show_docset_management_view, show_cheatsheet_management_view, show_usercontributed_management_view, theme_manager):
		self.data = ['Standard Docsets', 'Cheat Sheets', 'User Contributed Docsets']
		self.ack_data = [{'text':'Dash','url':'https://kapeli.com/dash'}]
		self.updates_data = ['Check for Update']#, 'Reinstall Current Version', 'Install Version']
		self.theme_data = ['Change theme']
		self.manage_docset_row = 0
		self.manage_cheatsheet_row = 1
		self.manage_usercontributed_row = 2
		self.show_docset_management_view = show_docset_management_view
		self.show_cheatsheet_management_view = show_cheatsheet_management_view
		self.show_usercontributed_management_view = show_usercontributed_management_view
		self.docset_section_number = 0
		self.ack_section_number = 1
		self.pydoc_updates_section_number = 2
		self.theme_section_number = 3
		self.updater = Updater.Updater()
		self.theme_manager = theme_manager
	
	@ui.in_background
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
			self.open_url(self.ack_data[row]['url'])
		if self.pydoc_updates_section_number == section:
			if row == 0:
				self.updater.checkForUpdate()
			elif row == 1:
				self.updater.reinstallCurrentVersion()
			elif row == 2:
				self.updater.showAvailableVersions()
		if self.theme_section_number == section:
			if row == 0:
				themes = self.theme_manager.themes
				data = [x for x in themes.keys()]
				t = dialogs.list_dialog('Please choose your theme', data)
				if not t == None:
					if not t == self.theme_manager.themeFileName:
						self.theme_manager.saveThemeToUse(t)
						ret = console.alert('Saved', 'Please restart Pythonista for your theme change to take affect.', button1 = 'Ok', hide_cancel_button=True)
					
		
	def tableview_number_of_sections(self, tableview):
		return 4
		
	def tableview_number_of_rows(self, tableview, section):
		if section == self.docset_section_number:
			return len(self.data)
		if section == self.ack_section_number:
			return len(self.ack_data)
		if section == self.pydoc_updates_section_number:
			return len(self.updates_data)
		if section == self.theme_section_number:
			return len(self.theme_data)
		
		
	def tableview_cell_for_row(self, tableview, section, row):
		cell = ui.TableViewCell()		
		cell.border_color = self.theme_manager.currentTheme.borderColour
		cell.background_color = self.theme_manager.currentTheme.backgroundColour
		cell.bg_color = self.theme_manager.currentTheme.backgroundColour
		cell.tint_color = self.theme_manager.currentTheme.tintColour
		cell.text_label.text_color = self.theme_manager.currentTheme.textColour
		if section == self.docset_section_number:
			cell.text_label.text = self.data[row]
			cell.accessory_type = 'disclosure_indicator'
		elif section == self.ack_section_number:
			cell.text_label.text = self.ack_data[row]['text']
		elif section == self.pydoc_updates_section_number:
			cell.text_label.text = self.updates_data[row]
		elif section == self.theme_section_number:
			cell.text_label.text = self.theme_data[row]	
		return cell
	
	def tableview_title_for_header(self, tableview, section):
		if section == self.docset_section_number:
			return 'Manage'
		if section == self.ack_section_number:
			return 'Docsets are provided by Dash the MacOS docset browser. Please checkout Dash please by clicking the link below.'
		if section == self.pydoc_updates_section_number:
			return 'Update PyDoc'
		if section == self.theme_section_number:
			return 'Themes'
		
	def tableview_title_for_footer(self, tableview, section):
		if section == self.pydoc_updates_section_number:
			return 'Current Version - v' + self.updater.currentVersion
		elif section == self.theme_section_number:
			return 'Current Theme - ' + self.theme_manager.currentTheme.themeName
			
	def open_url(self, url):
		UIApplication = ObjCClass('UIApplication')
		sharedApplication = UIApplication.sharedApplication()
		internalurl = NSURL.URLWithString_(ns(url))
		sharedApplication.openURL_(internalurl)

tv = ui.TableView('grouped')
def get_view(show_docset_management_view, show_cheatsheet_management_view, show_usercontributed_management_view, theme_manager):
	w,h = ui.get_screen_size()
	tv.width = w
	tv.height = h
	tv.flex = 'WH'
	tv.name = 'Settings'
	data = SettingsView(show_docset_management_view, show_cheatsheet_management_view, show_usercontributed_management_view, theme_manager)
	tv.delegate = data
	tv.data_source = data
	return tv

