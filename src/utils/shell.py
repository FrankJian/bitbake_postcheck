#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on Dec 8, 2016

@author: xiaopan
'''
import subprocess

from utils.log import Log


class Shell(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.logger = Log().getLogger("Shell")
        
    def execute(self, command, output=False, errorOuput=False): 
        result = subprocess.getstatusoutput(command)
        if result[0] == 0 :
            if output:
                self.logger.info("Execute command: " + command)
                self.logger.info(result[1])
            return result[1]
        else:
            self.logger.info("Execute command: " + command)
            self.logger.warning("Command execute failed: " + result[1])
            if errorOuput:
                return result
            else:
                return False    
