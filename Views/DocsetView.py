
import ui

class DocsetView (object):
	def __init__(self):
		self.data = []
		self.docset = None
		self.indexSelectCallback = None
		
	def tableview_did_select(self, tableview, section, row):
		self.indexSelectCallback(self.docset, self.data[row])
		
	def tableview_number_of_sections(self, tableview):
		return 1
		
	def tableview_number_of_rows(self, tableview, section):
		return len(self.data)
		
	def tableview_cell_for_row(self, tableview, section, row):
		cell = ui.TableViewCell()
		cell.text_label.text = self.data[row].plural
		cell.accessory_type = 'disclosure_indicator'
		if not self.data[row].icon == None:
			cell.image_view.image = self.data[row].icon
		return cell
	
	def update_with_docset(self, docset, types, indexSelectCallback):
		self.data = types
		self.docset = docset
		self.indexSelectCallback = indexSelectCallback
	
	
def get_view():
	tv = ui.TableView()
	w,h = ui.get_screen_size()
	tv.width = w
	tv.height = h
	tv.flex = 'WH'
	tv.name = 'PyDoc'
	data = DocsetView()
	tv.delegate = data
	tv.data_source = data
	return tv
