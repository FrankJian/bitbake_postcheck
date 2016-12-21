'''
Created on Dec 9, 2016

@author: xiaopan
'''
import json
import os

from config.config import BitbakePostCheckConfig
from utils.externals import Externals
from utils.log import Log
from utils.svn import SVN


class ParseConfig(object):
    '''
    classdocs
    '''


    def __init__(self, baseline):
        '''
        Constructor
        '''
        self.logger = Log().getLogger("ParseConfig")
        self.baseline = baseline.strip()
        self.externals = ""
        self.fetch_config()
        self._check_config()
        
    def get_externals(self):
        if self.externals == "":
            self._parse_externals()
        return self.externals
        
    def _parse_externals(self):
        self.externals = Externals(self.baseline).parse()
        
    def fetch_config(self):
        self.config = BitbakePostCheckConfig(self.baseline).get_configs()
        self._parse_externals()
        self._set_specific_config()
        self.logger.info("Configuration for baseline " + self.baseline)
        self.logger.info(self.config)
        return self.config
    
    def _set_specific_config(self):
        if self.externals.get("CB_BB_PATTERN", "") == "":
            self.config["patternRepo"] = self.config.get("defaultPatternRepo", "")
        else:
            externals = self.externals.get("CB_BB_PATTERN").get("externals", "")
            if externals == "" or len(externals) == 0 or externals[0].get("repo_path", "") == "":
                self.config["patternRepo"] = self.config.get("defaultPatternRepo", "")
            else:
                if externals[0].get("revision", "") == "":
                    patternRepo = externals[0].get("repo_path")
                else:
                    patternRepo = "{}@{}".format(externals[0].get("repo_path"), externals[0].get("revision"))
                self.config["patternRepo"] = "{}{}".format(self.config.get("svnServer"), patternRepo)
        if self.externals.get("CB_BB_SCRIPTS", "") == "":
            self.config["bbScriptRepo"] = self.config.get("defaultBbScriptRepo", "")
        else:
            externals = self.externals.get("CB_BB_SCRIPTS").get("externals", "")
            if externals == "" or len(externals) == 0 or externals[0].get("repo_path", "") == "":
                self.config["bbScriptRepo"] = self.config.get("defaultBbScriptRepo", "")
            else:
                if externals[0].get("revision", "") == "":
                    patternRepo = externals[0].get("repo_path")
                else:
                    patternRepo = "{}@{}".format(externals[0].get("repo_path"), externals[0].get("revision"))
                self.config["bbScriptRepo"] = "{}{}".format(self.config.get("svnServer"), patternRepo)
        
    def _check_config(self):
        pattern_repo = self.config.get("patternRepo", "")
        module = self.config.get("module", "")
        product_id = self.config.get("productId", "")
        bitbake_path = self.config.get("bitbakePath", "")
        repo = self.config.get("repo", "")
        if pattern_repo == "" or module == "" or product_id == "" or bitbake_path == "" or repo == "":
            raise Exception("Missing configurations, please double check")
        
    def fetch_sc_from_package_config(self):
        config = self._read_package_config()
        return self._parse_package_config(config)
        
    def _parse_package_config(self, config):
        baselines_from_share = "<baselines from share>"
        scs = self._get_sc(config, baselines_from_share)
        baselines_from_externals = "<baselines from svn:external>"
        scs.extend(self._get_sc(config, baselines_from_externals))
        self.logger.debug("Sc list is {}".format(scs))
        return scs
    
    def _get_sc(self, config, start_line): 
        sc_name = []
        
        start = False
        for line in config:
            line = line.strip()
            if line == "":
                continue
            if line == start_line:
                start = True
                continue
            if start:
                if line == "</baselines>":
                    break
                sc = line.split()[0]
                sc_name.append(sc)
        return sc_name
        
    def _read_package_config(self):
        package_config = SVN().cat(os.path.join(self.config.get("repo"), self.baseline, ".config")).splitlines()
        return package_config
        
    def _read_hardwares(self):
        pattern_config = os.path.join(self.config.get("patternRepo"), self.config.get("productId"), self.config.get("module"), 'config.json')
        hardwares = []
        if SVN().checkifexist(pattern_config):
            config = json.loads(SVN().cat(pattern_config))
            hardwares = config["hardwares"]
        else:
            hardwares.append(os.path.join(self.config.get("productId"), self.config.get("module")))
        return hardwares
    
    def fetch_bitbake_config(self):
        self.hardwares = self._read_hardwares()
        if len(self.hardwares) > 1:
            self.logger.info("Merging recipes data from {}".format(', '.join(self.hardwares)))
            self.recipes_data = self._merge_recipe_data()
        else:
            recipes_file = os.path.join(self.config.get("patternRepo"), self.hardwares[0], 'recipes.json')
            json_data = SVN().cat(recipes_file)
            self.recipes_data = json.loads(json_data)
        return self.recipes_data
            
    def _merge_recipe_data(self):
        json_recipes = self._read_recipes_files()
        package_names = set()
        for file in json_recipes:
            for package in file:
                package_names.add(package["package_name"])
        recipes_data = []
        for package in package_names:
            data = self._merge_package(json_recipes, package)
            recipes_data.append(data)
        return recipes_data
        
    def _read_recipes_files(self):
        json_recipes = []
        for hw in self.hardwares:
            recipes_file = os.path.join(self.config.get("patternRepo"), hw, 'recipes.json')
            self.logger.info("Reading {}".format(recipes_file))
            json_data = SVN().cat(recipes_file)
            json_recipes.append(json.loads(json_data))
        return json_recipes
    
    def _merge_package(self, json_recipes, package_name):
        recipes = []
        target_names = set()
        package_data = {"package_name": package_name}
        package_dependencies = set()
        pattern_sources = set()
        for file in json_recipes:
            for package in file:
                if package["package_name"] == package_name:
                    for dependency in package["depends_on"]:
                        package_dependencies.add(dependency)
                    if "pattern_sources" in package:
                        for src in package["pattern_sources"]:
                            pattern_sources.add(src)
                    for target in package["recipes"]:
                        if target["name"] not in target_names:
                            target_names.add(target["name"])
                            recipes.append(target)
                        else:
                            index = self._find_target(recipes, target["name"])
                            recipes[index] = self._merge_recipes(recipes[index], target)
        package_data["recipes"] = recipes
        package_data["depends_on"] = list(package_dependencies)
        package_data["pattern_sources"] = list(pattern_sources)
        return package_data
    
    def _find_target(self, recipes, name):
        for i in range(len(recipes)):
            if recipes[i]["name"] == name:
                return i
        raise IndexError
    
    def _merge_recipes(self, target1, target2):
        if target1["type"] == "target" and target2["type"] == "target":
            target1["architectures"] = self._merge_values(target1, target2, "architectures")
            target1["depends_on"] = self._merge_values(target1, target2, "depends_on")
        elif target1["type"] == "source" and target2["type"] == "source":
            if not "require_to_package" in target1:
                target1["require_to_package"] = True
            if not "require_to_package" in target2:
                target2["require_to_package"] = True
            target1["require_to_package"] = target1["require_to_package"] or target2["require_to_package"]
        else:
            print('ERROR: Could not merge recipes with different types')
        return target1
    
    def _merge_values(self, target1, target2, key):
        for value in target2[key]:
            if value not in target1[key]:
                target1[key].append(value)
        return target1[key]
        
        
