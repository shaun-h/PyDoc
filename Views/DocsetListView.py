
import ui

class DocsetListView (object):
	def __init__(self, docsets, cheatsheets, usercontributed, stackoverflows, transfers, docset_selected_callback, cheatsheet_selected_callback, usercontributed_selected_callback, stackoverflow_selected_callback, transfer_selected_callback, theme_manager):
		self.docsets = docsets
		self.cheatsheets = cheatsheets
		self.usercontributed = usercontributed
		self.stackoverflows = stackoverflows
		self.transfers = transfers
		self.docset_selected_callback = docset_selected_callback
		self.cheatsheet_selected_callback = cheatsheet_selected_callback
		self.usercontributed_selected_callback = usercontributed_selected_callback
		self.stackoverflow_selected_callback = stackoverflow_selected_callback
		self.transfer_selected_callback = transfer_selected_callback
		self.docsetSection = -1
		self.cheatsheetSection = -1
		self.usercontributedSection = -1
		self.stackoverflowSection = -1
		self.transfersSection = -1
		self.numberOfSections = 0
		self.theme_manager = theme_manager
	
		
	def tableview_did_select(self, tableview, section, row):
		if section == self.docsetSection:
			self.docset_selected_callback(self.docsets[row])
		elif section == self.cheatsheetSection:
			self.cheatsheet_selected_callback(self.cheatsheets[row])
		elif section == self.usercontributedSection:
			self.usercontributed_selected_callback(self.usercontributed[row])
		elif section == self.stackoverflowSection:
			self.stackoverflow_selected_callback(self.stackoverflows[row])
		elif section == self.transfersSection:
			self.transfer_selected_callback(self.transfers[row])
	
	def tableview_title_for_header(self, tableview, section):
		if section == self.docsetSection:
			return 'Docsets'
		elif section == self.cheatsheetSection:
			return 'Cheat Sheets'
		elif section == self.usercontributedSection:
			return 'User Contributed Docsets'	
		elif section == self.stackoverflowSection:
			return 'Stack Overflow Docsets'
		elif section == self.transfersSection:
			return 'Transferred Docsets'
		
	
	def tableview_number_of_sections(self, tableview):
		self.determineSections()
		return self.numberOfSections
		
	def tableview_number_of_rows(self, tableview, section):
		if section == self.docsetSection:
			return len(self.docsets)
		elif section == self.cheatsheetSection:
			return len(self.cheatsheets)
		elif section == self.usercontributedSection:
			return len(self.usercontributed)
		elif section == self.stackoverflowSection:
			return len(self.stackoverflows)
		elif section == self.transfersSection:
			return len(self.transfers)
		
		
	def tableview_cell_for_row(self, tableview, section, row):
		selectedBackgroundView = ui.View()
		selectedBackgroundView.background_color = self.theme_manager.currentTheme.cellSelectionColour
		if not self.theme_manager.currentTheme.showCellSelection:
			selectedBackgroundView.alpha = 0
		cell = ui.TableViewCell('subtitle')
		cell.border_color = self.theme_manager.currentTheme.tintColour
		cell.background_color = self.theme_manager.currentTheme.backgroundColour
		cell.bar_tint_color = self.theme_manager.currentTheme.toolbarBackgroundColour
		cell.bg_color = self.theme_manager.currentTheme.backgroundColour
		cell.tint_color = self.theme_manager.currentTheme.tintColour
		cell.title_color = self.theme_manager.currentTheme.tintColour
		cell.text_label.text_color = self.theme_manager.currentTheme.textColour
		cell.detail_text_label.text_color = self.theme_manager.currentTheme.subTextColour
		cell.selected_background_view = selectedBackgroundView
		if section == self.docsetSection:
			versionText = str(self.docsets[row]['version'])
			cell.text_label.text = self.docsets[row]['name'] + ' ' + versionText
			cell.accessory_type = 'disclosure_indicator'
			if not self.docsets[row]['image'] == None:
				cell.image_view.image = self.docsets[row]['image']
		elif section == self.cheatsheetSection:
			cell.text_label.text = self.cheatsheets[row].name + ' ' + str(self.cheatsheets[row].version)
			cell.accessory_type = 'disclosure_indicator'
			if not self.cheatsheets[row].image == None:
				cell.image_view.image = self.cheatsheets[row].image
		elif section == self.transfersSection:
			cell.text_label.text = self.transfers[row].name + ' ' + str(self.transfers[row].version)
			cell.accessory_type = 'disclosure_indicator'
			if not self.transfers[row].image == None:
				cell.image_view.image = self.transfers[row].image
		elif section == self.usercontributedSection:
			cell.text_label.text = self.usercontributed[row].name  + ' ' + str(self.usercontributed[row].version)
			cell.detail_text_label.text = 'Contributed by ' + self.usercontributed[row].authorName
			cell.accessory_type = 'disclosure_indicator'
			if not self.usercontributed[row].image == None:
				cell.image_view.image = self.usercontributed[row].image
		elif section == self.stackoverflowSection:
			head, _sep, tail = self.stackoverflows[row].name.rpartition(self.stackoverflows[row].type)
			cell.text_label.text = head + tail + ' (' +self.stackoverflows[row].type + ')' + ' ' + str(self.stackoverflows[row].version)
			cell.accessory_type = 'disclosure_indicator'
			if not self.stackoverflows[row].image == None:
				cell.image_view.image = self.stackoverflows[row].image
		return cell
	
	def determineSections(self):
		self.numberOfSections = 0
		if len(self.docsets) > 0:
			self.docsetSection = self.numberOfSections
			self.numberOfSections = self.numberOfSections + 1
		if len(self.cheatsheets) > 0:
			self.cheatsheetSection = self.numberOfSections
			self.numberOfSections = self.numberOfSections + 1
		if len(self.usercontributed) > 0:
			self.usercontributedSection = self.numberOfSections
			self.numberOfSections = self.numberOfSections + 1
		if len(self.stackoverflows) > 0:
			self.stackoverflowSection = self.numberOfSections
			self.numberOfSections = self.numberOfSections + 1
		if len(self.transfers) > 0:
			self.transfersSection = self.numberOfSections
			self.numberOfSections = self.numberOfSections + 1
	
tv = ui.TableView()
def get_view(docsets, cheatsheets, usercontributed, stackoverflows, transfers, docset_selected_callback, cheatsheet_selected_callback, usercontributed_selected_callback, stackoverflow_selected_callback, transfer_selected_callback, theme_manager):
	w,h = ui.get_screen_size()
	tv.width = w
	tv.height = h
	tv.flex = 'WH'
	tv.name = 'PyDoc'
	data = DocsetListView(docsets, cheatsheets, usercontributed, stackoverflows, transfers, docset_selected_callback, cheatsheet_selected_callback, usercontributed_selected_callback, stackoverflow_selected_callback, transfer_selected_callback, theme_manager)
	tv.delegate = data
	tv.data_source = data
	return tv

def refresh_view(docsets, cheatsheets, usercontributed, stackoverflows, transfers):
	tv.data_source.docsets = docsets
	tv.data_source.cheatsheets = cheatsheets
	tv.data_source.usercontributed = usercontributed
	tv.data_source.stackoverflows = stackoverflows
	tv.data_source.transfers = transfers
	tv.reload_data()
	tv.reload()
	
