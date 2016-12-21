#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on Dec 9, 2016

@author: xiaopan
'''
import logging
from utils.shell import Shell


class SVN(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('SVN')
        self.svn_option = "--no-auth-cache --non-interactive --trust-server-cert"
    
    def cat(self, file, option=""):
        file = self._check_repo(file)
        command = ["svn cat", file, option, self.svn_option]
        result = Shell().execute(" ". join(command))
        return result
    
    def export(self, file, option=""):
        file = self._check_repo(file)
        command = ["svn export", file, option, self.svn_option]
        result = Shell().execute(" ". join(command))
        return result
    
    def externals(self, file, option=""):
        file = self._check_repo(file)
        command = ["svn pg svn:externals", file, option, self.svn_option]
        result = Shell().execute(" ". join(command))
        return result
    
    def checkifexist(self, repo="", option=""):
        """ Method to check whether given repo is a svn repo """
        repo = self._check_repo(repo)
        command = ["svn info", repo, option, self.svn_option]
        if Shell().execute(" ". join(command)):
            return True
        return False
    def _check_repo(self, repo):
        if "@" in repo:
            temp = repo.split("@")
            if "/" in temp[1]:
                revision = temp[1].split("/")[0]
                repo = "{}@{}".format(repo.replace("@{}".format(revision), ""), revision)
        return repo
                
             
            
