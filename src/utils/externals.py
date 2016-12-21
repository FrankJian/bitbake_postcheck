'''
Created on Dec 13, 2016

@author: xiaopan
'''
import re

from config.config import BitbakePostCheckConfig
from utils.svn import SVN


class Externals(object):
    '''
    classdocs
    '''


    def __init__(self, baseline):
        '''
        Constructor
        '''
        config = BitbakePostCheckConfig(baseline).get_configs()
        self.repo = "{}/{}".format(config.get("repo"), baseline)
        self.externals = {}
    
    def parse(self):
        self.read_externals()
        self._parse_externals()
        return self.externals
       
    def read_externals(self):
        self.externals_str_list = SVN().externals(self.repo).splitlines()
    
    def end_of_external_body(self, line):
        return re.match('^$', line)
    
    def head_of_external(self, line):
        return re.search('^#', line)
    
    def cbe_line(self, line):
        return re.search('(?P<branch>.*)@(?P<revision>.*) (?P<fs_path>D_Build(/bin)?)$', line)

    def _parse_externals(self):
        external = None
        for line in self.externals_str_list:
            line = line.rstrip()
            line = re.sub('/$', '', line)
            if self.end_of_external_body(line):
                if external and 'externals' not in self.externals[external]:
                    self.externals[external]['externals'] = []
                external = None
            if external:
                self.parse_external_body(line, external)
            if self.head_of_external(line):
                external = self.parse_head_of_external(line)
            if self.cbe_line(line):
                self.add_cbe(line)
                
    def parse_external_body(self, line, external):

        matched = re.search('^(?P<repo_path>[^@]*)@?(?P<revision>.*) (?P<fs_path>.*)$', line)
        external_entity = {'repo_path':matched.group('repo_path').rstrip('/'), 'fs_path':matched.group('fs_path'), 'revision':matched.group('revision')}
        if 'externals' in self.externals[external]:
            self.externals[external]['externals'].append(external_entity)
        else:
            self.externals[external]['externals'] = [external_entity]
            
    def parse_head_of_external(self, line):
        match = re.search(r'^# for (?P<name>.*) \((?P<branch>[^@]*)@?(?P<revision>.*)\).*$', line)
        if match:
            external = match.group('name')
            parameters = {'name':match.group('name'), 'branch':match.group('branch'), 'revision':match.group('revision')}
            self.externals[external] = parameters
            return external


    def add_cbe(self, line):
        match_cbe = self.cbe_line(line)
        external_cbe = 'SCM'
        parameters = {'name':'SCM', 'branch':match_cbe.group('branch'), 'revision':match_cbe.group('revision')}
        external_entity = {'repo_path':match_cbe.group('branch').rstrip('/'), 'fs_path':match_cbe.group('fs_path'), 'revision':match_cbe.group('revision')}
        self.externals[external_cbe] = parameters
        self.externals[external_cbe]['externals'] = [external_entity]
