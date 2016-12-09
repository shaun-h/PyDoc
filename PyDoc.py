from Managers import DocsetManager
from Views import DocsetManagementView
import ui

class PyDoc(object):
	def __init__(self):
		self.main_view = self.setup_main_view()
		self.navigation_view = self.setup_navigation_view()
		self.docset_manager = DocsetManager.DocsetManager('Images/icons')
		self.management_view = self.setup_management_view()
		
	def setup_navigation_view(self):
		nav_view = ui.NavigationView(self.main_view)
		return nav_view

	def setup_main_view(self):
		main_view = ui.View(name='PyDoc')
		settings_button = ui.ButtonItem(title='Settings')
		settings_button.action = self.show_management_view
		main_view.left_button_items = [settings_button]
		return main_view

	def setup_management_view(self):
		docsets = self.docset_manager.getAvailableDocsets()
		return DocsetManagementView.get_view(docsets, self.docset_manager.downloadDocset, self.docset_manager.getAvailableDocsets)
		
	def show_management_view(self, sender):
		self.navigation_view.push_view(self.management_view)
	
		
if __name__ == '__main__':
	py = PyDoc()
	py.navigation_view.present(hide_title_bar=True)
