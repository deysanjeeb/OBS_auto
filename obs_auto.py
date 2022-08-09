import sys 
import time
from os.path import exists
from obswebsocket import obsws, events, requests
import PySimpleGUI as sg
import json, sys, os, time, csv
from flask import Flask,request
from flask import render_template
from flask import current_app as app


app = Flask(__name__)
app.app_context().push()

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
		for item in items:
			print(item)
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
	app.run(host='localhost',port=8080, debug=True)
	