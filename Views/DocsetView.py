
import ui

class DocsetView (object):
	def __init__(self, theme_manager):
		self.data = []
		self.docset = None
		self.indexSelectCallback = None
		self.theme_manager = theme_manager
		
	def tableview_did_select(self, tableview, section, row):
		self.indexSelectCallback(self.docset, self.data[row])
		
	def tableview_number_of_sections(self, tableview):
		return 1
		
	def tableview_number_of_rows(self, tableview, section):
		return len(self.data)
		
	def tableview_cell_for_row(self, tableview, section, row):
		cell = ui.TableViewCell()
		cell.border_color = self.theme_manager.currentTheme.tintColour
		cell.background_color = self.theme_manager.currentTheme.backgroundColour
		cell.bar_tint_color = self.theme_manager.currentTheme.toolbarBackgroundColour
		cell.bg_color = self.theme_manager.currentTheme.backgroundColour
		cell.tint_color = self.theme_manager.currentTheme.tintColour
		cell.title_color = self.theme_manager.currentTheme.tintColour
		cell.text_label.text_color = self.theme_manager.currentTheme.textColour
		cell.text_label.text = self.data[row].plural
		cell.accessory_type = 'disclosure_indicator'
		selectedBackgroundView = ui.View()
		selectedBackgroundView.background_color = self.theme_manager.currentTheme.cellSelectionColour
		if not self.theme_manager.currentTheme.showCellSelection:
			selectedBackgroundView.alpha = 0
		cell.selected_background_view = selectedBackgroundView
		if not self.data[row].icon == None:
			cell.image_view.image = self.data[row].icon
		return cell
	
	def update_with_docset(self, docset, types, indexSelectCallback):
		self.data = types
		self.docset = docset
		self.indexSelectCallback = indexSelectCallback
	
	
def get_view(theme_manager):
	tv = ui.TableView()
	w,h = ui.get_screen_size()
	tv.width = w
	tv.height = h
	tv.flex = 'WH'
	tv.name = 'PyDoc'
	data = DocsetView(theme_manager)
	tv.delegate = data
	tv.data_source = data
	return tv
