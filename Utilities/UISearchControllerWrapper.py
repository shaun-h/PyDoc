# coding: utf-8
import ui
import ctypes
import dialogs
from objc_util import ObjCInstance, ObjCClass, ns, on_main_thread, CGPoint, CGRect, CGSize, create_objc_class, NSArray
from ctypes import c_float

UISearchController = ObjCClass('UISearchController')
NSObject = ObjCClass('NSObject')
UITableViewController = ObjCClass('UITableViewController')
UITableViewCell = ObjCClass('UITableViewCell')
UIImageView = ObjCClass('UIImageView')
UIColor = ObjCClass('UIColor')
UITextField = ObjCClass('UITextField')
UISearchBar = ObjCClass('UISearchBar')
Theme_Manager = None

def tableView_cellForRowAtIndexPath_(sel,cmd,tableView,indexPath):
	ip = ObjCInstance(indexPath)
	ds = ObjCInstance(sel)
	data = ds.data[ip.row()]
	tv = ObjCInstance(sel)
	cell = ui.TableViewCell('subtitle')
	cell.text_label.text = data['name']
	cell.detail_text_label.text = data['docsetname']
	cell.image_view.image = data['icon']
	cell.border_color = Theme_manager.currentTheme.borderColour
	cell.background_color = Theme_manager.currentTheme.backgroundColour
	cell.bg_color = Theme_manager.currentTheme.backgroundColour
	cell.tint_color = Theme_manager.currentTheme.tintColour
	cell.text_label.text_color = Theme_manager.currentTheme.textColour
	cell.detail_text_label.text_color = Theme_manager.currentTheme.subTextColour
	iv = ui.ImageView()
	cell.content_view.add_subview(iv)
	iv.image = data['type'].icon
	iv.width = 15
	iv.height = 15
	iv.x = cell.content_view.width - (iv.width * 2)
	iv.y = (cell.content_view.height) / 2 - (iv.height)
	iv.flex = 'L'
	return ObjCInstance(cell).ptr

def numberOfSectionsInTableView_(sel,cmd,tableView):
	return 1

def tableView_numberOfRowsInSection_(sel,cmd, tableView,section):
	ds = ObjCInstance(sel)
	return len(ds.data)

def tableView_didSelectRowAtIndexPath_(sel,cmd,tableView,indexPath):
	ds = ObjCInstance(sel)
	ip = ObjCInstance(indexPath)
	url = ds.data[ip.row()]['path']
	ds.selectCallBack(url)
	
def searchBar_textDidChange_(sel, cmd, searchBar, searchText):
	s = ObjCInstance(sel)
	if s.resultController.firstRun:
		s.resultController.tableView().position = CGPoint(s.resultController.tableView().position().x, s.resultController.tableView().position().y-40)
		s.resultController.firstRun = False
	
def searchBarTextDidBeginEditing_(sel, cmd, searchBar):
	s = ObjCInstance(sel)
	sb = ObjCInstance(searchBar)
	sb.becomeFirstResponder()
	sb.position = CGPoint(sb.position().x,sb.size().height*2-2)
	
def searchBarTextDidEndEditing_(sel, cmd, searchBar):
	sb = ObjCInstance(searchBar)

def searchBarCancelButtonClicked_(sel, cmd, searchBar):
	s = ObjCInstance(sel)
	sb = ObjCInstance(searchBar)
	sb.setText_('')
	sb.resignFirstResponder()
	
def searchBarSearchButtonClicked_(sel, cmd, searchBar):
	sb = ObjCInstance(searchBar)
	sb.resignFirstResponder()

def updateSearchResultsForSearchController_(sel, cmd, searchController):
	sc = ObjCInstance(searchController)
	text = sc.searchBar().text()
	scc = ObjCInstance(sel)
	tv = sc.resultController.tableView()
	tv.dataSource().data = scc.filter(str(text))
	tv.reloadData()

def createSearchDelegateClass():	
	methods = [searchBar_textDidChange_, searchBarTextDidBeginEditing_, searchBarTextDidEndEditing_, searchBarCancelButtonClicked_, searchBarSearchButtonClicked_, updateSearchResultsForSearchController_]
	protocols = ['UISearchBarDelegate', 'UISearchResultsUpdating']
	sd = create_objc_class('sd', NSObject, methods=methods, protocols=protocols, debug=True)
	return sd
	
def createTableViewDelegateClass(tm):
	methods = [tableView_cellForRowAtIndexPath_,tableView_numberOfRowsInSection_,numberOfSectionsInTableView_, tableView_didSelectRowAtIndexPath_]
	protocols = ['UITableViewDataSource', 'UITableViewDelegate']
	TVDataSourceAndDelegate = create_objc_class('TVDataSourceAndDelegate', NSObject, methods=methods, protocols=protocols, debug=True)
	TVDataSourceAndDelegate.tm = tm
	return TVDataSourceAndDelegate
	
