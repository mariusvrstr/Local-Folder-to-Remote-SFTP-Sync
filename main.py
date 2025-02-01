
from sdk.logger import Logger

logger = Logger.get_instance()

def initialize():
    logger.info(f'Started the SFTP sync application.')



initialize()