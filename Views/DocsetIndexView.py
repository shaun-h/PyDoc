
import ui
import os
from urllib.parse import quote

class DocsetIndexView (object):
	def __init__(self, theme_manager, stackOverflowOnlineCallback):
		self.data = []
		self.docset = None
		self.indexSelectCallback = None
		self.docsetType = None
		self.theme_manager = theme_manager
		self.stackOverflowOnlineCallback = stackOverflowOnlineCallback
		
		
	def tableview_did_select(self, tableview, section, row):
		if self.docsetType == 'docset':
			data = 'file://' + os.path.join(self.docset['path'], 'Contents/Resources/Documents', self.data[row]['path'])
			data = data.replace(' ', '%20').replace('<', '%3E').replace('>', '%3C')
		elif self.docsetType == 'cheatsheet':
			data = 'file://' + os.path.join(self.docset.path, 'Contents/Resources/Documents', self.data[row]['path'])
			data = data.replace(' ', '%20').replace('<', '%3E').replace('>', '%3C')
		elif self.docsetType == 'usercontributed':
			data = 'file://' + os.path.join(self.docset.path, 'Contents/Resources/Documents', self.data[row]['path'])
			data = data.replace(' ', '%20').replace('<', '%3E').replace('>', '%3C')
		elif self.docsetType == 'transfer':
			data = 'file://' + os.path.join(self.docset.path, 'Contents/Resources/Documents', self.data[row]['path'])
			data = data.replace(' ', '%20').replace('<', '%3E').replace('>', '%3C')
		elif self.docsetType == 'stackoverflow' and self.docset.type == 'Offline':
			#url = 'file://' + os.path.join(self.docset.path, 'Contents/Resources/Documents', self.data[row]['path'])
			data = self.stackOverflowOnlineCallback(self.data[row], self.docset)
		elif self.docsetType == 'stackoverflow' and self.docset.type == 'Online':
			data = self.data[row]['path']
			data = data.replace(' ', '%20').replace('<', '%3E').replace('>', '%3C')
		self.indexSelectCallback(data)
		
	def tableview_number_of_sections(self, tableview):
		return 1
		
	def tableview_number_of_rows(self, tableview, section):
		return len(self.data)
		
	def tableview_cell_for_row(self, tableview, section, row):
		cell = ui.TableViewCell()
		cell.text_label.text = self.data[row]['name']
		cell.accessory_type = 'disclosure_indicator'
		cell.border_color = self.theme_manager.currentTheme.tintColour
		cell.background_color = self.theme_manager.currentTheme.backgroundColour
		cell.bar_tint_color = self.theme_manager.currentTheme.toolbarBackgroundColour
		cell.bg_color = self.theme_manager.currentTheme.backgroundColour
		cell.tint_color = self.theme_manager.currentTheme.tintColour
		cell.title_color = self.theme_manager.currentTheme.tintColour
		cell.text_label.text_color = self.theme_manager.currentTheme.textColour
		selectedBackgroundView = ui.View()
		selectedBackgroundView.background_color = self.theme_manager.currentTheme.cellSelectionColour
		if not self.theme_manager.currentTheme.showCellSelection:
			selectedBackgroundView.alpha = 0
		cell.selected_background_view = selectedBackgroundView		
		if not self.data[row]['type'].icon == None:
			cell.image_view.image = self.data[row]['type'].icon
		return cell
	
	def update_with_docset(self, docset, indexes, indexSelectCallback, docsetType):
		self.data = indexes
		self.docset = docset
		self.indexSelectCallback = indexSelectCallback
		self.docsetType = docsetType


def get_view(theme_manger, stackOverflowOnlineCallback):
	tv = ui.TableView()
	w,h = ui.get_screen_size()
	tv.width = w
	tv.height = h
	tv.flex = 'WH'
	tv.name = 'PyDoc'
	data = DocsetIndexView(theme_manger, stackOverflowOnlineCallback)
	tv.delegate = data
	tv.data_source = data
	return tv
