from loguru import logger
import os
import configparser
from sdk.contracts.logging import Logging

config = configparser.ConfigParser()

def _get_log_level(level:str):
    
    if (level.lower() == 'trace'):
        return "TRACE"

    if (level.lower() == 'debug'):
        return "DEBUG"
    
    if (level.lower() == 'info'):
        return "INFO"
    
    if (level.lower() == 'warn'):
        return "WARNING"
    
    if (level.lower() == 'error'):
        return "ERROR"
    
    if (level.lower() == 'critical'):
        return "CRITICAL"
    
    raise ValueError('Unknown log level specified in configuration')

class Logger:
    _logger_instance = None

    @staticmethod
    def get_instance():
        if Logger._logger_instance is None:
            Logger._logger_instance = Logger._setup_logger()
        return Logger._logger_instance

    @staticmethod
    def _setup_logger():
        try:
            config.read('config.ini')

            log_level = _get_log_level(config['logging']['level']) 
            log_filename =  config['logging']['file_name']
            log_file_path = config['logging']['path']
            max_file_size_mb = config.getint('logging','max_file_size_in_mb')
            max_number_of_files = config.getint('logging','max_number_of_files')
            config_format = config['logging']['log_format']

            os.makedirs(log_file_path, exist_ok=True)

            log_format:str = None

            if (config_format == None or config_format == ""):
                log_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {module}.{function}:{line} - {message}"
            else:
                log_format = config_format        

            logger.add(
                f"{log_file_path}/{log_filename}",
                level=log_level,
                rotation=f"{max_file_size_mb} MB",
                retention=max_number_of_files,
                enqueue=True,  # Safe in multi-threaded apps
                backtrace=True,
                compression="zip",  # Compress old log files
                format=log_format
            )

            return logger

        except Exception as ex:
            print(f"Oops! {ex.__class__} occurred. Unable to initialize the logger. Details: {ex}")
            raise