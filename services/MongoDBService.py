import pymongo
import configparser
from pymongo.errors import ServerSelectionTimeoutError
import json

class MongoDBService:

    def __init__(self, configReader):
        self.configReader = configReader
        self.myclient = pymongo.MongoClient(configReader.connectionUrl)
        self.mydb = self.myclient[configReader.databaseName]

    def __str__(self):
        return 'MongoDBService'

    def getDB(self):
        try:
            info =  self.myclient.server_info() # Forces a call.
            return self.myclient[self.configReader.databaseName]
        except ServerSelectionTimeoutError:
            self.myclient = pymongo.MongoClient(self.configReader.connectionUrl)
            self.mydb = self.myclient[self.configReader.databaseName]
    
    def closeDb(self):
        if self.myclient is not None:
            self.myclient.close()

    def isExisting(self, data, collectionName):
        res = self.mydb[collectionName].find_one(data)
        if res is None:
            return False
        else:
            return True

