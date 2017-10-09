from Managers import DocsetManager, ServerManager, CheatsheetManager, UserContributedManager, DBManager, ThemeManager, StackOverflowManager, WebSearchManager
from Views import DocsetManagementView, SettingsView, DocsetListView, DocsetView, DocsetIndexView, DocsetWebView, CheatsheetManagementView, UserContributedManagementView, StackOverflowManagementView
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
		self.main_view = self.setup_main_view()
		self.navigation_view = self.setup_navigation_view()
		self.docset_management_view = self.setup_docset_management_view()
		self.cheatsheet_management_view = self.setup_cheatsheetmanagement_view()
		self.usercontributed_management_view = self.setup_usercontributedmanagement_view()
		self.stackoverflow_management_view = self.setup_stackoverflowmanagement_view()
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
		main_view = UISearchControllerWrapper.get_view(DocsetListView.get_view(docsets, cheatsheets, usercontributed, stackoverflows, self.docset_selected_for_viewing, self.cheatsheet_selected_for_viewing, self.usercontributed_selected_for_viewing, self.stackoverflow_selected_for_viewing, self.theme_manager), self.search_all_docsets, self.docset_index_selected_for_viewing, self.theme_manager, self.build_offline_index_stackoverflow_selected_for_viewing)
		settings_button = ui.ButtonItem(title='Settings')
		settings_button.action = self.show_settings_view
		main_view.left_button_items = [settings_button]
		return main_view

	def setup_docset_management_view(self):
		docsets = self.docset_manager.getAvailableDocsets()
		docset_management_view = DocsetManagementView.get_view(docsets, self.docset_manager.downloadDocset, self.docset_manager.getAvailableDocsets, self.docset_manager.deleteDocset, self.refresh_main_view_data, self.theme_manager)
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
		DocsetListView.refresh_view(docsets, cheatsheets, usercontributed, stackoverflows)
	
	def setup_cheatsheetmanagement_view(self):
		view = CheatsheetManagementView.get_view(self.cheatsheet_manager.downloadCheatsheet, self.refresh_main_view_data, self.cheatsheet_manager.deleteCheatsheet, self.cheatsheet_manager.getAvailableCheatsheets, self.theme_manager)
		view.background_color = self.theme_manager.currentTheme.backgroundColour
		view.bar_tint_color = self.theme_manager.currentTheme.tintColour
		view.bg_color = self.theme_manager.currentTheme.backgroundColour
		view.tint_color = self.theme_manager.currentTheme.tintColour
		view.title_color = self.theme_manager.currentTheme.textColour
		return view
		
	def show_docset_management_view(self):
		self.navigation_view.push_view(self.docset_management_view)
		
	def show_cheatsheetmanagement_view(self):
		self.cheatsheet_management_view.data_source.data = self.cheatsheet_manager.getAvailableCheatsheets()
		self.cheatsheet_management_view.reload()
		self.navigation_view.push_view(self.cheatsheet_management_view)
		console.hide_activity()
		
	def setup_usercontributedmanagement_view(self):
		view = UserContributedManagementView.get_view(self.usercontributed_manager.downloadUserContributed, self.refresh_main_view_data, self.usercontributed_manager.deleteUserContributed, self.usercontributed_manager.getAvailableUserContributed, self.theme_manager)
		view.background_color = self.theme_manager.currentTheme.backgroundColour
		view.bar_tint_color = self.theme_manager.currentTheme.tintColour
		view.bg_color = self.theme_manager.currentTheme.backgroundColour
		view.tint_color = self.theme_manager.currentTheme.tintColour
		view.title_color = self.theme_manager.currentTheme.textColour
		return view
	
	def setup_stackoverflowmanagement_view(self):
		view = StackOverflowManagementView.get_view(self.stackoverflow_manager.downloadStackOverflow, self.refresh_main_view_data, self.stackoverflow_manager.deleteStackOverflow, self.stackoverflow_manager.getAvailableStackOverflows, self.theme_manager)
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
		
	def setup_settings_view(self):
		settings_view = SettingsView.get_view(self.show_docset_management_view, self.show_cheatsheetmanagement_view, self.show_usercontributedmanagement_view, self.theme_manager, self.show_stackoverflowmanagement_view,self.webSearchManager)
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
		self.docsetView.tv.filterData = self.docset_manager.getIndexesbyNameForDocset
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
		self.docsetView.tv.filterData = self.cheatsheet_manager.getIndexesbyNameForDocset
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
		self.docsetView.tv.filterData = self.usercontributed_manager.getIndexesbyNameForDocset
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
		self.docsetView.tv.filterData = self.stackoverflow_manager.getIndexesbyNameForDocset
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
		firstData = [x for x in data if x['name']==name]
		data = [x for x in data if x not in firstData]
		secondData = [x for x in data if x['name'].startswith(name)]
		data = [x for x in data if x not in secondData]
		
		r = []
		r.extend(firstData)
		r.extend(secondData)
		r.extend(data)
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
		webSearches = self.webSearchManager.GetAllWebSearches(name)
	
		firstStandard = [x for x in standard if x['name']==name]
		standard = [x for x in standard if x not in firstStandard]
		secondStandard = [x for x in standard if x['name'].startswith(name)]
		standard = [x for x in standard if x not in secondStandard]

		firstCheatsheet = [x for x in cheatsheet if x['name']==name]
		cheatsheet = [x for x in cheatsheet if x not in firstCheatsheet]
		secondCheatsheet = [x for x in cheatsheet if x['name'].startswith(name)]
		cheatsheet = [x for x in cheatsheet if x not in secondCheatsheet]
		
		firstUsercontributed = [x for x in usercontributed if x['name']==name]
		usercontributed = [x for x in usercontributed if x not in firstUsercontributed]
		secondUsercontributed = [x for x in usercontributed if x['name'].startswith(name)]
		usercontributed = [x for x in usercontributed if x not in secondUsercontributed]
		
		firstStackoverflow = [x for x in stackoverflow if x['name']==name]
		stackoverflow = [x for x in stackoverflow if x not in firstStackoverflow]
		secondStackoverflow = [x for x in stackoverflow if x['name'].startswith(name)]
		stackoverflow = [x for x in stackoverflow if x not in secondStackoverflow]
		
		r = []
		r.extend(firstStandard)
		r.extend(firstCheatsheet)
		r.extend(firstUsercontributed)
		r.extend(firstStackoverflow)
		r.extend(secondStandard)
		r.extend(secondCheatsheet)
		r.extend(secondUsercontributed)
		r.extend(secondStackoverflow)
		r.extend(standard)
		r.extend(cheatsheet)
		r.extend(usercontributed)
		r.extend(stackoverflow)
		r.extend(retEnd)
		r.extend(webSearches)
		return r
	
if __name__ == '__main__':
	try:
		py = PyDoc()
		py.navigation_view.present(hide_title_bar=True)
	except Exception as e:
		console.hide_activity()
		console.alert('Error occured', str(e), 'Ok', hide_cancel_button=True)


	
