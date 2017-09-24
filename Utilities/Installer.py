import requests
import os
import console
import shutil
import json
import zipfile
from io import BytesIO
def install():
	try:
		p = os.path.join(os.path.expanduser('~'),'Documents', 'PyDoc')
		if os.path.exists(p):
			op = console.alert('Please Check', 'Path ' + p + ' exists. Would you like to override it?', hide_cancel_button = True, button1='No', button2='Yes')
			if op == 2:
				shutil.rmtree(p)
			elif op == 1:
				return 
		os.makedirs(p)
		latestReleaseUrl = 'https://api.github.com/repos/shaun-h/pydoc/releases/latest'
		console.show_activity('Getting latest version')
		response = requests.get(latestReleaseUrl)
		release = json.loads(response.text)
		console.hide_activity()

		console.show_activity('Installing ' + release['tag_name'])
		request = requests.get(release['zipball_url'])
		file = zipfile.ZipFile(BytesIO(request.content))
		toRemove = file.namelist()[0]
		os.chdir(p)
		file.extractall()
		for filename in os.listdir(toRemove):
			shutil.move(os.path.join(toRemove, filename), filename)
		shutil.rmtree(toRemove)
		file.close()
		
		f = open('.version', 'w')
		f.write(release['tag_name'].replace('v',''))
		f.close()
		console.hide_activity()
		console.alert('Installed', release['tag_name'] + ' installed, please restart Pythonista', hide_cancel_button=True, button1 = 'Ok')			
	except requests.exceptions.ConnectionError as e:
			console.alert('Check your internet connection', 'Unable to check for update.', hide_cancel_button=True, button1 = 'Ok')
	
if __name__ == '__main__':
	install()
