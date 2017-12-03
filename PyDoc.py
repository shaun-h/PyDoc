from Managers import DocsetManager, ServerManager, CheatsheetManager, UserContributedManager, DBManager, ThemeManager, StackOverflowManager, WebSearchManager, TransferManager
from Views import DocsetManagementView, SettingsView, DocsetListView, DocsetView, DocsetIndexView, DocsetWebView, CheatsheetManagementView, UserContributedManagementView, StackOverflowManagementView, TransferManagementView, DocsetManagementVersionView
from Utilities import UISearchControllerWrapper
import ui
import console
import os
import time


class PyDoc(object):
	def __init__(self):
		console.show_activity('Loading...')
		self.docsetFolder = 'Docsets'
		self.setup()
		self.dbmanager = DBManager.DBManager()
		self.theme_manager = ThemeManager.ThemeManager('Themes')
		self.docset_manager = DocsetManager.DocsetManager('Images/icons', 'Images/types', ServerManager.ServerManager())
		self.cheatsheet_manager = CheatsheetManager.CheatsheetManager(ServerManager.ServerManager(), 'Images/icons', 'Images/types')
		self.usercontributed_manager = UserContributedManager.UserContributedManager(ServerManager.ServerManager(), 'Images/icons','Images/types')
		self.stackoverflow_manager = StackOverflowManager.StackOverflowManager(ServerManager.ServerManager(), 'Images/icons','Images/types')
		self.webSearchManager = WebSearchManager.WebSearchManager('Images/types')
		self.transfer_manager = TransferManager.TransferManager('Images/icons','Images/types')
		self.main_view = self.setup_main_view()
		self.navigation_view = self.setup_navigation_view()
		self.docset_management_version_view = self.setup_docset_management_version_view()
		self.docset_management_view = self.setup_docset_management_view()
		self.cheatsheet_management_view = self.setup_cheatsheetmanagement_view()
		self.usercontributed_management_view = self.setup_usercontributedmanagement_view()
		self.stackoverflow_management_view = self.setup_stackoverflowmanagement_view()
		self.transfer_management_view = self.setup_transfermanagement_view()
		self.settings_view = self.setup_settings_view()
		self.docsetView = self.setup_docset_view()
		self.docsetIndexView = self.setup_docsetindex_view()
		self.docsetWebView = self.setup_docsetweb_view()
		UISearchControllerWrapper.Theme_manager = self.theme_manager
		console.hide_activity()
	
	def setup(self):
		if not os.path.exists(self.docsetFolder):
			os.mkdir(self.docsetFolder)
		
	def setup_navigation_view(self):
		nav_view = ui.NavigationView(self.main_view)
		nav_view.border_color = self.theme_manager.currentTheme.borderColour
		nav_view.background_color = self.theme_manager.currentTheme.backgroundColour
		nav_view.bar_tint_color = self.theme_manager.currentTheme.toolbarBackgroundColour
		nav_view.bg_color = self.theme_manager.currentTheme.backgroundColour
		nav_view.tint_color = self.theme_manager.currentTheme.tintColour
		nav_view.title_color = self.theme_manager.currentTheme.textColour
		return nav_view

	def setup_main_view(self):
		docsets = self.docset_manager.getDownloadedDocsets()
		cheatsheets = self.cheatsheet_manager.getDownloadedCheatsheets()
		usercontributed = self.usercontributed_manager.getDownloadedUserContributed()
		stackoverflows = self.stackoverflow_manager.getDownloadedStackOverflows()
		transfers = self.transfer_manager.getInstalledDocsets()
		main_view = UISearchControllerWrapper.get_view(DocsetListView.get_view(docsets, cheatsheets, usercontributed, stackoverflows, transfers, self.docset_selected_for_viewing, self.cheatsheet_selected_for_viewing, self.usercontributed_selected_for_viewing, self.stackoverflow_selected_for_viewing, self.transfer_selected_for_viewing, self.theme_manager), self.search_all_docsets, self.docset_index_selected_for_viewing, self.theme_manager, self.build_offline_index_stackoverflow_selected_for_viewing)
		settings_button = ui.ButtonItem(title='Settings')
		settings_button.action = self.show_settings_view
		main_view.left_button_items = [settings_button]
		return main_view

	def setup_docset_management_view(self):
		docsets = self.docset_manager.getAvailableDocsets()
		docset_management_view = DocsetManagementView.get_view(docsets, self.docset_manager.downloadDocset, self.docset_manager.getAvailableDocsets, self.docset_manager.deleteDocset, self.refresh_main_view_data, self.theme_manager, self.show_docset_versions_view)
		docset_management_view.right_button_items = [ui.ButtonItem(action=self.checkStandardDocsetsForUpdate, title='Check for Update')]
		docset_management_view.background_color = self.theme_manager.currentTheme.backgroundColour
		docset_management_view.bar_tint_color = self.theme_manager.currentTheme.tintColour
		docset_management_view.bg_color = self.theme_manager.currentTheme.backgroundColour
		docset_management_view.tint_color = self.theme_manager.currentTheme.tintColour
		docset_management_view.title_color = self.theme_manager.currentTheme.textColour
		return docset_management_view
	
	def setup_docset_management_version_view(self):
		docset_management_view = DocsetManagementVersionView.get_view([], self.docset_manager.downloadDocset, self.docset_manager.getOnlineVersions, self.docset_manager.deleteDocset, self.refresh_main_view_data, self.theme_manager, None)
		docset_management_view.background_color = self.theme_manager.currentTheme.backgroundColour
		docset_management_view.bar_tint_color = self.theme_manager.currentTheme.tintColour
		docset_management_view.bg_color = self.theme_manager.currentTheme.backgroundColour
		docset_management_view.tint_color = self.theme_manager.currentTheme.tintColour
		docset_management_view.title_color = self.theme_manager.currentTheme.textColour
		return docset_management_view
	
	def refresh_main_view_data(self):
		docsets = self.docset_manager.getDownloadedDocsets()
		cheatsheets = self.cheatsheet_manager.getDownloadedCheatsheets()
		usercontributed = self.usercontributed_manager.getDownloadedUserContributed()
		stackoverflows = self.stackoverflow_manager.getDownloadedStackOverflows()
		transfers = self.transfer_manager.getInstalledDocsets()
		DocsetListView.refresh_view(docsets, cheatsheets, usercontributed, stackoverflows, transfers)
	
	def setup_cheatsheetmanagement_view(self):
		view = CheatsheetManagementView.get_view(self.cheatsheet_manager.downloadCheatsheet, self.refresh_main_view_data, self.cheatsheet_manager.deleteCheatsheet, self.cheatsheet_manager.getAvailableCheatsheets, self.theme_manager)
		view.right_button_items = [ui.ButtonItem(action=self.checkCheatsheetsForUpdate, title='Check for Update')]
		view.background_color = self.theme_manager.currentTheme.backgroundColour
		view.bar_tint_color = self.theme_manager.currentTheme.tintColour
		view.bg_color = self.theme_manager.currentTheme.backgroundColour
		view.tint_color = self.theme_manager.currentTheme.tintColour
		view.title_color = self.theme_manager.currentTheme.textColour
		return view
	
	def show_docset_versions_view(self, docset):
		versions = self.docset_manager.getOnlineVersions(docset)
		self.docset_management_version_view.data_source.data = versions
		self.docset_management_version_view.reload_data()
		self.navigation_view.push_view(self.docset_management_version_view)
		
	def show_docset_management_view(self):
		self.navigation_view.push_view(self.docset_management_view)
		
	def show_cheatsheetmanagement_view(self):
		self.cheatsheet_management_view.data_source.data = self.cheatsheet_manager.getAvailableCheatsheets()
		self.cheatsheet_management_view.reload()
		self.navigation_view.push_view(self.cheatsheet_management_view)
		console.hide_activity()
		
	def setup_usercontributedmanagement_view(self):
		view = UserContributedManagementView.get_view(self.usercontributed_manager.downloadUserContributed, self.refresh_main_view_data, self.usercontributed_manager.deleteUserContributed, self.usercontributed_manager.getAvailableUserContributed, self.theme_manager)
		view.right_button_items = [ui.ButtonItem(action=self.checkUserContributedForUpdate, title='Check for Update')]
		view.background_color = self.theme_manager.currentTheme.backgroundColour
		view.bar_tint_color = self.theme_manager.currentTheme.tintColour
		view.bg_color = self.theme_manager.currentTheme.backgroundColour
		view.tint_color = self.theme_manager.currentTheme.tintColour
		view.title_color = self.theme_manager.currentTheme.textColour
		return view
	
	def setup_stackoverflowmanagement_view(self):
		view = StackOverflowManagementView.get_view(self.stackoverflow_manager.downloadStackOverflow, self.refresh_main_view_data, self.stackoverflow_manager.deleteStackOverflow, self.stackoverflow_manager.getAvailableStackOverflows, self.theme_manager)
		view.right_button_items = [ui.ButtonItem(action=self.checkStackOverflowForUpdate, title='Check for Update')]
		view.background_color = self.theme_manager.currentTheme.backgroundColour
		view.bar_tint_color = self.theme_manager.currentTheme.tintColour
		view.bg_color = self.theme_manager.currentTheme.backgroundColour
		view.tint_color = self.theme_manager.currentTheme.tintColour
		view.title_color = self.theme_manager.currentTheme.textColour
		return view
	
	def show_stackoverflowmanagement_view(self):
		self.stackoverflow_management_view.data_source.data = self.stackoverflow_manager.getAvailableStackOverflows()
		self.stackoverflow_management_view.reload()
		self.navigation_view.push_view(self.stackoverflow_management_view)
		console.hide_activity()
		
	def show_usercontributedmanagement_view(self):
		self.usercontributed_management_view.data_source.data = self.usercontributed_manager.getAvailableUserContributed()
		self.usercontributed_management_view.reload()
		self.navigation_view.push_view(self.usercontributed_management_view)
		console.hide_activity()
	
	def setup_transfermanagement_view(self):
		view = TransferManagementView.get_view(self.transfer_manager.installDocset, self.refresh_main_view_data, self.transfer_manager.deleteDocset, self.transfer_manager.getAvailableDocsets, self.theme_manager, self.transfer_manager)
		view.background_color = self.theme_manager.currentTheme.backgroundColour
		view.bar_tint_color = self.theme_manager.currentTheme.tintColour
		view.bg_color = self.theme_manager.currentTheme.backgroundColour
		view.tint_color = self.theme_manager.currentTheme.tintColour
		view.title_color = self.theme_manager.currentTheme.textColour
		return view
		
	def show_transfermanagement_view(self):
		self.transfer_management_view.data = self.transfer_manager.getAvailableDocsets()
		self.transfer_management_view.reload()
		self.navigation_view.push_view(self.transfer_management_view)
	
	def setup_settings_view(self):
		settings_view = SettingsView.get_view(self.show_docset_management_view, self.show_cheatsheetmanagement_view, self.show_usercontributedmanagement_view, self.theme_manager, self.show_stackoverflowmanagement_view,self.webSearchManager, self.show_transfermanagement_view)
		settings_view.background_color = self.theme_manager.currentTheme.settingsBackgroundColour
		settings_view.bg_color = self.theme_manager.currentTheme.settingsBackgroundColour
		settings_view.tint_color = self.theme_manager.currentTheme.tintColour
		return settings_view
		
	def setup_docset_view(self):
		v = UISearchControllerWrapper.get_view(DocsetView.get_view(self.theme_manager), self.search_docset, self.docset_index_selected_for_viewing, self.theme_manager, self.build_offline_index_stackoverflow_selected_for_viewing)
		return v
		
	def setup_docsetindex_view(self):
		view = DocsetIndexView.get_view(self.theme_manager, self.stackoverflow_manager.buildOfflineDocsetHtml)
		view.background_color = self.theme_manager.currentTheme.backgroundColour
		view.bar_tint_color = self.theme_manager.currentTheme.tintColour
		view.bg_color = self.theme_manager.currentTheme.backgroundColour
		view.tint_color = self.theme_manager.currentTheme.tintColour
		view.title_color = self.theme_manager.currentTheme.textColour
		return view
		
	def setup_docsetweb_view(self):
		view = DocsetWebView.get_view(self.theme_manager)
		view.background_color = self.theme_manager.currentTheme.backgroundColour
		view.bar_tint_color = self.theme_manager.currentTheme.tintColour
		view.bg_color = self.theme_manager.currentTheme.backgroundColour
		view.tint_color = self.theme_manager.currentTheme.tintColour
		view.title_color = self.theme_manager.currentTheme.textColour
		return view
		
	def show_settings_view(self, sender):
		self.navigation_view.push_view(self.settings_view)
	
	def docset_selected_for_viewing(self, docset):
		types = self.docset_manager.getTypesForDocset(docset)
		self.docsetView.tv.data_source.update_with_docset(docset, types, self.docset_type_selected_for_viewing)
		self.docsetView.tv.filterData = self.docset_manager.getIndexesbyNameForDocsetSearch
		self.docsetView.name = docset['name']
		self.docsetView.tv.reload()
		self.navigation_view.push_view(self.docsetView)
	
	def docset_type_selected_for_viewing(self, docset, type):
		indexes = self.docset_manager.getIndexesbyTypeForDocset(docset, type)
		self.docsetIndexView.data_source.update_with_docset(docset, indexes, self.docset_index_selected_for_viewing, 'docset')
		self.docsetView.name = docset['name']
		self.docsetIndexView.reload()
		self.navigation_view.push_view(self.docsetIndexView)
	
	def cheatsheet_selected_for_viewing(self, cheatsheet):
		types = self.cheatsheet_manager.getTypesForCheatsheet(cheatsheet)
		self.docsetView.tv.data_source.update_with_docset(cheatsheet, types, self.cheatsheet_type_selected_for_viewing)
		self.docsetView.tv.filterData = self.cheatsheet_manager.getIndexesbyNameForDocsetSearch
		self.docsetView.name = cheatsheet.name
		self.docsetView.tv.reload()
		self.navigation_view.push_view(self.docsetView)
	
	def cheatsheet_type_selected_for_viewing(self, cheatsheet, type):
		indexes = self.cheatsheet_manager.getIndexesbyTypeForCheatsheet(cheatsheet, type)
		self.docsetIndexView.data_source.update_with_docset(cheatsheet, indexes, self.docset_index_selected_for_viewing, 'cheatsheet')
		self.docsetView.name = cheatsheet.name
		self.docsetIndexView.reload()
		self.navigation_view.push_view(self.docsetIndexView)
		
	def usercontributed_selected_for_viewing(self, usercontributed):
		types = self.usercontributed_manager.getTypesForUserContributed(usercontributed)
		self.docsetView.tv.data_source.update_with_docset(usercontributed, types, self.usercontributed_type_selected_for_viewing)
		self.docsetView.tv.filterData = self.usercontributed_manager.getIndexesbyNameForDocsetSearch
		self.docsetView.name = usercontributed.name
		self.docsetView.tv.reload()
		self.navigation_view.push_view(self.docsetView)
	
	def usercontributed_type_selected_for_viewing(self, usercontributed, type):
		indexes = self.usercontributed_manager.getIndexesbyTypeForUserContributed(usercontributed, type)
		self.docsetIndexView.data_source.update_with_docset(usercontributed, indexes, self.docset_index_selected_for_viewing, 'usercontributed')
		self.docsetView.name = usercontributed.name
		self.docsetIndexView.reload()
		self.navigation_view.push_view(self.docsetIndexView)
		
	def stackoverflow_selected_for_viewing(self, stackoverflow):
		types = self.stackoverflow_manager.getTypesForStackOverflow(stackoverflow)
		self.docsetView.tv.data_source.update_with_docset(stackoverflow, types, self.stackoverflow_type_selected_for_viewing)
		self.docsetView.tv.filterData = self.stackoverflow_manager.getIndexesbyNameForDocsetSearch
		head, _sep, tail = stackoverflow.name.rpartition(stackoverflow.type)
		self.docsetView.name = head + tail + ' (' +stackoverflow.type + ')'
		self.docsetView.tv.reload()
		self.navigation_view.push_view(self.docsetView)
		
	def stackoverflow_type_selected_for_viewing(self, stackoverflow, type):
		indexes = self.stackoverflow_manager.getIndexesbyTypeForStackOverflow(stackoverflow, type)
		index_callback = self.docset_index_selected_for_viewing
		if stackoverflow.type == 'Offline':
			index_callback = self.docset_index_for_offline_stackoverflow_selected_for_viewing
		self.docsetIndexView.data_source.update_with_docset(stackoverflow, indexes, index_callback, 'stackoverflow')
		self.docsetView.name = stackoverflow.name
		self.docsetIndexView.reload()
		self.navigation_view.push_view(self.docsetIndexView)
	
	def transfer_selected_for_viewing(self, docset):
		types = self.transfer_manager.getTypesForDocset(docset)
		self.docsetView.tv.data_source.update_with_docset(docset, types, self.transfer_type_selected_for_viewing)
		self.docsetView.tv.filterData = self.transfer_manager.getIndexesbyNameForDocsetSearch
		self.docsetView.name = docset.name
		self.docsetView.tv.reload()
		self.navigation_view.push_view(self.docsetView)
	
	def transfer_type_selected_for_viewing(self, docset, type):
		indexes = self.transfer_manager.getIndexesbyTypeForDocset(docset, type)
		self.docsetIndexView.data_source.update_with_docset(docset, indexes, self.docset_index_selected_for_viewing, 'transfer')
		self.docsetView.name = docset.name
		self.docsetIndexView.reload()
		self.navigation_view.push_view(self.docsetIndexView)
		
	def docset_index_selected_for_viewing(self, url):
		self.docsetWebView.load_url(url)
		self.docsetWebView.delegate.buttonHandler.showButtons = True
		self.navigation_view.push_view(self.docsetWebView)
	
	def build_offline_index_stackoverflow_selected_for_viewing(self, entry, docset):
		html = self.stackoverflow_manager.buildOfflineDocsetHtml(entry, docset)
		self.docset_index_for_offline_stackoverflow_selected_for_viewing(html)
	
	def docset_index_for_offline_stackoverflow_selected_for_viewing(self, data):
		self.docsetWebView.load_html(data)
		self.docsetWebView.delegate.buttonHandler.showButtons = False
		self.navigation_view.push_view(self.docsetWebView)
	
	def search_docset(self, name):
		if len(name) < 3:
			return []
		data = self.docsetView.tv.filterData(self.docsetView.tv.data_source.docset, name)
		r = []
		r.extend(data['first'])
		r.extend(data['second'])
		r.extend(data['third'])
		r.extend(data['fourth'])
		return r
		
		
		
	def search_all_docsets(self, name):
		if len(name) < 3:
			return self.webSearchManager.GetAllWebSearches(name)
		ret = []
		retEnd = []
		standard = self.docset_manager.getIndexesbyNameForAllDocset(name)
		cheatsheet = self.cheatsheet_manager.getIndexesbyNameForAllCheatsheet(name)
		usercontributed = self.usercontributed_manager.getIndexesbyNameForAllUserContributed(name)
		stackoverflow = self.stackoverflow_manager.getIndexesbyNameForAllStackOverflow(name)
		transfers = self.transfer_manager.getIndexesbyNameForAllDocsets(name)
		webSearches = self.webSearchManager.GetAllWebSearches(name)
		
		r = []
		if 'first' in standard.keys():
			r.extend(standard['first'])
		if 'first' in cheatsheet.keys():
			r.extend(cheatsheet['first'])
		if 'first' in usercontributed.keys():
			r.extend(usercontributed['first'])
		if 'first' in stackoverflow.keys():
			r.extend(stackoverflow['first'])
		if 'first' in transfers.keys():
			r.extend(transfers['first'])
		if 'second' in standard.keys():
			r.extend(standard['second'])
		if 'second' in cheatsheet.keys():
			r.extend(cheatsheet['second'])
		if 'second' in usercontributed.keys():
			r.extend(usercontributed['second'])
		if 'second' in stackoverflow.keys():
			r.extend(stackoverflow['second'])
		if 'second' in transfers.keys():
			r.extend(transfers['second'])		
		if 'third' in standard.keys():
			r.extend(standard['third'])
		if 'third' in cheatsheet.keys():
			r.extend(cheatsheet['third'])
		if 'third' in usercontributed.keys():
			r.extend(usercontributed['third'])
		if 'third' in stackoverflow.keys():
			r.extend(stackoverflow['third'])
		if 'third' in transfers.keys():
			r.extend(transfers['third'])
		if 'fourth' in standard.keys():
			r.extend(standard['fourth'])
		if 'fourth' in cheatsheet.keys():
			r.extend(cheatsheet['fourth'])	
		if 'fourth' in usercontributed.keys():
			r.extend(usercontributed['fourth'])
		if 'fourth' in stackoverflow.keys():
			r.extend(stackoverflow['fourth'])
		if 'fourth' in transfers.keys():
			r.extend(transfers['fourth'])
		r.extend(webSearches)
		return r
	
	@ui.in_background
	def checkStandardDocsetsForUpdate(self, sender):
		self.docset_manager.checkDocsetsForUpdates(self.docset_management_view.data_source.data)
		self.docset_management_view.reload()
		console.hide_activity()
	
	@ui.in_background
	def checkCheatsheetsForUpdate(self, sender):
		self.cheatsheet_manager.checkDocsetsForUpdates(self.cheatsheet_management_view.data_source.data)
		self.cheatsheet_management_view.reload()
		console.hide_activity()

	@ui.in_background
	def checkUserContributedForUpdate(self, sender):
		self.usercontributed_manager.checkDocsetsForUpdates(self.usercontributed_management_view.data_source.data)
		self.usercontributed_management_view.reload()
		console.hide_activity()

	@ui.in_background
	def checkStackOverflowForUpdate(self, sender):
		self.stackoverflow_manager.checkDocsetsForUpdates(self.stackoverflow_management_view.data_source.data)
		self.stackoverflow_management_view.reload()
		console.hide_activity()
		
if __name__ == '__main__':
	try:
		py = PyDoc()
		py.navigation_view.present(hide_title_bar=True)
	except Exception as e:
		console.hide_activity()
		console.alert('Error occured', str(e), 'Ok', hide_cancel_button=True)


	
