import ui 

class webViewDelegate (object):
	def __init__(self, invert, buttonHandler):
		self.invert = invert
		self.buttonHandler = buttonHandler
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
		webview.right_button_items = self.buttonHandler.getStopButtons()
	def webview_did_finish_load(self, webview):
		webview.right_button_items = self.buttonHandler.getReloadButtons()
		if self.invert:
			webview.evaluate_javascript(self.js)
	def webview_did_fail_load(self, webview, error_code, error_msg):
		webview.right_button_items = self.buttonHandler.getReloadButtons()

class buttonHandler (object):
	def __init__(self, webView, tintColour):
		self.webView = webView
		self.tintColour = tintColour
		self.showButtons = True
		
	def reload(self, sender):
		self.webView.reload()
		
	def back(self, sender):
		self.webView.go_back()
	
	def forward(self, sender):
		self.webView.go_forward()
	
	def stop(self, sender):
		self.webView.stop()

	def getReloadButtons(self):
		rightBarButtons = []
		rightBarButtons.append(ui.ButtonItem(image = ui.Image.named('iob:ios7_refresh_empty_32'), action = self.reload, tint_color = self.tintColour))
		rightBarButtons.append(ui.ButtonItem(image = ui.Image.named('iob:ios7_arrow_forward_32'), action = self.forward, tint_color = self.tintColour))
		rightBarButtons.append(ui.ButtonItem(image = ui.Image.named('iob:ios7_arrow_back_32'), action= self.back, tint_color = self.tintColour))
		if self.showButtons:
			return  rightBarButtons
		else:
			return []
	
	def getStopButtons(self):
		rightBarButtons = []
		rightBarButtons.append(ui.ButtonItem(image = ui.Image.named('iob:close_round_24'), action = self.stop, tint_color = self.tintColour))
		rightBarButtons.append(ui.ButtonItem(image = ui.Image.named('iob:ios7_arrow_forward_32'), action = self.forward, tint_color = self.tintColour))
		rightBarButtons.append(ui.ButtonItem(image = ui.Image.named('iob:ios7_arrow_back_32'), action= self.back, tint_color = self.tintColour))
		if self.showButtons:
			return  rightBarButtons
		else:
			return []

def get_view(theme_manager):
	wv = ui.WebView()
	bh = buttonHandler(wv, theme_manager.currentTheme.tintColour)
	wvd = webViewDelegate(theme_manager.currentTheme.invertWebView, bh)
	wv.delegate = wvd
	
	wv.right_button_items = bh.getReloadButtons()
	return wv
