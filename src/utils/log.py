'''
Created on Dec 9, 2016

@author: xiaopan
'''
import logging


class Log(object):
    '''
    classdocs
    '''

    def getLogger(self, name, file=""):    
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        self.add_stream_handler(logger)
        if file != "":
            self.add_file_handler(logger, file)
       
        return logger
    
    def add_stream_handler(self, logger):
        is_added = False
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                is_added = True
                
        if not is_added:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
    def add_file_handler(self, logger, file):
        is_added = False
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                is_added = True
                
        if not is_added:
            console_handler = logging.FileHandler(file)
            console_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler) 
