import datetime
import pymongo
import configparser
import json
from MongoDBService import MongoDBService


class ApplicationService:

    def __init__(self, configReader):
        self.configReader = configReader

    def __str__(self):
        return 'ApplicationService'

    def updateApp(self, appData):
        json_re = json.loads(appData)
        mydb = MongoDBService(self.configReader).getDB()
        mycollection = mydb[self.configReader.collection_app_name]
        myquery = {"username": json_re['username'],
                   "appName": json_re['appName']}
        json_re['updatedAt'] = datetime.datetime.utcnow()
        newvalues = {"$set": json_re}
        mycollection.update_one(myquery, newvalues)
        return {'success': True, 'message': 'Application Updated!'}

    def deleteApp(self, appData):
        json_re = json.loads(appData)
        mydb = MongoDBService(self.configReader).getDB()
        mycollection = mydb[self.configReader.collection_app_name]
        mycollection.delete_one(json_re)
        # need to delete all files as well? Or just leave the files alone
        return {'success': True, 'message': 'Application Deleted!'}

    # appName appDesc username createdAt updatedAt
    def createApp(self, appData):
        json_re = json.loads(appData)
        if json_re['appName'] is None or json_re['username'] is None:
            return {'success': False, 'message': 'Application Name Should Not Be Empty!'}
        client = MongoDBService(self.configReader)
        if client.isExisting({ "username": json_re['username'],"appName": json_re['appName']}, self.configReader.collection_app_name):
            return {'success': False, 'message': 'Application Name Already Exists!'}
        mydb = client.getDB()
        mycollection = mydb[self.configReader.collection_app_name]
        time = datetime.datetime.utcnow()
        json_re['createdAt'] = time
        json_re['updatedAt'] = time
        mycollection.insert_one(json_re)
        return {'success': True, 'message': 'New Application Created!'}

    def deleteAllAppForUser(self, username):
        mydb = MongoDBService(self.configReader).getDB()
        mycollection = mydb[self.configReader.collection_app_name]
        myquery = { "username": username }
        mycollection.delete_many(myquery)
        # need to delete all files as well? Or just leave the files alone
        return {'success': True, 'message': 'All Applications Deleted For User: ' + username}
