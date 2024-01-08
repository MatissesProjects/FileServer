import logging
from utils.path_manager import get_path

def setup_logger():
    logging.basicConfig(
        filename=get_path('fileserver.log', 'logs/'),
        format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s',
        level=logging.INFO,
        encoding='utf-8'
    )

def get_logger():
    setup_logger()
    return logging.getLogger(__name__)