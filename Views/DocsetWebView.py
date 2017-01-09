import ui 

wv = ui.WebView()
def get_view(url):
	wv = ui.WebView()
	wv.load_url(url)
	return wv
