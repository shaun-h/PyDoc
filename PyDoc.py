from Managers import DocsetManager, ServerManager
from Views import DocsetManagementView, SettingsView, DocsetListView
import ui

class PyDoc(object):
	def __init__(self):
		self.docset_manager = DocsetManager.DocsetManager('Images/icons', ServerManager.ServerManager())
		self.main_view = self.setup_main_view()
		self.navigation_view = self.setup_navigation_view()
		self.management_view = self.setup_management_view()
		self.settings_view = self.setup_settings_view()
		
	def setup_navigation_view(self):
		nav_view = ui.NavigationView(self.main_view)
		return nav_view

	def setup_main_view(self):
		docsets = self.docset_manager.getDownloadedDocsets()
		main_view = DocsetListView.get_view(docsets)
		settings_button = ui.ButtonItem(title='Settings')
		settings_button.action = self.show_settings_view
		main_view.left_button_items = [settings_button]
		return main_view

	def setup_management_view(self):
		docsets = self.docset_manager.getAvailableDocsets()
		return DocsetManagementView.get_view(docsets, self.docset_manager.downloadDocset, self.docset_manager.getAvailableDocsets)
		
	def setup_settings_view(self):
		return SettingsView.get_view(self.management_view)
		
	def show_settings_view(self, sender):
		self.navigation_view.push_view(self.settings_view)
	
		
if __name__ == '__main__':
	py = PyDoc()
	py.navigation_view.present(hide_title_bar=True)
