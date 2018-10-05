import datetime
import pymongo
import json
from MongoDBService import MongoDBService

class UserService:

    def __init__(self, configReader):
        self.configReader = configReader

    def __str__(self):
        return 'UserService'

    #update password
    def updateUser(self, userData):
        json_re = json.loads(userData)
        mydb = MongoDBService(self.configReader).getDB()
        mycollection = mydb[self.configReader.collection_userInfo_name]
        myquery = { "username": json_re['username'] }
        json_re['updatedAt'] = datetime.datetime.utcnow()
        newvalues = { "$set": json_re }
        mycollection.update_one(myquery, newvalues)
        return {'success':True, 'message':'User Updated!'}

    def deleteUser(self, userData):
        json_re = json.loads(userData)
        mydb = MongoDBService(self.configReader).getDB()
        mycollection = mydb[self.configReader.collection_userInfo_name]
        mycollection.delete_one(json_re)
        return {'success':True, 'message':'User Deleted!'}
    
    def createUser(self, userData):
        json_re = json.loads(userData)
        client = MongoDBService(self.configReader)
        if client.isExisting({ "username": json_re['username'] }, self.configReader.collection_userInfo_name):
            return {'success':False, 'message':'User Already Exists!'}
        mydb = client.getDB()
        mycollection = mydb[self.configReader.collection_userInfo_name]
        time = datetime.datetime.utcnow()
        json_re['createdAt'] = time
        json_re['updatedAt'] = time
        mycollection.insert_one(json_re)
        return {'success':True, 'message':'New User Created!'}
    
    def authUser(self, userData):
        json_re = json.loads(userData)
        mydb = MongoDBService(self.configReader).getDB()
        mycollection = mydb[self.configReader.collection_userInfo_name]
        res= mycollection.find_one(json_re)
        if res is None:
            return False
        else:
            return True

    def delAllForUser(self, userData):
        return