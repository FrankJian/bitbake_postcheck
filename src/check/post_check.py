#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on Dec 8, 2016

@author: xiaopan
'''

from _io import StringIO
import os

from check.parse_config import ParseConfig
from utils.log import Log
from utils.mail import Mail
from utils.shell import Shell
from utils.svn import SVN


class BitbakePostCheck(object):
    '''
    classdocs
    '''


    def __init__(self, baseline):
        '''
        Constructor
        '''
        self.logger = Log().getLogger('BitbakePostCheck')
        self.baseline = baseline
        
        
    def check_all_7zfiles_exist(self, target_name):
        
        bitbake_location = self.config.get("bitbakePath")

        bitbake_7zname = self.baseline + "-bs10k-" + target_name + ".7z"
        if not os.path.isfile(os.path.join(bitbake_location, bitbake_7zname)):
            self.logger.error("7z file {} not exist in {}".format(bitbake_7zname, bitbake_location))
            self.mail_content_7zfiles.write("7z file {} not exist in {} \n".format(bitbake_7zname, bitbake_location))
            self.is_all_7zfiles_exist = False
        else:
            self.all_7zfiles.append(os.path.join(bitbake_location, bitbake_7zname))
        
    def traverse_recipes(self):
        self.is_all_7zfiles_exist = True
        self.mail_content_7zfiles = StringIO()
        self.all_7zfiles = []
        for package in self.bitbake_recipes:
            if package["package_name"] == "enb":
                for recipe in package["recipes"]:
                    if recipe["type"] == "target":
                        self.check_all_7zfiles_exist(recipe['name'].lower().replace("_", ""))
                    elif recipe["type"] == "source":
                        self.remove_from_scs(recipe['name'])
                    
    def remove_from_scs(self, sc_name):
        index = 0
        for sc in self.scs:
            if sc == sc_name:
                del self.scs[index]
                break
            index = index + 1
            
    def check_all_scs_configed(self):
        self.is_all_scs_configed = True
        ignore_list = self.config.get("ignoreSC", "").split(",")
        for sc in ignore_list:
            self.remove_from_scs(sc)
        if len(self.scs) > 0:
            self.is_all_scs_configed = False
            self.mail_content_scs = "These System Components {} are not configed in bitbake recipes.json".format(self.scs)
            
    def mails(self):
        self.mail_content = StringIO()
        self.mail_content.write("*This is an automatically generated email. Do not reply.*\n\n\n")
        self.is_need_mail = False
        
        if not self.is_all_7zfiles_exist:
            self.is_need_mail = True
            self.mail_content.write("**************************Missing 7z files**************************\n")
            self.mail_content.writelines(self.mail_content_7zfiles.getvalue())
            self.mail_content.write("\n\n")
            
        if not self.is_all_scs_configed:
            self.is_need_mail = True
            self.mail_content.write("**************************Scs not configed**************************\n")
            self.mail_content.write(self.mail_content_scs)
            self.mail_content.write("\n\n")
            
        if not self.is_recovered_bitbake:
            self.is_need_mail = True
            self.mail_content.write("**************************Recover bitbake**************************\n")
            self.mail_content.writelines(self.mail_content_recover.getvalue())
            self.mail_content.write("\n\n")
        elif not self.is_bitbake_content_fine:
            self.is_need_mail = True
            self.mail_content.write("**************************Recover bitbake**************************\n")
            self.mail_content.writelines(self.mail_content_recover.getvalue())
            self.mail_content.write("\n\n")

        if self.is_need_mail:
            mail = Mail(self.config.get("mail_from"), self.config.get("mail_to"))
            mail.create(self.config.get("mail_subject"), self.mail_content.getvalue())
            mail.send()
            
    def bitbake_content_check(self):
        self.is_bitbake_content_fine = True
        self.mail_content_bitbake_content = StringIO()
        if self.config.get("bitbakeContentCheck", False):
            package_path = self.config.get("packagePath", "")
            if package_path == "":
                self.logger.warning("packagePath not configed, ignore bitbake content check for {}".format(self.baseline))
                return
            official_hashContainer = os.path.join(package_path, "HashContainer_{}.txt".format(self.baseline))
            self.copy_official_hashContainer_to_current_folder(official_hashContainer)
            self.remove_ignore_lines("HashContainer_{}.txt".format(self.baseline))
            current_hashContainer = "lteDo/package/btssm/bts_sw/HashContainer_{}.txt".format(self.baseline)
            self.remove_ignore_lines(current_hashContainer)
            result = Shell().execute("diff {} {}".format("HashContainer_{}.txt".format(self.baseline), current_hashContainer), errorOuput=True)
            if isinstance(result, list) and result[0] != 0:
                self.is_bitbake_content_fine = False
                self.mail_content_bitbake_content.write(result[1])
                
    def copy_official_hashContainer_to_current_folder(self, official_path):
        Shell().execute("cp {} .".format(official_path))
        
    def remove_ignore_lines(self, file):  
        Shell().execute("sed -i '/TargetBD/d' {}".format(file))      
            
    def recover_bitbake(self):
        self.is_recovered_bitbake = True
        self.mail_content_recover = StringIO()
        if self.is_all_7zfiles_exist:
            os.mkdir("recover")
            os.chdir("recover")
            self.prepare_workspace()
        os.chdir("..")
            
    def prepare_workspace(self):
        prepare_script = os.path.join(self.config.get("bbScriptRepo"), "prepare-enb-ws.sh")
        SVN().export(prepare_script)
        if os.system("sh prepare-enb-ws.sh --enb {} --src enb".format(self.baseline)) == 0:
            self.logger.info("Successfully to prepare work space")
            self.package()
        else:
            self.logger.error("Error to recover bitbake with command 'prepare-enb-ws.sh --enb {} --src enb'".format(self.baseline))
            self.is_recovered_bitbake = False
            self.mail_content_recover.write("Error to recover bitbake with below command\n")
            self.mail_content_recover.write("prepare-enb-ws.sh --enb {} --src enb".format(self.baseline))
            
    def package(self):
        self.extract_7zfiles()
        if Shell().execute("source .property && make linsup.core -j24"):
            self.logger.info("Successfully package with bitbake result")
            self.bitbake_content_check()
        else:
            self.logger.error("Error to package with bitbake result, command is make linsup.core")
            self.is_recovered_bitbake = False
            self.mail_content_recover.write("Error to package with bitbake result for package {}\n".format(self.baseline))
            self.mail_content_recover.write("Package command is make linsup.core")
            
    def extract_7zfiles(self):
        for file in self.all_7zfiles:
            Shell().execute("7za x {} -yo'{}'".format(file, "lteDo")) 
            self.logger.info("Extract {} done".format(file))    
        
    def start(self):
        parse_config = ParseConfig(self.baseline)
        self.bitbake_recipes = parse_config.fetch_bitbake_config()
        self.config = parse_config.fetch_config()
        self.scs = parse_config.fetch_sc_from_package_config()
        self.externals = parse_config.get_externals()
        self.traverse_recipes()
        self.check_all_scs_configed()
        self.recover_bitbake()
        
        self.mails()
            
            
            
