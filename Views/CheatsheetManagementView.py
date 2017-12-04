import ui

class CheatsheetManagementView (object):
	def __init__(self, download_action, refresh_main_view, delete_action, refresh_cheatsheets_action, theme_manager):
		self.data = []
		self.delete_action = delete_action
		self.download_action = download_action
		self.refresh_main_view = refresh_main_view
		self.refresh_cheatsheets_action = refresh_cheatsheets_action
		self.theme_manager = theme_manager
		
		
	def tableview_did_select(self, tableview, section, row):
		pass
		
	def tableview_number_of_sections(self, tableview):
		return 1
		
	def tableview_number_of_rows(self, tableview, section):
		return len(self.data)
		
	def tableview_cell_for_row(self, tableview, section, row):
		status = self.data[row].status
		cell = ui.TableViewCell('subtitle')
		cell.text_label.text = self.data[row].name
		cell.border_color = self.theme_manager.currentTheme.tintColour
		cell.background_color = self.theme_manager.currentTheme.backgroundColour
		cell.bar_tint_color = self.theme_manager.currentTheme.tintColour
		cell.bg_color = self.theme_manager.currentTheme.backgroundColour
		cell.tint_color = self.theme_manager.currentTheme.tintColour
		cell.text_label.text_color = self.theme_manager.currentTheme.textColour
		cell.detail_text_label.text_color = self.theme_manager.currentTheme.subTextColour
		if not status == 'downloading':
			cell.detail_text_label.text = status
		else:
			cell.detail_text_label.text = self.data[row].stats
		if not self.data[row].image == None:
			cell.image_view.image = self.data[row].image
		iv = self.__getDetailButtonForStatus(status, cell.height, self.action, self.data[row])
		iv.x = cell.content_view.width - (iv.width * 1.5)
		iv.y = (cell.content_view.height) - (iv.height * 1.05)
		iv.flex = 'L'
		cell.content_view.add_subview(iv)
		cell.selectable = False
		return cell
		
	def __getDetailImageForStatus(self, status):
		if status == 'online' or status == 'Update Available':
			return 'iob:ios7_cloud_download_outline_24'
		else:
			return 'iob:ios7_close_outline_24'
			
	def __getDetailButtonForStatus(self, status, height, action, row):
		img = ui.Image.named(self.__getDetailImageForStatus(status))
		button = ui.Button()
		button.image = img
		size = img.size
		ratio = size.y / size.x
		button.height = height * 0.9
		button.width = button.height * ratio
		ca = CustomAction(button)
		ca.action = self.action
		ca.row = row
		button.action = ca
		return button

	def refresh_all_views(self):
		self.refresh_main_view()
		d = self.refresh_cheatsheets_action()
		refresh_view(d)
						
	def action(self, sender):
		if sender.action.row.status == 'Update Available':
			sender.action.row.status = 'removing...'
			self.refresh()
			self.delete_action(sender.action.row, None, False)
			sender.action.row.path = None
			self.download_action(sender.action.row, self.refresh, self.refresh_all_views)
		else:
			if not sender.action.row.path == None:
				self.delete_action(sender.action.row, self.refresh_all_views)
				sender.action.row.path = None
			else:
				self.download_action(sender.action.row, self.refresh, self.refresh_all_views)
				
	def refresh(self):
		tv.reload()
		
class CustomAction(object):
	def __init__(self, parent):
		self.obj = parent
		self.action = self.real_action
		self.row = None
		
	def __call__(self, sender):
		return self.action(sender)
		
	def real_action(self, sender):
		print('Did you need to set the action?')

tv = ui.TableView()
def get_view(download_action, refresh_all_views, delete_action, refresh_cheatsheets_action, theme_manager):
	w,h = ui.get_screen_size()
	tv.width = w
	tv.height = h
	tv.flex = 'WH'
	tv.name = 'Cheatsheets'
	data = CheatsheetManagementView(download_action, refresh_all_views, delete_action, refresh_cheatsheets_action, theme_manager)
	tv.delegate = data
	tv.data_source = data
	return tv
	
def refresh_view(data):
	tv.data_source.data = data
	tv.reload_data()

if __name__ == '__main__':
	view = get_view([{'name':'test','status':'online'},{'name':'test2','status':'downloaded'}])
	view.present()

