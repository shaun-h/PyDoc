from Managers import DocsetManager
from Views import DocsetManagementView

if __name__ == '__main__':
	m = DocsetManager.DocsetManager()
	docsets = m.getAvailableDocsets()
	view = DocsetManagementView.get_view(docsets, m.downloadDocset)
	view.present(hide_title_bar=True)
