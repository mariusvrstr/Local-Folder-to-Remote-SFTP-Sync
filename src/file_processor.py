
import os
import time
import shutil

from datetime import datetime
from sdk.logger import Logger
from src.remote_file_manager import RemoteFileManager
from typing import List, Optional

logger = Logger.get_instance()

class FileProcessor:    
    exluded_folders:List[str] = []
    succeeded_files:List[str] = []
    failed_files:List[str] = []
    skipped_files:List[str] = []
    remote_manager:RemoteFileManager = None
    local_folder_path:str = None

    def __init__(self, remote_manager:RemoteFileManager, folder_exclusions=None):
        self.exluded_folders = [folder.strip() for folder in folder_exclusions.split(',')]
        self.remote_manager = remote_manager

    def process_files(self, local_folder_path:str):
        file_counter = 0
        self.local_folder_path = local_folder_path
        logger.info(f'Starting to process files in [{self.local_folder_path}]...')
        
        for root, dirs, files in os.walk(self.local_folder_path):
            dirs[:] = [d for d in dirs if d not in self.exluded_folders]

            for file in files:
                file_counter += 1
                file_path = os.path.join(root, file)
                outcome = self.process_file(file_path)

                if (outcome):
                    self.succeeded_files.append(file)
                else:
                    self.failed_files.append(file)
    
        if (file_counter > 0):
            if (len(self.succeeded_files) > 0):
                logger.info(f'{len(self.succeeded_files)}/{file_counter} Successfull: [{" | ".join(self.succeeded_files)}]')

            if (len(self.failed_files) > 0):
                logger.info(f'{len(self.failed_files)}/{file_counter} Failed: [{" | ".join(self.failed_files)}]')


    def can_process_file(self, file_path:str, check_change_sec=2, checks=5, max_age=600):

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"{file_path} does not exist.")

        stable_count = 0
        tic_count = 0
        prev_size = os.path.getsize(file_path)        
        file_create_time = os.path.getctime(file_path)

        while True:
            tic_count += 1

            if time.time() - file_create_time > max_age:
                return True

            time.sleep(check_change_sec)
            current_size = os.path.getsize(file_path)

            if current_size == prev_size:
                stable_count += 1
            else:
                stable_count = 0
            
            prev_size = current_size
            
            if stable_count >= checks:
                return True
            
            if tic_count > 20:
                return False

    
    def process_file(self, local_file_path:str) -> Optional[bool] :

        try:
            logger.info(f'Beginning to process file [{local_file_path}]')

            remote_file_path = local_file_path.replace(self.local_folder_path, '').replace('\\', '/')

            if (not self.can_process_file(local_file_path)):
                return False
            
            local_file_size = (os.path.getsize(local_file_path) / 1024)
            remote_file_size = self.remote_manager.get_file_size_if_exist(remote_file_path)

            skip = False
            if (remote_file_size is not None and remote_file_size < local_file_size):
                self.remote_manager.remove_file(remote_file_path)
            elif (remote_file_size is not None):
                skip = True    
            
            if (skip):
                logger.info(f'Skipped [{local_file_path}] as file already exists on remote server')
            else:
                self.remote_manager.transfer_file(local_file_path, remote_file_path)

            directory = os.path.dirname(local_file_path)
            archive_dir = os.path.join(directory, 'Archive')

            if not os.path.exists(archive_dir):
                os.makedirs(archive_dir)
                logger.info(f"Created directory: {archive_dir}")

            date_str = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")  # Format: YYYY-MM-DD_H-M-S

            original_filename = os.path.basename(local_file_path)
            new_filename = f"{os.path.splitext(original_filename)[0]}_{date_str}{os.path.splitext(original_filename)[1]}"
            new_file_path = os.path.join(archive_dir, new_filename)

            shutil.move(local_file_path, new_file_path)
            
            return True
        
        except Exception as ex:        
            logger.error(f"Failed to move file [{local_file_path}]: {ex}")
            return False

            


        