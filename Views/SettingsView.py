import ui
	
class SettingsView (object):
	def __init__(self, management_view):
		self.data = ['Manage Docsets']
		self.manage_docset_row = [0,0]
		self.management_view = management_view
		
	def tableview_did_select(self, tableview, section, row):
		if self.manage_docset_row[0] == section and self.manage_docset_row[1] == row:
			tv.navigation_view.push_view(self.management_view)
			
		
	def tableview_number_of_sections(self, tableview):
		return 1
		
	def tableview_number_of_rows(self, tableview, section):
		return len(self.data)
		
	def tableview_cell_for_row(self, tableview, section, row):
		cell = ui.TableViewCell()
		cell.text_label.text = self.data[row]
		cell.accessory_type = 'disclosure_indicator'
		return cell
	
	def tableview_title_for_header(self, tableview, section):
		return 'Docsets'

tv = ui.TableView('grouped')
def get_view(management_view):
	w,h = ui.get_screen_size()
	tv.width = w
	tv.height = h
	tv.flex = 'WH'
	tv.name = 'Settings'
	data = SettingsView(management_view)
	tv.delegate = data
	tv.data_source = data
	return tv
	
#if __name__ == '__main__':
	#view = get_view(manag)
	#view.present()
