import sys 
import time
from os.path import exists
from obswebsocket import obsws, events, requests
import PySimpleGUI as sg
import json, sys, os, time, csv
from flask import Flask,request
from flask import render_template
from flask import current_app as app
import pandas
import socket, threading
import asyncio
from threading import Event

app = Flask(__name__)
app.app_context().push()
thr=0
print(thr)
async def tasks(commands):
	while True:
		for i in commands.index:		
			print(u"Switching to {} in {}".format(commands['scene'][i],commands['duration'][i]))
			await asyncio.sleep(commands['duration'][i]) 
			ws.call(requests.SetCurrentTransition(commands['transition'][i]))
			ws.call(requests.SetCurrentScene(commands['scene'][i]))
		global event
		if event.is_set():
			break

	

@app.route("/", methods=["GET"])
def home():
	if connected:
		scns = ws.call(requests.GetSceneList())
		scenes=[]
		for s in scns.getScenes():
			name = s['name']
			scenes.append(name)
		transitions=[]
		sitions = ws.call(requests.GetTransitionList())
		for t in sitions.getTransitions():
			name = t['name']
			transitions.append(name)

		return render_template("dashboard.html",scenes=scenes, transitions=transitions)
	else:
		return render_template("setup.html")
		
	

@app.route("/setup", methods=["POST"])
def setup():
	host=request.form['host']
	port=request.form['port']
	secret=request.form['secret']
	save=request.form['save']
	if save=='True':
		file = open("config.py", "w")
		file.write("host = '"+host+"'\n")
		file.write("port = '"+port+"'\n")
		file.write("secret = '"+secret+"'\n")
		file.close()
	ws = obsws(host, port, secret)
	ws.connect()
	
	return render_template("dashboard.html")

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
	if request.method=="GET":
		scns = ws.call(requests.GetSceneList())
		transitions = ws.call(requests.GetTransitionList())
		for s in scns.getScenes():
			name = s['name']
			scenes.append(name)
		return render_template("dashboard.html",scenes=scenes, transitions=transitions)
	if request.method=="POST":
		
		items=request.form.items(multi=True)

		print(items)
		with open('saved.csv', 'w', encoding='UTF8') as f:
			writer = csv.writer(f)
			header = ['scene', 'transition', 'duration']
			writer.writerow(header)
			i=1
			row=[]
			for item in items:
				if i%2!=0:
					row.append(item[0].removesuffix('_transition'))
					row.append(item[1])
					i=i+1
				else:
					row.append(item[1])
					writer.writerow(row)
					row=[]
					i=i+1
		df = pandas.read_csv('saved.csv')
		global thr
		global _thread
		global event
		if thr==1:
			event.set()
			_thread.join()
			_thread = threading.Thread(target=asyncio.run, args=(tasks(df),))
			_thread.start()
		else:
			event = Event()
			_thread = threading.Thread(target=asyncio.run, args=(tasks(df),))
			_thread.start()
		thr=1

		scns = ws.call(requests.GetSceneList())
		scenes=[]
		for s in scns.getScenes():
			name = s['name']
			scenes.append(name)
		transitions=[]
		sitions = ws.call(requests.GetTransitionList())
		for t in sitions.getTransitions():
			name = t['name']
			transitions.append(name)
		return render_template("dashboard.html",scenes=scenes, transitions=transitions, flow=df)

	
# try:
# 	scenes = ws.call(requests.GetSceneList())
# 	transitions = ws.call(requests.GetTransitionList())
# 	ws.call(requests.SetCurrentTransition("Fade"))
# 	print(transitions)
# 	for s in scenes.getScenes():
# 		name = s['name']
# 		print(u"Switching to {}".format(name))
# 		ws.call(requests.SetCurrentScene(name))
# 		time.sleep(5) 
# 	print("End of list")

# except KeyboardInterrupt:
# 	pass

app.app_context().push()
if __name__ == '__main__':
	file_exists = exists("config.py")
	
	if file_exists:
		import config
		host = config.host
		port= config.port
		secret = config.secret
		print("connecting")
		global connected
		connected=True
		ws = obsws(host, port, secret)
		ws.connect()
	else:
		connected=False
	app.run(host='0.0.0.0',port=8080, debug=True)
	