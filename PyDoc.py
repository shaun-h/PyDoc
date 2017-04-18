from Managers import DocsetManager, ServerManager, CheatsheetManager
from Views import DocsetManagementView, SettingsView, DocsetListView, DocsetView, DocsetIndexView, DocsetWebView, CheatsheetManagementView
import ui
import threading

class PyDoc(object):
	def __init__(self):
		self.docset_manager = DocsetManager.DocsetManager('Images/icons', 'Images/types', ServerManager.ServerManager())
		self.cheatsheet_manager = CheatsheetManager.CheatsheetManager(ServerManager.ServerManager(), 'Images/icons', 'Images/types')
		self.main_view = self.setup_main_view()
		self.navigation_view = self.setup_navigation_view()
		self.docset_management_view = self.setup_docset_management_view()
		self.cheatsheet_management_view = self.setup_cheatsheetmanagement_view()
		self.settings_view = self.setup_settings_view()
		
	def setup_navigation_view(self):
		nav_view = ui.NavigationView(self.main_view)
		return nav_view

	def setup_main_view(self):
		docsets = self.docset_manager.getDownloadedDocsets()
		cheatsheets = self.cheatsheet_manager.getDownloadedCheatsheets()
		main_view = DocsetListView.get_view(docsets, cheatsheets, self.docset_selected_for_viewing, self.cheatsheet_selected_for_viewing)
		settings_button = ui.ButtonItem(title='Settings')
		settings_button.action = self.show_settings_view
		main_view.left_button_items = [settings_button]
		return main_view

	def setup_docset_management_view(self):
		docsets = self.docset_manager.getAvailableDocsets()
		return DocsetManagementView.get_view(docsets, self.docset_manager.downloadDocset, self.docset_manager.getAvailableDocsets, self.docset_manager.deleteDocset, self.refresh_main_view_data)
	
	def refresh_main_view_data(self):
		docsets = self.docset_manager.getDownloadedDocsets() 
		cheatsheets = self.cheatsheet_manager.getDownloadedCheatsheets()
		DocsetListView.refresh_view(docsets, cheatsheets)
	
	def setup_cheatsheetmanagement_view(self):
		cheatsheets = self.cheatsheet_manager.getAvailableCheatsheets()
		return CheatsheetManagementView.get_view(cheatsheets, self.cheatsheet_manager.downloadCheatsheet, self.refresh_main_view_data, self.cheatsheet_manager.deleteCheatsheet, self.cheatsheet_manager.getAvailableCheatsheets)
		
	def show_cheatsheetmanagement_view(self):
		self.navigation_view.push_view(self.cheatsheet_management_view)
		
	def setup_settings_view(self):
		return SettingsView.get_view(self.docset_management_view, self.cheatsheet_management_view)
		
	def show_settings_view(self, sender):
		self.navigation_view.push_view(self.settings_view)
	
	def docset_selected_for_viewing(self, docset):
		types = self.docset_manager.getTypesForDocset(docset)
		view = DocsetView.get_view(docset, types, self.docset_type_selected_for_viewing, 'docset')
		self.navigation_view.push_view(view)
	
	def docset_type_selected_for_viewing(self, docset, type):
		indexes = self.docset_manager.getIndexesbyTypeForDocset(docset, type)
		view = DocsetIndexView.get_view(docset, indexes, self.docset_index_selected_for_viewing, 'docset')
		self.navigation_view.push_view(view)
	
	def cheatsheet_selected_for_viewing(self, cheatsheet):
		types = self.cheatsheet_manager.getTypesForCheatsheet(cheatsheet)
		view = DocsetView.get_view(cheatsheet, types, self.cheatsheet_type_selected_for_viewing, 'cheatsheet')
		self.navigation_view.push_view(view)
	
	def cheatsheet_type_selected_for_viewing(self, cheatsheet, type):
		indexes = self.cheatsheet_manager.getIndexesbyTypeForCheatsheet(cheatsheet, type)
		view = DocsetIndexView.get_view(cheatsheet, indexes, self.docset_index_selected_for_viewing, 'cheatsheet')
		self.navigation_view.push_view(view)
		
	def docset_index_selected_for_viewing(self, url):
		view = DocsetWebView.get_view(url)
		self.navigation_view.push_view(view)
				
if __name__ == '__main__':
	py = PyDoc()
	py.navigation_view.present(hide_title_bar=True)
	
