import yaml
import os

class SettingsManager (object):
	def __init__(self):
		self.settingsStoreLoaction = '.settings'
		self.settings = {}
		self.load_settings()
		self.set_defaults()
		self.save_settings()
	
	def set_defaults(self):
		if not 'ui_style' in self.settings.keys():
			self.settings['ui_style'] = 'default'
			
	def load_settings(self):
		if os.path.exists(self.settingsStoreLoaction):
			with open(self.settingsStoreLoaction, 'r') as set:
				self.settings = yaml.load(set)
			
	def save_settings(self):
		with open(self.settingsStoreLoaction, 'w') as yaml_file:
			yaml.dump(self.settings, yaml_file, default_flow_style=False)
