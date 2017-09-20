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

def tableView_cellForRowAtIndexPath_(sel,cmd,tableView,indexPath):
	ip = ObjCInstance(indexPath)
	ds = ObjCInstance(sel)
	data = ds.data[ip.row()]
	cell = ui.TableViewCell('subtitle')
	cell.text_label.text = data['name']
	cell.detail_text_label.text = data['docsetname']
	cell.image_view.image = data['icon']
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
	
def createTableViewDelegateClass():
	methods = [tableView_cellForRowAtIndexPath_,tableView_numberOfRowsInSection_,numberOfSectionsInTableView_, tableView_didSelectRowAtIndexPath_]
	protocols = ['UITableViewDataSource', 'UITableViewDelegate']
	TVDataSourceAndDelegate = create_objc_class('TVDataSourceAndDelegate', NSObject, methods=methods, protocols=protocols, debug=True)
	return TVDataSourceAndDelegate
	
class SearchTableView(ui.View):
	@on_main_thread
	def __init__(self, tableView, filterData, selectCallBack, *args, **kwargs):
		ui.View.__init__(self, *args, **kwargs)
		self.width, self.height = ui.get_screen_size()
		frame = CGRect(CGPoint(0, 0), CGSize(self.width, self.height))
		self.tv = tableView
		self.tv.width = self.width
		self.tv.height = self.height
		self.tableView = ObjCInstance(self.tv)
		flex_width, flex_height = (1<<1), (1<<4)
		self.tableView.setAutoresizingMask_(flex_width|flex_height)
		self.selectCallBack = selectCallBack
		v = UITableViewController.alloc().init().autorelease()
		tvd = createTableViewDelegateClass()
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
		
		#searchBar = UISearchBar.alloc().init()
		#searchBar.setPlaceholder_(ns('Search'))
		#searchBar.setDelegate_(self.searchDelegate)
		#searchBar.setShowsBookmarkButton_(ns(True))
		#searchBar.setShowsCancelButton_(ns(True))
		#searchBar.setShowsSearchResultsButton_(ns(True))
		#searchBar.setScopeButtonTitles_(ns(['test1','hi']))
		#searchBar.setShowsScopeBar(ns(True))
		
		#self.tableView.setTableHeaderView_(searchBar)
		#searchBar.sizeToFit()
		
		self_objc = ObjCInstance(self)
		self_objc.addSubview_(self.tableView)
		self.tableView.release()
	
	def performSelectCallBack(self, url):
		self.searchController.active = False
		self.selectCallBack(url)



def get_view(tableview, filter, selectCallBack):
	my = SearchTableView(tableview, filter, selectCallBack)
	return my

