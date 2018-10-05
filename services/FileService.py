import pymongo
import configparser
import datetime
from MongoDBService import MongoDBService
from S3Service import S3Service
import os
import io
import shutil
import json
# from bson.json_util import dumps
# from bson import json_util

class FileService:

    def __init__(self, configReader):
        self.configReader = configReader

    def __str__(self):
        return 'FileService'
        # update password

    def saveFile(self, userName, appName, fileType, fileName, myfile, folderPath, isUsingCloud):
        json_re = {"username": userName, "appName": appName,
                   "fileType": fileType, "fileName": fileName,
                   "isUsingCloud": isUsingCloud}
        client = MongoDBService(self.configReader)
        mydb = client.getDB()
        mycollection = mydb[self.configReader.collection_files_name]
        if client.isExisting(json_re, self.configReader.collection_files_name):
            # update
            myquery = {"username": userName, "appName": appName,
                       "fileType": fileType, "fileName": fileName,
                       "isUsingCloud": isUsingCloud}
            json_re['updatedAt'] = datetime.datetime.utcnow()
            newvalues = {"$set": json_re}
            mycollection.update_one(myquery, newvalues)
        else:
            # save
            time = datetime.datetime.utcnow()
            json_re['createdAt'] = time
            json_re['updatedAt'] = time
            mycollection.insert_one(json_re)

        #previous insertion op should be in the same transaction with following file op
        if self.str2bool(isUsingCloud):
            self.saveToCloud(userName, appName, fileType, fileName, myfile)
        else:
            self.saveToLocal(userName, appName, fileType,fileName, myfile, folderPath)

        return {'success': True, 'message': 'New File Created!'}

    def delFile(self, userName, appName, fileType, fileName, folderPath, isUsingCloud):

        if self.str2bool(isUsingCloud):
            self.delFromCloud(userName, appName, fileType, fileName)
        else:
            self.delFromLocal(userName, appName, fileType,fileName, folderPath)

        json_re = {"username": userName, "appName": appName,
                   "fileType": fileType, "fileName": fileName}
        mydb = MongoDBService(self.configReader).getDB()
        mycollection = mydb[self.configReader.collection_files_name]
        mycollection.delete_one(json_re)

        return {'success': True, 'message': 'File Deleted!'}

    def delAllFileForApp(self, userName, appName, folderPath, isUsingCloud):

        if self.str2bool(isUsingCloud):
            self.delAllCloudFilesForApp(userName, appName)
        else:
            self.delAllLocalFilesForApp(userName, appName, folderPath)

        json_re = {"username": userName, "appName": appName}
        mydb = MongoDBService(self.configReader).getDB()
        mycollection = mydb[self.configReader.collection_files_name]
        mycollection.delete_many(json_re)
        return {'success': True, 'message': 'Files Deleted for: ' + userName + ' , appName: ' + appName}

    def getFile(self, userName, appName, fileType, fileName, folderPath, isUsingCloud):
        # following may not need
        # json_re = {"username":userName, "appName":appName, "fileType":fileType, "fileName":fileName}
        # mydb = MongoDBService(self.configReader).getDB()
        # mycollection = mydb[self.configReader.collection_files_name]
        # res= mycollection.find_one(json_re)
        if self.str2bool(isUsingCloud):
            return self.getCloudFile(userName, appName, fileType, fileName)
        else:
            return self.getLocalFile(userName, appName, fileType,fileName, folderPath)

    def getFileList(self, userName, appName):
        json_re = {"username": userName, "appName": appName}
        mydb = MongoDBService(self.configReader).getDB()
        mycollection = mydb[self.configReader.collection_files_name]
        res = mycollection.find(json_re)
        docs = []
        for doc in res:
            doc.pop('_id')
            docs.append(doc)
        return json.dumps(docs,default=self.default)

    # file with same name will be replaced
    def saveToLocal(self, userName, appName, fileType, fileName, myfile, folderPath):
        if not os.path.isdir(folderPath):
            os.mkdir(folderPath)
        uploadFolder = os.path.join(folderPath, self.configReader.localStorageFolder)
        if not os.path.isdir(uploadFolder):
            os.mkdir(uploadFolder)
        userFolder = os.path.join(uploadFolder, userName)
        if not os.path.isdir(userFolder):
            os.mkdir(userFolder)
        appFolder = os.path.join(userFolder, appName)
        if not os.path.isdir(appFolder):
            os.mkdir(appFolder)
        typeFolder = os.path.join(appFolder, fileType)
        if not os.path.isdir(typeFolder):
            os.mkdir(typeFolder)
        destination = "/".join([typeFolder, fileName])
        myfile.save(destination)
        return {'success':True, 'message':'File Saved To Local Folder!'}

    def delFromLocal(self, userName, appName, fileType, fileName, folderPath):
        fileToDel = self.buildFilePath(userName, appName, fileType, fileName, folderPath)
        if os.path.isfile(fileToDel):
            os.remove(fileToDel)
        return {'success':True, 'message':'Local File Deleted: ' + fileName}

    def delAllLocalFilesForApp(self, userName, appName, folderPath):
        uploadFolder = os.path.join(folderPath, self.configReader.localStorageFolder)
        userFolder = os.path.join(uploadFolder, userName)
        appFolder = os.path.join(userFolder, appName)
        if os.path.isdir(appFolder):
            shutil.rmtree(appFolder)
        return {'success':True, 'message':'All Local Files Deleted for App:  ' + appName}
    # probably we can only return the file path?
    def getLocalFile(self, userName, appName, fileType, fileName, folderPath):
        fileToGet = self.buildFilePath(userName, appName, fileType, fileName, folderPath)
        fileInMem = None
        if os.path.isfile(fileToGet):
            with open(fileToGet, 'rb') as fin:
                fileInMem = io.BytesIO(fin.read())
                fileInMem.seek(0)
                #return in memory binary data
        return fileInMem

    def saveToCloud(self, userName, appName, fileType, fileName, file):
        fileNameAsKey = self.buildS3Prefix(userName, appName, fileType, fileName)
        bucketName = self.configReader.s3_bucket
        S3Service(self.configReader).uploadFileObj(file, bucketName, fileNameAsKey)
        return {'success':True, 'message':'File Saved To Cloud Folder!'}

    def delFromCloud(self, userName, appName, fileType, fileName):
        fileNameAsKey = self.buildS3Prefix(userName, appName, fileType, fileName)
        bucketName = self.configReader.s3_bucket
        S3Service(self.configReader).deleteFile(bucketName, fileNameAsKey)
        return {'success':True, 'message':'File Deleted From Cloud Folder!'}

    def delAllCloudFilesForApp(self, userName, appName):
        listFromMongo = self.getFileList(userName,appName)
        fileList = json.loads(listFromMongo)
        objectsArray = []
        bucketName = self.configReader.s3_bucket
        for ele in fileList:
            #buildS3Prefix(self, userName, appName, fileType, fileName):
            temp_key = self.buildS3Prefix(ele['username'], ele['appName'], ele['fileType'], ele['fileName'])
            objectsArray.append({'Key': temp_key})
        if len(fileList) > 0:
            S3Service(self.configReader).deleteAllFilesForApp(bucketName, objectsArray)
            return {'success':True, 'message':'Files Deleted For User ${userName} App ${appName}!'}
        else:
            return {'success':True, 'message':'No Files Deleted For User ${userName} App ${appName}!'}

    def getCloudFile(self, userName, appName, fileType, fileName):
        fileNameAsKey = self.buildS3Prefix(userName, appName, fileType, fileName)
        bucketName = self.configReader.s3_bucket
        res = S3Service(self.configReader).downloadFileObj(bucketName, fileNameAsKey)
        return res

    def buildFilePath(self, userName, appName, fileType, fileName, folderPath):
        uploadFolder = os.path.join(folderPath, self.configReader.localStorageFolder)
        userFolder = os.path.join(uploadFolder, userName)
        appFolder = os.path.join(userName, appName)
        typeFolder = os.path.join(appFolder, fileType)
        fileToReturn = os.path.join(typeFolder, fileName)
        return fileToReturn

    def buildS3Prefix(self, userName, appName, fileType, fileName):
        appFolder = os.path.join(userName, appName)
        typeFolder = os.path.join(appFolder, fileType)
        fileToReturn = os.path.join(typeFolder, fileName)
        return fileToReturn

    def str2bool(self, v):
        return v.lower() in ("yes", "true", "t", "1")

    def default(self, o):
        if type(o) is datetime.date or type(o) is datetime.datetime:
            return o.isoformat()
