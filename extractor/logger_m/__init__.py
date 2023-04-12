import os
import logging

from datetime import datetime
from logging.handlers import RotatingFileHandler

PATH = os.path.abspath(os.path.dirname(__file__))

class Logger:
    def __init__(self, path: str = ''):
        if not path:
            import os
            path = os.path.abspath(os.path.dirname(__file__))

        current_time = datetime.now()
        formatted_current_time = datetime.strftime(current_time, '%d_%m-%H_%M')

        logging_handler = RotatingFileHandler(f'{path}/{formatted_current_time}.log',
                                             maxBytes=1000000,
                                             backupCount=0,
                                             encoding='utf-8')

        logging.basicConfig(handlers=[logging_handler],
                            format='%(asctime)s __%(levelname)s__ __%(name)s__ %(message)s',
                            datefmt='%m-%d-%Y %H:%M:%S',
                            level=logging.INFO)


    def get_logger(self, name: str = ''):
        return logging.getLogger(name)

logger_obj = Logger(f'{PATH}/logs')

logger_inst = logger_obj.get_logger()
