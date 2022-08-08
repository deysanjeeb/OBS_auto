import sys 
import time
from os.path import exists
from obswebsocket import obsws, events, requests
import PySimpleGUI as sg

file_exists = exists("config.py")
if file_exists:
	import config
	host = config.host
	port= config.port
	secret = config.secret
else:
	event, values = sg.Window('Login Window',
	[[sg.T('host'), sg.In(key='host')],
	[sg.T('port'), sg.In(key='port')],
	[sg.T('secret'), sg.In(key='secret')],
	[sg.B('OK'), sg.B('Cancel') ]]).read(close=True)
	
	host = values['host']
	port= values['port']
	secret = values['secret']
	file = open("config.py", "w")
	file.write("host = '"+host+"'\n")
	file.write("port = '"+port+"'\n")
	file.write("secret = '"+secret+"'\n")
	file.close()

ws = obsws(host, port, secret)
ws.connect()

try:
	scenes = ws.call(requests.GetSceneList())
	for s in scenes.getScenes():
		name = s['name']
		print(u"Switching to {}".format(name))
		ws.call(requests.SetCurrentScene(name))
		time.sleep(2)

	print("End of list")

except KeyboardInterrupt:
	pass

ws.disconnect()