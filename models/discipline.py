# -*- coding: utf-8 -*-
"""
  Created on September 28, 2022
  @author: Fedor Alexander Steeman, NHMD
  Copyright 2022 Natural History Museum of Denmark (NHMD)
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

  PURPOSE: Represent discipline data record as "Model" in the MVC pattern  
"""

# Internal dependencies
from models import model

class Discipline(model.Model):
    """
    Class representing a discipline data record  
    """

    def __init__(self, collection_id) -> None:
        # Set up blank record 
        model.Model.__init__(self, collection_id)
        self.table   = 'discipline'
        self.sptype  = 'discipline'
        self.taxontreedefid = 0

    def fill(self, jsonObject, source="Specify"):
        """
        Specific function for filling discipline instance's fields with data from record fetched from external source 
        CONTRACT 
            jsonObject (json)  : Specify data record fetched from external source 
        """
        self.source = source
        if jsonObject:
            if source=="Specify":
                self.spid = jsonObject['id']
                self.name = jsonObject['name']
                #self.fullname = jsonObject['collectionname']
                self.taxontreedefid = jsonObject['taxontreedef'].split('/')[4]
        else:
            self.remarks = 'Could not set values, because empty object was passed. '

# Generic functions
    
    def __str__ (self):
        return f'[{self.table}] id:{self.id}, spid:{self.spid}, name:{self.name}'
