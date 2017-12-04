import ui
import console
import objc_util
class TransferManagementView (object):
	def __init__(self, install_action, refresh_main_view, delete_action, refresh_transfer_action, theme_manager, transfer_manager, tv):
		self.data = refresh_transfer_action()
		self.delete_action = delete_action
		self.install_action = install_action
		self.refresh_main_view = refresh_main_view
		self.refresh_transfer_action = refresh_transfer_action
		self.theme_manager = theme_manager
		self.transfer_manager = transfer_manager
		self.view = tv
		button = self.getButton()
		self.view.right_button_items = [button]
		
	def getButton(self):
		title = ''
		action = None
		if self.transfer_manager.running:
			title = 'Stop Server'
			action = self.stopServer
		else:
			title = 'Start Server'
			action = self.startServer
		return ui.ButtonItem(title=title, action=action)
	
	def startServer(self, sender):
		try:
			data = self.transfer_manager.startTransferService('Resources', 'Docsets/Transfer', 8080, self.refresh_all_views)
			console.alert('Started', 'Server is available on http://' + str(data['hostname']) + ':' + str(data['port']) + ' IP:' + str(data['ip']), hide_cancel_button = True, button1='Ok')
			button = self.getButton()
			self.view.right_button_items = [button]
		except OSError as e:
			console.alert('Error', 'Unable to start http server, please restart Pythonista \r'+ e.strerror, hide_cancel_button = True, button1='Ok')

	@objc_util.on_main_thread
	def stopServer(self, sender):
		self.transfer_manager.stopTransferService(self.refresh_all_views)
		button = self.getButton()
		self.view.right_button_items = [button]
		
		
	def tableview_did_select(self, tableview, section, row):
		pass
		
	def tableview_number_of_sections(self, tableview):
		return len(self.data.keys())
		
	def tableview_number_of_rows(self, tableview, section):
		k = list(self.data.keys())[section]
		return len(self.data[k])
		
	def tableview_title_for_header(self, tableview, section):
		return list(self.data.keys())[section]
		
	def tableview_cell_for_row(self, tableview, section, row):
		k = list(self.data.keys())[section]
		cell = ui.TableViewCell('subtitle')
		cell.text_label.text = self.data[k][row].name
		cell.border_color = self.theme_manager.currentTheme.tintColour
		cell.background_color = self.theme_manager.currentTheme.backgroundColour
		cell.bar_tint_color = self.theme_manager.currentTheme.tintColour
		cell.bg_color = self.theme_manager.currentTheme.backgroundColour
		cell.tint_color = self.theme_manager.currentTheme.tintColour
		cell.text_label.text_color = self.theme_manager.currentTheme.textColour
		cell.detail_text_label.text_color = self.theme_manager.currentTheme.subTextColour
		if not self.data[k][row].status == 'Installing':
			cell.detail_text_label.text = self.data[k][row].status
		else:
			cell.detail_text_label.text = self.data[k][row].stats
		if not self.data[k][row].image == None:
			cell.image_view.image = self.data[k][row].image
		iv = self.__getDetailButtonForStatus(self.data[k][row].status, cell.height, self.action, self.data[k][row])
		iv.x = cell.content_view.width - (iv.width * 1.5)
		iv.y = (cell.content_view.height) - (iv.height * 1.05)
		iv.flex = 'L'
		cell.content_view.add_subview(iv)
		cell.selectable = False
		return cell
		
	def __getDetailImageForStatus(self, status):
		if status == 'Not Installed':
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
		d = self.refresh_transfer_action()
		self.data = d
		self.view.reload()
	
	@ui.in_background				
	def action(self, sender):
		if not sender.action.row.path == None:
			sender.action.row.status = 'removing...'
			self.refresh()
			self.delete_action(sender.action.row, self.refresh_all_views)
			sender.action.row.path = None
		else:
			self.install_action(sender.action.row, self.refresh, self.refresh_all_views)
				
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
def get_view(download_action, refresh_all_views, delete_action, refresh_transfer_action, theme_manager, transfer_manager):
	w,h = ui.get_screen_size()
	tv.width = w
	tv.height = h
	tv.flex = 'WH'
	tv.name = 'Transferred Docsets'
	data = TransferManagementView(download_action, refresh_all_views, delete_action, refresh_transfer_action, theme_manager, transfer_manager, tv)
	tv.delegate = data
	tv.data_source = data
	return tv
	
def refresh_view(data):
	tv.data_source.data = data
	tv.reload_data()
	tv.reload()
def refresh_v():
	tv.reload()

if __name__ == '__main__':
	view = get_view([{'name':'test','status':'online'},{'name':'test2','status':'downloaded'}])
	view.present()
