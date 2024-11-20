# -*- encoding: utf-8 -*-
"""
  Created on November 05, 2024
  @author: Fedor Alexander Steeman, NHMD
  Copyright 2024 Natural History Museum of Denmark (NHMD)
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

  PURPOSE: Main starting point of application 
"""

import os
import sys
import util
import json
import importlib

#Internal Dependencies
import specify_interface
import global_settings as gs
from tools.mass_add_storage_nodes import MassAddStorageNodeTool

class Main():
    """
    Main starting point of the application.
    """

    def __init__(self, mode) -> None:
        """
        Initialize main class 
        """
        util.buildLogger()
        util.logger.debug(f"__init__ , {mode}")

        self.loadConfiguration(mode)
          
        self.loadTools()

        self.main()


    def main(self):
        """
        Run main method
        """
        util.cls()
        print("**** Specify7 API Toolbox ****")
        print("Current domain: ", gs.baseURL)
        print("Selected collection:", gs.collectionName)

        self.selectTool()
        self.selectDatafile()

        print("Running tool...")
        args = {'filename': self.filename}
        self.tool_instance.runTool(args)  # Assuming each tool has a run method


    def selectDatafile(self):
        """
        
        """

        self.dataFiles = os.listdir("data")

        print("\nChoose your datafile:")
        for index, name in enumerate(self.dataFiles, start=1):
                    print(f"{index}. {name}")
        dataFile = int(input("\nEnter the number of the datafile you want to use: ")) - 1

        if 0 <= dataFile < len(self.dataFiles):
            self.filename = self.dataFiles[dataFile]
            print(f"\nSelected datafile: {self.filename}")
        else:
            print("Invalid choice. Please try again.")
            self.selectDatafile()

    def selectTool(self):
        """
        
        """

        print("\nChoose your tool: ")

        for index, (name, _) in enumerate(self.toolKit, start=1):
            print(f"{index}. {name}")

        choice = int(input("\nEnter the number of the tool you want to run: ")) - 1

        if 0 <= choice < len(self.toolKit):
            tool_name, self.tool_instance = self.toolKit[choice]
            print(f"\nSelected tool: {tool_name}")
        else:
            print("Invalid choice. Please try again.")
            self.selectTool()
   
    def loadConfiguration(self, mode):
        """
        
        """
        if mode != "": mode = "." + mode
        with open(f"config{mode}.json", "r") as file:
            config = json.load(file)

        if config:
            self.mode = config['mode']
            gs.baseURL = config['domain']
            gs.collectionName = config['collection']
            gs.userName = config['username']
            gs.password =  config['password']
        else:
            raise Exception("Configuration error!") 
                
        self.sp = specify_interface.SpecifyInterface()

        collections = self.sp.getInitialCollections()

        print(collections)

        gs.collectionId = collections.get(gs.collectionName, None)
        print(gs.collectionId)

    def loadTools(self):
        """
        Load tools dynamically from a JSON configuration file.
        """

        self.toolKit = []

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
       

# Application execution entry point 
if __name__ == "__main__":
    """
    Initiate main class
    """

    # Check if run mode parameter has been passed 
    mode = sys.argv[1] if len(sys.argv) > 1 else ""

    # Initialize according to mode, if any set at all
    main = Main(mode)
    