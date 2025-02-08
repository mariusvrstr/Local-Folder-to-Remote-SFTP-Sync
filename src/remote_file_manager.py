import paramiko
import os

from sdk.logger import Logger
from typing import List, Optional

logger = Logger.get_instance()

class RemoteFileManager:
    def __init__(self, host_address, username, password):
        self.host_address = host_address
        self.username = username
        self.password = password
        self.sftp = None
        self.client = None

        self.connect()

    def connect(self) -> bool:
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.host_address, username=self.username, password=self.password)
            self.sftp = self.client.open_sftp()
            logger.info(f'Connection established to [{self.host_address}]')

        except Exception as e:
            logger.error(f"Failed to connect to {self.host_address}: {e}")
            raise
    
    def ensure_remote_directory_exists(self, sftp, remote_directory):
        if remote_directory in ("", "/"):
            return

        try:
            sftp.stat(remote_directory)  # Check if directory exists
        except IOError:
            # The directory does not exist, so first ensure the parent exists
            parent_dir = os.path.dirname(remote_directory)
            self.ensure_remote_directory_exists(sftp, parent_dir)

            # Now create the current directory
            sftp.mkdir(remote_directory)


    def get_file_size_if_exist(self, file_path):
        try:
            file_info = self.sftp.stat(file_path)
            return file_info.st_size / 1024  # Convert size in bytes to kilobytes
        except FileNotFoundError:
            return None
        
    def remove_file(self, file_path):
        try:
            self.sftp.remove(file_path)
            logger.info(f"File {file_path} successfully removed to be replaced.")
        except Exception as e:
            logger.error(f"Failed to remove file: {e}")

    def transfer_file(self, local_file_path, remote_file_path):
        try:
            remote_dir = os.path.dirname(remote_file_path)
            self.ensure_remote_directory_exists(self.sftp, remote_dir)
            self.sftp.put(local_file_path, remote_file_path)
            logger.info(f"File {local_file_path} successfully transferred to {remote_file_path}")

        except Exception as e:
            logger.error(f"Failed to transfer file: {e}")

    def __del__(self):
        if self.sftp:
            self.sftp.close()
        if self.client:
            self.client.close()
            
        if logger:
            logger.info("Connection closed.")