import json
import yaml
import console
import os
import shutil

class MigrationManager (object):
	def __init__(self, dbmanager, docsetmanager, usercontributionmanager, docsetfolder):
		self.dbmanager = dbmanager 
		self.docsetmanager = docsetmanager
		self.usercontributedmanager = usercontributionmanager
		self.migrations = {'change_version_column_to_text':self.change_version_column_to_text}
		self.docsetfolder = docsetfolder
	
	def perform_migrations(self):
		for migration in self.migrations.keys():
			if self.check_migration_required(migration):
				action = self.migrations[migration]
				try:
					action()
					self.dbmanager.UpdateMigration(migration, True)
				except:
					self.dbmanager.UpdateMigration(migration, False)
					
	def change_version_column_to_text(self):
		req = len(self.dbmanager.InstalledDocsets()) > 0
		if req:
			console.hide_activity()
			console.alert('Breaking Change', 'A breaking database change is required. All docsets need to be removed.', 'Ok', hide_cancel_button=True)
			console.show_activity('Performing migrations')
			df = os.path.join(os.path.abspath('.'),self.docsetfolder)
			shutil.rmtree(df)
		if not os.path.exists(os.path.join(os.path.abspath('.'),self.docsetfolder)):
			os.mkdir(os.path.join(os.path.abspath('.'),self.docsetfolder))
		self.dbmanager.RunQueryOnDocsetDB('DROP TABLE IF EXISTS docsets;')
		self.dbmanager.RunQueryOnDocsetDB('CREATE TABLE IF NOT EXISTS docsets(ID INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT NOT NULL, Path TEXT NOT NULL, Type TEXT NOT NULL, Icon TEXT NOT NULL, Version TEXT NULL, OtherData TEXT NOT NULL);')
	
	def check_migration_required(self, name):
		dbmigration = self.dbmanager.GetMigration(name)
		if dbmigration == None:
			self.dbmanager.AddMigration(name)
			return True
		else:
			return not dbmigration[2]
