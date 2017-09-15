from Managers import DocsetManager, ServerManager, CheatsheetManager, UserContributedManager, DBManager
from Views import DocsetManagementView, SettingsView, DocsetListView, DocsetView, DocsetIndexView, DocsetWebView, CheatsheetManagementView, UserContributedManagementView
import ui
import console
import os


class PyDoc(object):
	def __init__(self):
		console.show_activity('Loading...')
		self.docsetFolder = 'Docsets'
		self.setup()
		self.dbmanager = DBManager.DBManager()
		self.docset_manager = DocsetManager.DocsetManager('Images/icons', 'Images/types', ServerManager.ServerManager())
		self.cheatsheet_manager = CheatsheetManager.CheatsheetManager(ServerManager.ServerManager(), 'Images/icons', 'Images/types')
		self.usercontributed_manager = UserContributedManager.UserContributedManager(ServerManager.ServerManager(), 'Images/icons','Images/types')
		self.main_view = self.setup_main_view()
		self.navigation_view = self.setup_navigation_view()
		self.docset_management_view = self.setup_docset_management_view()
		self.cheatsheet_management_view = self.setup_cheatsheetmanagement_view()
		self.usercontributed_management_view = self.setup_usercontributedmanagement_view()
		self.settings_view = self.setup_settings_view()
		self.docsetView = self.setup_docset_view()
		self.docsetIndexView = self.setup_docsetindex_view()
		self.docsetWebView = self.setup_docsetweb_view()
		console.hide_activity()
		
	def setup(self):
		if not os.path.exists(self.docsetFolder):
			os.mkdir(self.docsetFolder)
		
	def setup_navigation_view(self):
		nav_view = ui.NavigationView(self.main_view)
		return nav_view

	def setup_main_view(self):
		docsets = self.docset_manager.getDownloadedDocsets()
		cheatsheets = self.cheatsheet_manager.getDownloadedCheatsheets()
		usercontributed = self.usercontributed_manager.getDownloadedUserContributed()
		main_view = DocsetListView.get_view(docsets, cheatsheets, usercontributed, self.docset_selected_for_viewing, self.cheatsheet_selected_for_viewing, self.usercontributed_selected_for_viewing)
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
		usercontributed = self.usercontributed_manager.getDownloadedUserContributed()
		DocsetListView.refresh_view(docsets, cheatsheets, usercontributed)
	
	def setup_cheatsheetmanagement_view(self):
		return CheatsheetManagementView.get_view(self.cheatsheet_manager.downloadCheatsheet, self.refresh_main_view_data, self.cheatsheet_manager.deleteCheatsheet, self.cheatsheet_manager.getAvailableCheatsheets)
		
	def show_docset_management_view(self):
		self.navigation_view.push_view(self.docset_management_view)
		
	def show_cheatsheetmanagement_view(self):
		self.cheatsheet_management_view.data_source.data = self.cheatsheet_manager.getAvailableCheatsheets()
		self.cheatsheet_management_view.reload()
		self.navigation_view.push_view(self.cheatsheet_management_view)
		console.hide_activity()
		
	def setup_usercontributedmanagement_view(self):
		return UserContributedManagementView.get_view(self.usercontributed_manager.downloadUserContributed, self.refresh_main_view_data, self.usercontributed_manager.deleteUserContributed, self.usercontributed_manager.getAvailableUserContributed)
		
	def show_usercontributedmanagement_view(self):
		self.usercontributed_management_view.data_source.data = self.usercontributed_manager.getAvailableUserContributed()
		self.usercontributed_management_view.reload()
		self.navigation_view.push_view(self.usercontributed_management_view)
		console.hide_activity()
		
	def setup_settings_view(self):
		return SettingsView.get_view(self.show_docset_management_view, self.show_cheatsheetmanagement_view, self.show_usercontributedmanagement_view)
		
	def setup_docset_view(self):
		 return DocsetView.get_view()
		
	def setup_docsetindex_view(self):
		return DocsetIndexView.get_view()
		
	def setup_docsetweb_view(self):
		return DocsetWebView.get_view()
		
	def show_settings_view(self, sender):
		self.navigation_view.push_view(self.settings_view)
	
	def docset_selected_for_viewing(self, docset):
		types = self.docset_manager.getTypesForDocset(docset)
		self.docsetView.data_source.update_with_docset(docset, types, self.docset_type_selected_for_viewing)
		self.docsetView.name = docset['name']
		self.docsetView.reload()
		self.navigation_view.push_view(self.docsetView)
	
	def docset_type_selected_for_viewing(self, docset, type):
		indexes = self.docset_manager.getIndexesbyTypeForDocset(docset, type)
		self.docsetIndexView.data_source.update_with_docset(docset, indexes, self.docset_index_selected_for_viewing, 'docset')
		self.docsetView.name = docset['name']
		self.docsetIndexView.reload()
		self.navigation_view.push_view(self.docsetIndexView)
	
	def cheatsheet_selected_for_viewing(self, cheatsheet):
		types = self.cheatsheet_manager.getTypesForCheatsheet(cheatsheet)
		self.docsetView.data_source.update_with_docset(cheatsheet, types, self.cheatsheet_type_selected_for_viewing)
		self.docsetView.name = cheatsheet.name
		self.docsetView.reload()
		self.navigation_view.push_view(self.docsetView)
	
	def cheatsheet_type_selected_for_viewing(self, cheatsheet, type):
		indexes = self.cheatsheet_manager.getIndexesbyTypeForCheatsheet(cheatsheet, type)
		self.docsetIndexView.data_source.update_with_docset(cheatsheet, indexes, self.docset_index_selected_for_viewing, 'cheatsheet')
		self.docsetView.name = cheatsheet.name
		self.docsetIndexView.reload()
		self.navigation_view.push_view(self.docsetIndexView)
		
	def usercontributed_selected_for_viewing(self, usercontributed):
		types = self.usercontributed_manager.getTypesForUserContributed(usercontributed)
		self.docsetView.data_source.update_with_docset(usercontributed, types, self.usercontributed_type_selected_for_viewing)
		self.docsetView.name = usercontributed.name
		self.docsetView.reload()
		self.navigation_view.push_view(self.docsetView)
	
	def usercontributed_type_selected_for_viewing(self, usercontributed, type):
		indexes = self.usercontributed_manager.getIndexesbyTypeForUserContributed(usercontributed, type)
		self.docsetIndexView.data_source.update_with_docset(usercontributed, indexes, self.docset_index_selected_for_viewing, 'usercontributed')
		self.docsetView.name = usercontributed.name
		self.docsetIndexView.reload()
		self.navigation_view.push_view(self.docsetIndexView)
		
	def docset_index_selected_for_viewing(self, url):
		self.docsetWebView.load_url(url)
		self.navigation_view.push_view(self.docsetWebView)
	
if __name__ == '__main__':
	try:
		py = PyDoc()
		py.navigation_view.present(hide_title_bar=True)
	except Exception as e:
		console.hide_activity()
		console.alert('Error occured', str(e), 'Ok', hide_cancel_button=True)
		
	
