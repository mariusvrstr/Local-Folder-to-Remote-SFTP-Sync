
import os
import time
from sdk.logger import Logger
from typing import List, Optional

logger = Logger.get_instance()


class FileProcessor:    
    exluded_folders:List[str] = []
    succeeded_files:List[str] = []
    failed_files:List[str] = []
    skipped_files:List[str] = []

    def __init__(self, folder_exclusions=None):
        self.exluded_folders = [folder.strip() for folder in folder_exclusions.split(',')]

    def process_files(self, local_folder_path:str):
        file_counter = 0
        logger.info(f'Starting to process files in [{local_folder_path}]...')

        # Connect to SFTP
         
        for root, dirs, files in os.walk(local_folder_path):
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

    
    def process_file(self, file_path:str) -> Optional[bool] :

        try:
            logger.info(f'Beginning to process file [{file_path}]')

            if (not self.can_process_file(file_path)):
                return False
            
            # Does it exist in the destination? Then return True
            # Get the relative path
            # Copy to the remote destination
            # Move to archive
            
            return True
        
        except Exception as ex:        
            logger.error(f"Failed to move file [{file_path}]: {ex}")
            return False

            


        