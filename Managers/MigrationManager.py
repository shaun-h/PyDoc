import json
class MigrationManager (object):
	def __init__(self, dbmanager, docsetmanager, usercontributionmanager):
		self.dbmanager = dbmanager 
		self.docsetmanager = docsetmanager
		self.usercontributedmanager = usercontributionmanager
		self.migrations = {'update_docset_has_versions':self.update_docset_has_versions}
	
	def perform_migrations(self):
		for migration in self.migrations.keys():
			if self.check_migration_required(migration):
				action = self.migrations[migration]
				try:
					action()
					#self.dbmanager.UpdateMigration(migration, True)
				except:
					self.dbmanager.UpdateMigration(migration, False)
	
	def update_docset_has_versions(self):
		docsets = self.dbmanager.InstalledDocsets()
		downdocsets = self.docsetmanager.getDownloadedDocsets()
		for docset in docsets:
			if docset[3] == 'standard':
				hasVersions = False
				for ddocsets in downdocsets:
					if ddocsets['name'] == docset[1]:
						hasVersions = ddocsets['hasVersions']
				dict = {'hasVersions':hasVersions}
				st = json.dumps(dict)
				self.dbmanager.DocsetInstalled(docset[1], docset[2], docset[3], docset[4], docset[5], st)
				self.dbmanager.DocsetRemoved(docset[0])
	
	def check_migration_required(self, name):
		dbmigration = self.dbmanager.GetMigration(name)
		if dbmigration == None:
			self.dbmanager.AddMigration(name)
			return True
		else:
			return not dbmigration[2]
