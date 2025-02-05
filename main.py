
from sdk.logger import Logger
from src.file_processor import FileProcessor
from src.remote_file_manager import RemoteFileManager
import configparser

logger = Logger.get_instance()
config = configparser.ConfigParser()

def initialize():
    config.read('config.ini')
    logger.info(f'Started the SFTP sync application. Debug: [{config['settings']['debug']}]')

def process_all_files():
    local_folder_path = config['settings']['local_folder_path']
    skip_folders = config['settings']['skip_folders']
    remote_address = config['sftp']['remote_address']
    sftp_user = config['sftp']['username']
    sftp_pass = config['sftp']['password']

    remote_manager = RemoteFileManager(remote_address, sftp_user, sftp_pass)
    file_processor = FileProcessor(remote_manager, skip_folders)
    file_processor.process_files(local_folder_path)

initialize()
process_all_files()
