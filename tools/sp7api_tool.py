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

import json

# Internal Dependencies
import global_settings as gs
import specify_interface
import util

class Sp7ApiTool:
    """
    The Storage Tree Tool groups methods specifically meant to perform actions on the Specify storage tree through the API.
    ...
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
        token = self.sp.specifyLogin(gs.userName, gs.password, gs.collectionId)
        if token == '': 
            msg = f"Could not log in with these credentials ({gs.userName}) and collection ({gs.collectionName} : {gs.collectionId})! "
            util.logger.error(msg)
            raise Exception(msg)

    def runTool(self, args: dict) -> None:
        """
        Run the tool with the given arguments.
        CONTRACT 
            args (dict) : dictionary of arguments. 
        """
        print(args)


    def __str__(self) -> str:
        """
        String representation of the tool.
        """
        return "Sp7ApiTool"




    
    

