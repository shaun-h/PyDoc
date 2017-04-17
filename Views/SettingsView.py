import ui
from objc_util import ObjCClass, NSURL, ns
	
class SettingsView (object):
	def __init__(self, docset_management_view, cheatsheet_management_view):
		self.data = ['Standard Docsets', 'Cheatsheets']
		self.ack_data = [{'text':'Dash','url':'https://kapeli.com/dash'}]
		self.manage_docset_row = 0
		self.manage_cheatsheet_row = 1
		self.docset_management_view = docset_management_view
		self.cheatsheet_management_view = cheatsheet_management_view 
		self.docset_section_number = 0
		self.ack_section_number = 1
		
	def tableview_did_select(self, tableview, section, row):
		if self.docset_section_number == section:
			#self.manage_docset_row[0] == section and self.manage_docset_row[1] == row:
			if self.manage_docset_row == row:
				tv.navigation_view.push_view(self.docset_management_view)
			elif self.manage_cheatsheet_row == row:
				tv.navigation_view.push_view(self.cheatsheet_management_view)
		if self.ack_section_number == section:
			if row == 0:
				self.open_url(self.ack_data[row]['url'])
			
		
	def tableview_number_of_sections(self, tableview):
		return 2
		
	def tableview_number_of_rows(self, tableview, section):
		if section == self.docset_section_number:
			return len(self.data)
		if section == self.ack_section_number:
			return len(self.ack_data)
		
	def tableview_cell_for_row(self, tableview, section, row):
		cell = ui.TableViewCell()
		if section == self.docset_section_number:
			cell.text_label.text = self.data[row]
			cell.accessory_type = 'disclosure_indicator'
		elif section == self.ack_section_number:
			cell.text_label.text = self.ack_data[row]['text']
		return cell
	
	def tableview_title_for_header(self, tableview, section):
		if section == self.docset_section_number:
			return 'Manage'
		if section == self.ack_section_number:
			return 'Docsets are provided by Dash the MacOS docset browser. Please checkout Dash please by clicking the link below.'
	
	def open_url(self, url):
		UIApplication = ObjCClass('UIApplication')
		sharedApplication = UIApplication.sharedApplication()
		internalurl = NSURL.URLWithString_(ns(url))
		sharedApplication.openURL_(internalurl)

tv = ui.TableView('grouped')
def get_view(docset_management_view, cheatsheet_management_view):
	w,h = ui.get_screen_size()
	tv.width = w
	tv.height = h
	tv.flex = 'WH'
	tv.name = 'Settings'
	data = SettingsView(docset_management_view, cheatsheet_management_view)
	tv.delegate = data
	tv.data_source = data
	return tv
	
#if __name__ == '__main__':
	#view = get_view(manag)
	#view.present()
