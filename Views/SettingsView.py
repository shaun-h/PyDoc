import ui
import dialogs
import console
import threading
import time
from objc_util import ObjCClass, NSURL, ns
from Utilities import Updater
	
class SettingsView (object):
	def __init__(self, show_docset_management_view, show_cheatsheet_management_view, show_usercontributed_management_view, theme_manager, show_stackoverflow_management_view, websearch_manager, show_transfer_management_view):
		self.data = ['Standard Docsets', 'Cheat Sheets', 'User Contributed Docsets', 'Stack Overflow Docsets', 'Transfer Docsets']
		self.webSearch_data = ['Add Web Search', 'Enable/Disable Web Searches', 'Remove Web Search', 'Refresh Web Search Icons']
		self.ack_data = [{'text':'Dash','url':'https://kapeli.com/dash'}]
		self.updates_data = ['Check for Update', 'Reinstall Current Version', 'Install Version', 'Install Pre-release Version']
		self.theme_data = ['Change theme']
		self.manage_docset_row = 0
		self.manage_cheatsheet_row = 1
		self.manage_usercontributed_row = 2
		self.manage_stackoverflow_row = 3
		self.manage_transfer_row = 4
		self.add_websearches_row = 0
		self.en_di_websearches_row = 1
		self.del_websearches_row = 2
		self.refresh_websearch_icons = 3
		self.show_docset_management_view = show_docset_management_view
		self.show_cheatsheet_management_view = show_cheatsheet_management_view
		self.show_usercontributed_management_view = show_usercontributed_management_view
		self.show_stackoverflow_management_view = show_stackoverflow_management_view
		self.show_transfer_management_view = show_transfer_management_view
		self.docset_section_number = 0
		self.ack_section_number = 1
		self.websearch_section_number = 2
		self.pydoc_updates_section_number = 3
		self.theme_section_number = 4
		self.updater = Updater.Updater()
		self.theme_manager = theme_manager
		self.websearch_manager = websearch_manager
	
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
			elif self.manage_stackoverflow_row == row:
				console.show_activity('Loading Stack Overflow Docsets...')
				uiThread = threading.Thread(target=self.show_stackoverflow_management_view)
				uiThread.start()
			elif self.manage_transfer_row == row:
				uiThread = threading.Thread(target=self.show_transfer_management_view)
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
			elif row == 3:
				ret = console.alert('Warning','Pre-release versions can have bugs and be unstable, including corrupting your installation. Only install a pre-release version if you are sure. Would you like to install a pre-release version?', hide_cancel_button=True, button1='No', button2 = 'Yes')
				if ret == 2:
					self.updater.showAvailableVersions(True)
		if self.theme_section_number == section:
			if row == 0:
				themes = self.theme_manager.themes
				data = [x for x in themes.keys()]
				t = dialogs.list_dialog('Please choose your theme', data)
				if not t == None:
					if not t == self.theme_manager.themeFileName:
						self.theme_manager.saveThemeToUse(t)
						ret = console.alert('Saved', 'Please restart PyDoc for your theme change to take affect.', button1 = 'Ok', hide_cancel_button=True)
		if section == self.websearch_section_number:
			if row == self.add_websearches_row:
				dialogs.alert('Info','Please include {query} in your url this will be replaced with your search query.',hide_cancel_button=True,button1='Ok')
				ok = True
				name = ''
				url = ''
				while ok:
					s = [{'title':'Name','type':'text', 'value':name},{'title':'URL','type':'text', 'autocorrection':False, 'autocapitalization':False,'value':url}]
					data = dialogs.form_dialog(title='Add Web Search',fields=s)
					if not data == None:
						ret, error = self.websearch_manager.AddWebSearch(data['Name'],data['URL'])
						if not ret:
							name = data['Name']
							url = data['URL']
							dialogs.alert('Error',error, hide_cancel_button=True, button1='Ok')
						else:
							ok = False
							dialogs.alert('Save','Web Search ' +data['Name']+' has been saved.', hide_cancel_button=True, button1='Ok')
					else:
						ok = False
					
			if row == self.en_di_websearches_row:
				searches = self.websearch_manager.GetWebSearches()
				list = []
				for search in searches:
					v = False
					if search[3] == 1:
						v = True
					s = {'key': str(search[0]),'type':'switch','value':v,'title':str(search[1])}
					list.append(s)
				data = dialogs.form_dialog(title='Enable/Disable Web Searches',fields=list)
				if not data == None:
					for v in data:
						if data[v]:
							self.websearch_manager.EnableWebSearch(v)
						else:
							self.websearch_manager.DisableWebSearch(v)
					
			if row == self.del_websearches_row:
				searches = self.websearch_manager.GetWebSearches()
				d = []
				for search in searches:
					d.append(search[1])
				data = dialogs.edit_list_dialog(title='Please swipe to delete', items=d,move=False,delete=True)
				if not data == None:
					for search in searches:
						if not search[1] in data:
							self.websearch_manager.RemoveWebSearch(search[0])
			if row == self.refresh_websearch_icons:
				console.show_activity('Saving icons...')
				searches = self.websearch_manager.GetWebSearches()
				for search in searches:
					self.websearch_manager.SaveIconForWebSearch(search[0], search[2])
				console.hide_activity()
		
	def tableview_number_of_sections(self, tableview):
		return 5
		
	def tableview_number_of_rows(self, tableview, section):
		if section == self.docset_section_number:
			return len(self.data)
		if section == self.ack_section_number:
			return len(self.ack_data)
		if section == self.pydoc_updates_section_number:
			return len(self.updates_data)
		if section == self.theme_section_number:
			return len(self.theme_data)
		if section == self.websearch_section_number:
			return len(self.webSearch_data)
		
		
	def tableview_cell_for_row(self, tableview, section, row):
		cell = ui.TableViewCell()		
		cell.border_color = self.theme_manager.currentTheme.borderColour
		cell.background_color = self.theme_manager.currentTheme.backgroundColour
		cell.bg_color = self.theme_manager.currentTheme.backgroundColour
		cell.tint_color = self.theme_manager.currentTheme.tintColour
		cell.text_label.text_color = self.theme_manager.currentTheme.textColour
		selectedBackgroundView = ui.View()
		selectedBackgroundView.background_color = self.theme_manager.currentTheme.settingsCellSelectionColour
		if not self.theme_manager.currentTheme.showSettingsCellSelection:
			selectedBackgroundView.alpha = 0
		cell.selected_background_view = selectedBackgroundView
		if section == self.docset_section_number:
			cell.text_label.text = self.data[row]
			cell.accessory_type = 'disclosure_indicator'
		elif section == self.ack_section_number:
			cell.text_label.text = self.ack_data[row]['text']
		elif section == self.pydoc_updates_section_number:
			cell.text_label.text = self.updates_data[row]
		elif section == self.theme_section_number:
			cell.text_label.text = self.theme_data[row]
		elif section == self.websearch_section_number:
			cell.text_label.text = self.webSearch_data[row]
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
		if section == self.websearch_section_number:
			return 'Manage Web Search'
		
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
def get_view(show_docset_management_view, show_cheatsheet_management_view, show_usercontributed_management_view, theme_manager, show_stackoverflow_management_view,websearch_manager, show_transfer_management_view):
	w,h = ui.get_screen_size()
	tv.width = w
	tv.height = h
	tv.flex = 'WH'
	tv.name = 'Settings' 
	data = SettingsView(show_docset_management_view, show_cheatsheet_management_view, show_usercontributed_management_view, theme_manager, show_stackoverflow_management_view,websearch_manager, show_transfer_management_view)
	tv.delegate = data
	tv.data_source = data
	return tv