class SearchTableView(ui.View):
	@on_main_thread
	def __init__(self, tableView, filterData, selectCallBack, theme_manager, *args, **kwargs):
		ui.View.__init__(self, *args, **kwargs)
		self.width, self.height = ui.get_screen_size()
		frame = CGRect(CGPoint(0, 0), CGSize(self.width, self.height))
		theme_manager_g = theme_manager
		self.theme_manager = theme_manager
		bkg_view = ui.View()
		bkg_view.background_color = self.theme_manager.currentTheme.backgroundColour
		self.tv = tableView
		self.tv.width = self.width
		self.tv.height = self.height
		self.tableView = ObjCInstance(self.tv)
		self.tableView.setBackgroundView(bkg_view)
		flex_width, flex_height = (1<<1), (1<<4)
		self.tableView.setAutoresizingMask_(flex_width|flex_height)
		self.selectCallBack = selectCallBack
		v = UITableViewController.alloc().init().autorelease()
		tvd = createTableViewDelegateClass(theme_manager)
		self.tb_ds = tvd.alloc().init().autorelease()

		v.tableView().setDataSource_(self.tb_ds)
		v.tableView().setDelegate_(self.tb_ds)
		v.tableView().dataSource().data = []
		v.tableView().dataSource().selectCallBack = self.performSelectCallBack
		self.searchController = UISearchController.alloc().initWithSearchResultsController_(v)
		self.searchController.resultController = v
		self.searchController.firstRun = True
		
		sd = createSearchDelegateClass()
		self.searchDelegate = sd.alloc().init().autorelease()
		self.searchDelegate.filter = filterData
		self.searchDelegate.resultController = v
		self.tableView.extendedLayoutIncludesOpaqueBars = True
		self.searchController.searchResultsUpdater = self.searchDelegate
		self.searchController.dimsBackgroundDuringPresentation = True
		self.searchController.hidesNavigationBarDuringPresentation = True
		self.searchController.searchBar().delegate = self.searchDelegate
		self.searchController.searchBar().setPlaceholder_(ns('Search'))
		self.tableView.tableHeaderView =self.searchController.searchBar();
		self.searchController.searchBar().sizeToFit();		
		tColour = tuple(int(self.theme_manager.currentTheme.searchTintColour.lstrip('#')[i:i+2], 16) for i in (0, 2 ,4))
		bTColour = tuple(int(self.theme_manager.currentTheme.searchBackgroundColour.lstrip('#')[i:i+2], 16) for i in (0, 2 ,4))
		tColour = (tColour[0]/255, tColour[1]/255, tColour[2]/255)
		bTColour = (bTColour[0]/255, bTColour[1]/255, bTColour[2]/255)
		searchTintColour = UIColor.colorWithRed_green_blue_alpha_(tColour[0], tColour[1], tColour[2], 1)
		self.searchController.searchBar().tintColor = searchTintColour
		searchBackgroundTintColour = UIColor.colorWithRed_green_blue_alpha_(bTColour[0], bTColour[1], bTColour[2], 1)
		self.searchController.searchBar().tintColor = searchTintColour
		self.searchController.searchBar().barTintColor = searchBackgroundTintColour


		# self.tb_ds.textColour = searchTColour
		self.tv.border_color = self.theme_manager.currentTheme.borderColour
		self.tv.background_color = self.theme_manager.currentTheme.backgroundColour
		self.tv.bg_color = self.theme_manager.currentTheme.backgroundColour		
		self.tv.tint_color = self.theme_manager.currentTheme.tintColour
		self.tv.separator_color = self.theme_manager.currentTheme.separatorColour
		bk_view = ui.View()
		bk_view.background_color = self.theme_manager.currentTheme.backgroundColour
		v.tableView().setBackgroundView(bk_view)
		
		self_objc = ObjCInstance(self)
		self_objc.addSubview_(self.tableView)
		self.tableView.release()
	
	def performSelectCallBack(self, url):
		self.searchController.active = False
		self.selectCallBack(url)


def getUIColourFromHex(hexColour):
	colour = tuple(int(hexColour.lstrip('#')[i:i+2], 16) for i in (0, 2 ,4))
	colour = (colour[0]/255, colour[1]/255, colour[2]/255)
	return UIColor.colorWithRed_green_blue_alpha_(colour[0], colour[1], colour[2], 1)
		
def get_view(tableview, filter, selectCallBack, theme_manager):
	my = SearchTableView(tableview, filter, selectCallBack, theme_manager)
	return my

