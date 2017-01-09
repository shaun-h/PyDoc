
import ui
import os

class DocsetIndexView (object):
	def __init__(self, docset, indexes, indexSelectCallback):
		self.data = indexes
		self.docset = docset
		self.indexSelectCallback = indexSelectCallback
		
	def tableview_did_select(self, tableview, section, row):
		url = 'file://' + os.path.join(self.docset['path'], 'Contents/Resources/Documents', self.data[row]['path'])
		self.indexSelectCallback(url)
		
	def tableview_number_of_sections(self, tableview):
		return 1
		
	def tableview_number_of_rows(self, tableview, section):
		return len(self.data)
		
	def tableview_cell_for_row(self, tableview, section, row):
		cell = ui.TableViewCell()
		cell.text_label.text = self.data[row]['name']
		cell.accessory_type = 'disclosure_indicator'
		if not self.data[row]['type']['image'] == None:
			cell.image_view.image = self.data[row]['type']['image']
		return cell
	
tv = ui.TableView()
def get_view(docsets, indexes, indexSelectCallback):
	tv = ui.TableView()
	w,h = ui.get_screen_size()
	tv.width = w
	tv.height = h
	tv.flex = 'WH'
	tv.name = 'PyDoc'
	data = DocsetIndexView(docsets, indexes, indexSelectCallback)
	tv.delegate = data
	tv.data_source = data
	tv.name = docsets['name']
	return tv
