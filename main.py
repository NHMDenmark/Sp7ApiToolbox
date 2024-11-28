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

#Internal Dependencies
import global_settings as app
import configuration

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

        self.cfg = configuration.ConfigurationHandler()
        self.cfg.loadConfiguration(mode)
        self.cfg.loadTools()

        self.main()


    def main(self):
        """
        Run main method
        """
        util.cls()
        print("**** Specify7 API Toolbox ****")
        print("Current domain: ", app.settings['baseURL'])
        print("Selected collection:", app.settings['collectionName'])

        self.selectTool()
        self.selectDatafile()

        print("Running tool...")
        args = {'filename' : self.filename}
        self.tool_instance.runTool(args)  # Assuming each tool has a run method

        print("*** Finished running tool ***")


    def selectDatafile(self):
        """
        Allow user interaction in CLI to select the data file for use by the tool. 
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
        Allow user interaction in CLI to select the tool for operations. 
        """

        print("\nChoose your tool: ")

        for index, (name, _) in enumerate(self.cfg.toolKit, start=1):
            print(f"{index}. {name}")

        entry = input("\nEnter the number of the tool you want to run: ")
        if not entry.isnumeric():
            print("Invalid choice. Please try again.")
            self.selectTool()

        choice = int(entry) - 1

        if 0 <= choice < len(self.cfg.toolKit):
            tool_name, self.tool_instance = self.cfg.toolKit[choice]
            print(f"\nSelected tool: {tool_name}")
        else:
            print("Invalid choice. Please try again.")
            self.selectTool()
      

# Application execution entry point 
if __name__ == "__main__":
    """
    Start main execution thread.
    """

    # Check if run mode parameter has been passed 
    mode = sys.argv[1] if len(sys.argv) > 1 else ""

    # Initialize according to mode, if any set at all
    main = Main(mode)
    
