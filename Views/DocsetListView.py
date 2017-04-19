
import ui

class DocsetListView (object):
	def __init__(self, docsets, cheatsheets, usercontributed, docset_selected_callback, cheatsheet_selected_callback, usercontributed_selected_callback):
		self.docsets = docsets
		self.cheatsheets = cheatsheets
		self.usercontributed = usercontributed
		self.docset_selected_callback = docset_selected_callback
		self.cheatsheet_selected_callback = cheatsheet_selected_callback
		self.usercontributed_selected_callback = usercontributed_selected_callback
		self.docsetSection = -1
		self.cheatsheetSection = -1
		self.numberOfSections = 0
	
		
	def tableview_did_select(self, tableview, section, row):
		if section == self.docsetSection:
			self.docset_selected_callback(self.docsets[row])
		elif section == self.cheatsheetSection:
			self.cheatsheet_selected_callback(self.cheatsheets[row])
	
	def tableview_title_for_header(self, tableview, section):
		if section == self.docsetSection:
			return 'Docsets'
		elif section == self.cheatsheetSection:
			return 'Cheatsheets'	
	
	def tableview_number_of_sections(self, tableview):
		self.determineSections()
		return self.numberOfSections
		
	def tableview_number_of_rows(self, tableview, section):
		if section == self.docsetSection:
			return len(self.docsets)
		elif section == self.cheatsheetSection:
			return len(self.cheatsheets)
		
	def tableview_cell_for_row(self, tableview, section, row):
		cell = ui.TableViewCell()
		if section == self.docsetSection:
			cell.text_label.text = self.docsets[row]['name']
			cell.accessory_type = 'disclosure_indicator'
			if not self.docsets[row]['image'] == None:
				cell.image_view.image = self.docsets[row]['image']
		elif section == self.cheatsheetSection:
			cell.text_label.text = self.cheatsheets[row].name
			cell.accessory_type = 'disclosure_indicator'
			if not self.cheatsheets[row].image == None:
				cell.image_view.image = self.cheatsheets[row].image
		return cell
	
	def determineSections(self):
		self.numberOfSections = 0
		if len(self.docsets) > 0:
			self.docsetSection = self.numberOfSections
			self.numberOfSections = self.numberOfSections + 1
		if len(self.cheatsheets) > 0:
			self.cheatsheetSection = self.numberOfSections
			self.numberOfSections = self.numberOfSections + 1
	
tv = ui.TableView()
def get_view(docsets, cheatsheets, usercontributed, docset_selected_callback, cheatsheet_selected_callback, usercontrobuted_selected_callback):
	w,h = ui.get_screen_size()
	tv.width = w
	tv.height = h
	tv.flex = 'WH'
	tv.name = 'PyDoc'
	data = DocsetListView(docsets, cheatsheets, usercontributed, docset_selected_callback, cheatsheet_selected_callback, usercontrobuted_selected_callback)
	tv.delegate = data
	tv.data_source = data
	return tv

def refresh_view(docsets, cheatsheets):
	tv.data_source.docsets = docsets
	tv.data_source.cheatsheets = cheatsheets
	tv.reload_data()
	tv.reload()
	
