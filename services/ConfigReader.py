import configparser
import os

class ConfigReader:

    def __init__(self):
        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini'))
        self.cfg = cfg
        self.port = cfg['server']['port']
        self.connectionUrl = cfg['database']['connectionUrl']
        self.databaseName = cfg['database']['databaseName']
        self.collection_userInfo_name = cfg['database']['collection_userInfo_name']
        self.collection_app_name = cfg['database']['collection_app_name']
        self.collection_files_name = cfg['database']['collection_files_name']
        self.data_prefix = cfg['file']['data_file_prefix']
        self.model_prefix = cfg['file']['model_file_prefix']
        self.file_storage_type = cfg['file']['file_storage_type']
        self.localStorageFolder = cfg['file']['localStorageFolder']
        self.s3_bucket = cfg['s3_credentials']['s3_bucket']
        self.s3_access_key_id = cfg['s3_credentials']['s3_access_key_id']
        self.s3_secret_access_key = cfg['s3_credentials']['s3_secret_access_key']
        self.s3_host = cfg['s3_credentials']['s3_host']
        self.s3_uri = cfg['s3_credentials']['s3_uri']
        self.s3_region = cfg['s3_credentials']['s3_region']
        self.s3_username = cfg['s3_credentials']['s3_username']

    def __str__(self):
        return 'UserService'