# coding: utf-8
import ui
import ctypes
import dialogs
from objc_util import ObjCInstance, ObjCClass, ns, on_main_thread, CGPoint, CGRect, CGSize, create_objc_class

UISearchBar = ObjCClass('UISearchBar')
NSObject = ObjCClass('NSObject')

class tv (object):
	def __init__(self, data, tv):
		self.data = data
		self.filteredData = data
		self.tv = tv
		
	def tableview_did_select(self, tableview, section, row):
		pass
		
	def tableview_number_of_sections(self, tableview):
		return 1

	def tableview_number_of_rows(self, tableview, section):
		return len(self.filteredData)
		
	def tableview_cell_for_row(self, tableview, section, row):
		cell = ui.TableViewCell()
		cell.text_label.text = self.filteredData[row]
		return cell
	
	def filterData(self, text):
		if text == '':
			self.filteredData = self.data
		else:
			ff = []
			for d in self.data:
				if(d.lower().find(str(text).lower())>-1):
					ff.append(d)
			self.filteredData = ff
		self.tv.reload()	
		
def searchBar_textDidChange_(sel, cmd, searchBar, searchText):
	sb = ObjCInstance(searchBar)
	s = ObjCInstance(sel)
	ObjCInstance(sel).filt(sb.text())

def searchBarTextDidBeginEditing_(sel, cmd, searchBar):
	sb = ObjCInstance(searchBar)
	sb.becomeFirstResponder()
	
def searchBarTextDidEndEditing_(sel, cmd, searchBar):
	sb = ObjCInstance(searchBar)

def searchBarCancelButtonClicked_(sel, cmd, searchBar):
	s = ObjCInstance(sel)
	s.filt('')
	sb = ObjCInstance(searchBar)
	sb.setText_('')
	sb.resignFirstResponder()
	
def searchBarSearchButtonClicked_(sel, cmd, searchBar):
	sb = ObjCInstance(searchBar)
	sb.resignFirstResponder()
	
def createSearchDelegateClass():
		
	methods = [searchBar_textDidChange_, searchBarTextDidBeginEditing_, searchBarTextDidEndEditing_, searchBarCancelButtonClicked_, searchBarSearchButtonClicked_]
	protocols = ['UISearchBarDelegate']
	try:
		sd = ObjCClass('sd')
		return sd
	except ValueError:
		sd = create_objc_class('sd', NSObject, methods=methods, protocols=protocols, debug=False)
		return sd
	
class SearchTableView(ui.View):
	@on_main_thread
	def __init__(self, tableView, filterData, *args, **kwargs):
		ui.View.__init__(self, *args, **kwargs)
		frame = CGRect(CGPoint(0, 0), CGSize(self.width, self.height))
		self.tv = tableView
		self.tableView = ObjCInstance(self.tv)
		flex_width, flex_height = (1<<1), (1<<4)
		self.tableView.setAutoresizingMask_(flex_width|flex_height)
		sd = createSearchDelegateClass()
		self.searchDelegate = sd.alloc().init().autorelease()
		self.searchDelegate.filt = filterData
		searchBar = UISearchBar.alloc().init()
		searchBar.setPlaceholder_(ns('Search'))
		searchBar.setDelegate_(self.searchDelegate)
		#searchBar.setShowsBookmarkButton_(ns(True))
		searchBar.setShowsCancelButton_(ns(True))
		#searchBar.setShowsSearchResultsButton_(ns(True))
		#searchBar.setScopeButtonTitles_(ns(['test1','hi']))
		#searchBar.setShowsScopeBar(ns(True))
		
		self.tableView.setTableHeaderView_(searchBar)
		searchBar.sizeToFit()
		
		self_objc = ObjCInstance(self)
		self_objc.addSubview_(self.tableView)
		self.tableView.release()

def get_view(tableview, filter):
	my = SearchTableView(tableview, filter)
	return my
	
	
if __name__ == '__main__':
	
	v = ui.TableView()
	data = tv(['test1','test2'],v)
	
	v.data_source = data
	v.delegate = data
	my = get_view(v, data.filterData)

	my.present(hide_title_bar=True)
