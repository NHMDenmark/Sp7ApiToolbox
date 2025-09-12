# -*- encoding: utf-8 -*-
"""
  Created on November 28, 2024
  @author: Fedor Alexander Steeman, NHMD
  Copyright 2024 Natural History Museum of Denmark (NHMD)
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

  PURPOSE: Configuration handler for main application and unit tests

"""

import json
import importlib

#Internal Dependencies
import specify_interface
import global_settings as app

class ConfigurationHandler():
    """
    
    """

    def __init__(self) -> None:
        """
        CONSTRUCTOR
        """
        
        self.toolKit = []
    
   
    def loadConfiguration(self, mode):
        """
        Loads the main app configuration file depending on mode. 
        If no mode name is specified, it will use the default config.json
        If a mode name is passed as an argument, it will use the config.[mode].json
        CONTRACT 
            mode (String) : The name of the mode of operation 
        """
        if mode != "": mode = "." + mode
        with open(f"config/config{mode}.json", "r") as file:
            config = json.load(file)

        if config:
            self.mode = config['mode']
            app.settings['baseURL'] = config['domain']
            app.settings['collectionName'] = config['collection']
            app.settings['userName'] = config['username']
            app.settings['password'] =  config['password']
            app.settings['csrfToken'] = ''  # CSRF token is empty at this point
        else:
            raise Exception("Configuration error!") 
                
        self.sp = specify_interface.SpecifyInterface()

        collections = self.sp.getInitialCollections()

        app.settings['collectionId'] = collections.get(app.settings['collectionName'], None)

        self.sp.login(app.settings['userName'], 
                      app.settings['password'], 
                      app.settings['collectionId'],
                      self.sp.getCSRFToken())
        pass

    def loadTools(self):
        """
        Load tools dynamically from a JSON configuration file.
        The tools json must specify the name, class and module of the tool. 
        """

        with open("tools.json", "r") as file:
            config = json.load(file)

        tools = config.get("tools", [])

        if tools:
            for tool in tools:
                module = importlib.import_module(tool["module"])
                class_ = getattr(module, tool["class"])
                instance = class_(self.sp)
                self.toolKit.append((tool["name"], instance))
        else:
            raise Exception("No tools loaded...")