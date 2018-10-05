# -*- coding: utf-8 -*-
from flask import Flask
from flask import abort, redirect, url_for, request
from flask import render_template
from flask import send_file
import json
import pymongo
from pymongo import MongoClient
import os
import sys
import codecs
from io import BytesIO

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(APP_ROOT, 'services'))
from MongoDBService import MongoDBService
from UserService import UserService
from FileService import FileService
from ApplicationService import ApplicationService
from ConfigReader import ConfigReader
configReader = ConfigReader()

# static pages
@app.route('/')
def root_page():
    return render_template('home.html')

# @app.route('/<string:page_name>/')
# def static_page(page_name):
#     return render_template('%s.html' % page_name)

@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

@app.route('/post/<int:post_id>')  #float also works
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id

#get parameters from form.
#http://localhost:5000/submitForm
@app.route('/submitForm', methods=['POST', 'GET'])
def submitForm():
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'No username found!'
            return error
        else:
            return request.form['username']
    else:
        return 'this is from GET method'

#upload file
@app.route('/uploadFile', methods=['POST','GET'])
def upload_file():
    targetFolder = os.path.join(APP_ROOT, 'uploadedFiles')

    if not os.path.isdir(targetFolder):
        os.mkdir(targetFolder)

    if request.method == 'POST':
        myfile = request.files['myfile']
        destination = "/".join([targetFolder, myfile.filename])
        myfile.save(destination)
        return redirect(url_for('upload_file'), 303)
    else:
        return render_template('uploadfile.html')

#get json data
#http://localhost:5000/getJson    playload is a json obj
@app.route('/getJson', methods=['POST'])
def getJson():
    data = request.get_data()
    json_re = json.loads(data)
    print (json_re)
    return 'We got this json data: '+ json.dumps(json_re)

#connect to a database
@app.route('/connectMongo', methods=['GET'])
def connectMongo():
    #mongodb://[username:password@]host1[:port1]
    dbService = MongoDBService(configReader)
    client = dbService.myclient
    print(client.database_names())
    return 'connected and DB names are: ' + ' '.join(client.database_names())


#### user services - start
    #pass data via json payload without encryption over password, just for poc purpose
    #{username:"", password:""}
@app.route('/user/createUser', methods=['POST'])
def createUser():
    data = request.get_data()
    res = UserService(configReader).createUser(data)
    return json.dumps(res), 200, {'ContentType':'application/json'} 

@app.route('/user/updateUser', methods=['PUT','POST'])
def updateUser():
    data = request.get_data()
    res = UserService(configReader).updateUser(data)
    return json.dumps(res), 200, {'ContentType':'application/json'} 

@app.route('/user/deleteUser', methods=['DELETE','POST'])
def deleteUser():
    data = request.get_data()
    res = UserService(configReader).deleteUser(data)
    return json.dumps(res), 200, {'ContentType':'application/json'} 

@app.route('/user/authUser', methods=['POST'])
def authUser():
    data = request.get_data()
    res = UserService(configReader).authUser(data)
    return json.dumps({'isAuthorized}':res}), 200, {'ContentType':'application/json'} 

#### user services - end

#### app services - start
#Json payload must include : appName appDesc username
@app.route('/app/createApp', methods=['POST'])
def createApp():
    data = request.get_data()
    res = ApplicationService(configReader).createApp(data)
    return json.dumps(res), 200, {'ContentType':'application/json'} 

@app.route('/app/updateApp', methods=['PUT','POST'])
def updateApp():
    data = request.get_data()
    res = ApplicationService(configReader).updateApp(data)
    return json.dumps(res), 200, {'ContentType':'application/json'} 

@app.route('/app/deleteApp', methods=['DELETE','POST'])
def deleteApp():
    data = request.get_data()
    res = ApplicationService(configReader).deleteApp(data)
    return json.dumps(res), 200, {'ContentType':'application/json'} 

#{username:"aName"}
@app.route('/app/deleteAllAppForUser', methods=['POST'])
def deleteAllAppForUser():
    data = request.get_data()
    json_re = json.loads(data)
    res = ApplicationService(configReader).deleteAllAppForUser(json_re['username'])
    return json.dumps(res), 200, {'ContentType':'application/json'} 
#### app services - end

#### model/data file services - start

#!!!! this is not json payload, should be a form submit
# fileType: data / model
#file must be from upload form
#folderPath will pass to service from route
@app.route('/file/saveFile', methods=['POST','GET'])
def saveFile():
    if request.method == 'POST':
        userName = request.form['username']
        appName = request.form['appName']
        fileType = request.form['fileType']
        myFile = request.files['myfile']
        fileName = myFile.filename
        isUsingCloud = request.form['isUsingCloud']
        res = FileService(configReader).saveFile(userName, appName, fileType, fileName, myFile, APP_ROOT, isUsingCloud)
        return redirect(url_for('saveFile'), 303)
    else:
        return render_template('savefile.html')

#Json payload must include : username appName fileType fileName isUsingCloud
@app.route('/file/delFile', methods=['DELETE','POST'])
def delFile():
    data = request.get_data()
    json_re = json.loads(data)
    res = FileService(configReader).delFile(json_re['username'], json_re['appName'], json_re['fileType'],json_re['fileName'], APP_ROOT, json_re['isUsingCloud'])
    return json.dumps(res), 200, {'ContentType':'application/json'} 

#Json payload must include : username appName isUsingCloud
@app.route('/file/delAllFileForApp', methods=['DELETE','POST'])
def delAllFileForApp():
    data = request.get_data()
    json_re = json.loads(data)
    res = FileService(configReader).delAllFileForApp(json_re['username'], json_re['appName'], APP_ROOT, json_re['isUsingCloud'])
    return json.dumps(res), 200, {'ContentType':'application/json'} 

#Json payload must include : username appName fileType fileName isUsingCloud
@app.route('/file/getFile', methods=['POST'])
def getFile():
    ##!!!!!! to be rewritten, how would it be called?
    data = request.get_data()
    json_re = json.loads(data)
    res = FileService(configReader).getFile(json_re['username'], json_re['appName'], json_re['fileType'],json_re['fileName'], APP_ROOT, json_re['isUsingCloud'])
    return send_file(res, as_attachment=True, attachment_filename=json_re['fileName'])

#Json payload must include : username appName
@app.route('/file/getFileList', methods=['POST'])
def getFileList():
    data = request.get_data()
    json_re = json.loads(data)
    res = FileService(configReader).getFileList(json_re['username'], json_re['appName'])
    return res, 200, {'ContentType':'application/json'} 

#### model/data file services - end

#### machine learning services - start

#### machine learning services - end

if __name__ == '__main__':
    #app.run()
    app.run(host='0.0.0.0',port=configReader.port)