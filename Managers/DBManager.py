import sqlite3

class DBManager (object):
	def __init__(self):
		self.docsetDBLocation = 'Docsets/docsets.db'
		self.connection = None
		self.SetupDocsetDB()
		
	def SetupDocsetDB(self):
		self.connection = sqlite3.connect(self.docsetDBLocation)
		c = self.connection.cursor()
		c.execute('CREATE TABLE IF NOT EXISTS docsets(ID INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT NOT NULL, Path TEXT NOT NULL, Type TEXT NOT NULL, Icon TEXT NOT NULL, Version REAL NULL, OtherData TEXT NOT NULL);')
		self.connection.commit()
	
	def DocsetInstalled(self, name, path, type, icon, version, otherdata = ''):
		c = self.connection.cursor()
		c.execute('INSERT INTO docsets (Name, Path, Type, Icon, Version, OtherData) VALUES (?,?,?,?,?,?)',(name,path,type,icon,version,otherdata,))
		self.connection.commit()
	
	def DocsetRemoved(self, id):
		c = self.connection.cursor()
		c.execute('DELETE FROM docsets WHERE ID = (?)',(id,))
		self.connection.commit()
	
	def InstalledDocsets(self):
		return self.connection.execute('SELECT * FROM docsets').fetchall()
	
	def InstalledDocsetsByType(self, type):
		return self.connection.execute('SELECT * FROM docsets WHERE type = (?) ORDER BY name COLLATE NOCASE', (type,)).fetchall()
		
