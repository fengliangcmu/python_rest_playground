import configparser
import json
import io
import boto3
import botocore

class S3Service:

    def __init__(self, configReader):
        self.configReader = configReader
        self.s3 = boto3.client('s3',
                                   aws_access_key_id=configReader.s3_access_key_id,
                                   aws_secret_access_key=configReader.s3_secret_access_key,
                                   region_name=configReader.s3_region)

    def __str__(self):
        return 'S3Service'

    def uploadFile(self, file_path, bucketName, fileNameAsKey):
        try:
            self.s3.upload_file(file_path, bucketName,fileNameAsKey)
        except botocore.exceptions.ClientError as e:
            print('Client Exception: %s'%e)
            raise

    def uploadFileObj(self,binaryData, bucketName, fileNameAsKey):
        try:
            self.s3.put_object(Body=binaryData.getvalue(), Bucket=bucketName, Key=fileNameAsKey)
        except botocore.exceptions.ClientError as e:
            print('Client Exception: %s'%e)
            raise

    def downloadFileObj(self,bucketName, fileNameAsKey):
        buffer = io.BytesIO()
        try:
            self.s3.download_fileobj(bucketName, fileNameAsKey, buffer)
            buffer.seek(0)
            return buffer
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object (%s) does not exist."%fileNameAsKey)
                raise

    def downloadFile(self,bucketName, fileNameAsKey, fileName):
        try:
            self.s3.Bucket(bucketName).download_file(fileNameAsKey, fileName)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object (%s) does not exist."%key)
                raise

    def deleteFile(self, bucketName, fileNameAsKey):
        try:
            self.s3.delete_objects(Bucket=bucketName, Delete={'Objects': [{'Key': fileNameAsKey}]})
        except botocore.exceptions.ClientError as e:
            print('Client Exception: %s'%e)
            raise
      
    def deleteAllFilesForApp(self, bucketName, objectsArray):
        try:
            self.s3.delete_objects(Bucket=bucketName, Delete={'Objects': objectsArray})
        except botocore.exceptions.ClientError as e:
            print('Client Exception: %s'%e)
            raise

    def listFilesInBucket(self, bucketName):
        try:
            my_objs = self.s3.list_objects(Bucket=bucketName)
            #mybucket.objects.filter(Prefix='foo/bar')
            for object in my_objs['Contents']:
                print(object)
        except botocore.exceptions.ClientError as e:
            print('Client Exception: %s'%e)
            raise