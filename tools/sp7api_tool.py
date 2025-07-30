# -*- encoding: utf-8 -*-
"""
  Created on November 15, 2024
  @author: Fedor Alexander Steeman, NHMD
  Copyright 2024 Natural History Museum of Denmark (NHMD)
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

  PURPOSE: Methods for manipulating the storage tree through the Specify7 API 
"""

import os
import csv

# Internal Dependencies
import global_settings as app
import specify_interface
import util
import models.collection as coll

class Sp7ApiTool:
    """
    Generic class for tools that interact with the Specify7 API 
    """

    def __init__(self, specifyInterface: specify_interface.SpecifyInterface) -> None:
        """
        CONSTRUCTOR
        Initialize the tool with the Specify interface injected as argument and log on user to Specify7 API.
        Design pattern: Dependency injection. 
        CONTRACT
            specifyInterface (specify_interface.SpecifyInterface) : specify interface class instance
        """

        self.sp = specifyInterface

        user_name = app.settings['userName']
        pass_word = app.settings['password']
        coll_id   = app.settings['collectionId']

        self.collection = coll.Collection(coll_id, self.sp)
        
        # Log in to Specify API and get CSFR token 
        token = self.sp.specifyLogin(user_name, pass_word, coll_id)
        if token == '': 
            msg = f"Could not log in with these credentials ({user_name}) to collection ({app.settings['collectionName']} : {coll_id})! "
            util.logger.error(msg)
            raise Exception(msg)

    def runTool(self, args):
        """
        Execute the tool for operation. 
        CONTRACT 
            args (dict) : Must normally include the following items(s):  
                            1. 'filename': name of the data file (can be omitted depending on tool) 
        """

        filename = args.get('filename')
        if not filename:
            raise Exception("No filename provided in args.")

        if not os.path.isfile(f'data/{filename}'):
            raise Exception(f"File {filename} does not exist.")

        print(f"Processing file: {filename}")
        self.handleDatafile(filename)

    def handleDatafile(self, filename):
        """
        
        """

        with open(f'data/{filename}', mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, delimiter=',') # TODO Specify delimiter for files 
            headers = csv_reader.fieldnames
            if self.validateHeaders(headers):
                for row in csv_reader:
                    if self.validateRow(row):
                        self.processRow(headers, row)
    
    def processRow(self, headers, row) -> None:
        """
        Generic empty method for handling individual data file rows
        """
        pass

    def validateRow(self, row) -> bool:
        """
        Unfinished method for evaluating whether row format is valid. 
        """
        
        return True

    def validateHeaders(self, headers) -> bool:
        """
        Method for ensuring that the file format can be used by the tool.
        """
        
        return True

    def __str__(self) -> str:
        """
        String representation of the tool.
        """
        return "Sp7ApiTool"




    
    

