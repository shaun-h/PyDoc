import ui 

class webViewDelegate (object):
	def __init__(self, invert):
		self.invert = invert
		self.js = js = """javascript: (
function () { 
// the css we are going to inject
var css = 'html {-webkit-filter: invert(100%);' +
    '-moz-filter: invert(100%);' + 
    '-o-filter: invert(100%);' + 
    '-ms-filter: invert(100%); }',

head = document.getElementsByTagName('head')[0],
style = document.createElement('style');

// a hack, so you can "invert back" clicking the bookmarklet again
if (!window.counter) { window.counter = 1;} else  { window.counter ++;
if (window.counter % 2 == 0) { var css ='html {-webkit-filter: invert(0%); -moz-filter:    invert(0%); -o-filter: invert(0%); -ms-filter: invert(0%); }'}
 };

style.type = 'text/css';
if (style.styleSheet){
style.styleSheet.cssText = css;
} else {
style.appendChild(document.createTextNode(css));
}

//injecting the css to the head
head.appendChild(style);
}());"""
	def webview_should_start_load(self, webview, url, nav_type):
		return True
	def webview_did_start_load(self, webview):
		pass
	def webview_did_finish_load(self, webview):
		if self.invert:
			webview.evaluate_javascript(self.js)
	def webview_did_fail_load(self, webview, error_code, error_msg):
		pass

def get_view(theme_manager):
	wv = ui.WebView()
	wvd = webViewDelegate(theme_manager.currentTheme.invertWebView)
	wv.delegate = wvd
	return wv
