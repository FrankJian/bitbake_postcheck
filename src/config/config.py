'''
Created on Dec 8, 2016

@author: xiaopan
'''
import os
import re


class BitbakePostCheckConfig(object):
    '''
    classdocs
    '''


    def __init__(self, baseline):
        '''
        Constructor
        '''
        self.baseline = baseline.strip()
        svn_default_server = "https://beisop60.china.nsn-net.net"
        try:
            self.svn_server = os.environ["SVN_SERVER"]
        except KeyError:
            self.svn_server = svn_default_server
            
        self.default_configs = {"mail_from":"tdlte-sw-build-team@mlist.emea.nsn-intra.net",
                                "mail_to":"tdlte-sw-build-team@mlist.emea.nsn-intra.net",
                                "mail_subject":"[ Bitbake Warning ] bitbake for {} is abnormal, please check".format(self.baseline),
                                "ignoreSC":"CB_BB_PATTERN,CB_BB_SCRIPTS,TLDA",
                                "svnServer":self.svn_server
                                }
        
        
    def configs(self):
        configs = {"FSMr3":{"repo":self.svn_server + "/isource/svnroot/tdlte_cb_scm/TD_LTE/frozen/TDD_FSMR3/",
                            "defaultPatternRepo":self.svn_server + "/isource/svnroot/BTS_SCM_LTE_BBMETA/pattern/trunk",
                            "defaultBbScriptRepo":self.svn_server + "/isource/svnroot/BTS_SCM_LTE_BBMETA/scripts/trunk",
                            "bitbakePath":"/lteRel/bitbake",
                            "productId":"TDD",
                            "module":"FSM-r3",
                            "bitbakeContentCheck":False,
                            "packagePath":"/lteStorage/FSMr3_trunk_package/{}/TL00".format(self.baseline)},
                   "FSMr4":{"repo":self.svn_server + "/isource/svnroot/BTS_SCM_LTE_CB_CI/frozen/TDD_FSMR4/",
                            "defaultPatternRepo":self.svn_server + "/isource/svnroot/BTS_SCM_LTE_BBMETA/pattern/trunk",
                            "defaultBbScriptRepo":self.svn_server + "/isource/svnroot/BTS_SCM_LTE_BBMETA/scripts/trunk",
                            "bitbakePath":"/lteRel/bitbake",
                            "productId":"TDD",
                            "module":"FSM-r4",
                            "bitbakeContentCheck":False,
                            "packagePath":"/lteStorage/FSMr4_trunk_package/{}/lteDeliveries/build/TL00".format(self.baseline)},
                   "TL16A":{"repo":self.svn_server + "/isource/svnroot/BTS_SCM_LTE/builds/tags/",
                            "defaultPatternRepo":self.svn_server + "/isource/svnroot/BTS_SCM_LTE_BBMETA/pattern/branches/maintenance/TL16A",
                            "defaultBbScriptRepo":self.svn_server + "/isource/svnroot/BTS_SCM_LTE_BBMETA/scripts/trunk",
                            "bitbakePath":"/lteRel/bitbake",
                            "productId":"TDD",
                            "module":"FSMr3AirScale",
                            "bitbakeContentCheck":True,
                            "packagePath":"/mnt/TDD_release/Official_Build/{}".format(self.baseline)},
                   "TL17":{"repo":self.svn_server + "/isource/svnroot/BTS_SCM_LTE/builds/tags/",
                           "defaultPatternRepo":self.svn_server + "/isource/svnroot/BTS_SCM_LTE_BBMETA/pattern/branches/maintenance/FL17",
                           "defaultBbScriptRepo":self.svn_server + "/isource/svnroot/BTS_SCM_LTE_BBMETA/scripts/trunk",
                           "bitbakePath":"/lteRel/bitbake",
                           "productId":"TDD",
                           "module":"FSMr3AirScale",
                           "bitbakeContentCheck":True,
                           "packagePath":"/TDD_Storage/Official_Build2/{}".format(self.baseline)}}
        return configs
    
    def get_regexps(self):
        regexps = {
                "TL00_ENB_9999_.*":"FSMr3",
                "TL00_FSM4_9999_.*":"FSMr4",
                "TL16A_ENB_0000_.*":"TL16A",
                "TL17_ENB_0000_.*":"TL17"}
        return regexps
    def get_branch(self):
        regexps = self.get_regexps()
        found = False
        for regexp in regexps:
            baseline_regex = re.compile(regexp)
            match = baseline_regex.match(self.baseline)
            if match:
                found = True
                return regexps.get(regexp)
        if not found:
            raise Exception("There is no matched branch name, please check the configuration")
        
    def get_configs(self):
        
        branch = self.get_branch()
        configs = self.configs()
        for config in configs:
            if config == branch:
                return dict(configs.get(config), **self.default_configs)
        else:
            raise Exception("Configs not found for baseline " + self.baseline)
        
