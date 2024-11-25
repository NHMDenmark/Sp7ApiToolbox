# -*- encoding: utf-8 -*-
"""
  Created on November 22, 2024
  @author: Fedor Alexander Steeman, NHMD
  Copyright 2024 Natural History Museum of Denmark (NHMD)
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

  PURPOSE:

"""
from enum import Enum
#from enums import StorageRank

class StorageNode():
    """
    Class encapsulating storage tree node relevant methods 
    """

    def __init__(self, name, fullname, parent_id, rank_id, treedefitemid) -> None:
        """
        Constructor
        CONTRACT 
            record (dict)
        """
        
        self.sptype = 'storage'
        
        self.name = name
        self.fullname = fullname
        self.rank = StorageRank(rank_id).value
        self.parent_id = parent_id
        self.definitionitem = treedefitemid
        self.discipline = None
        self.collection = None

    def createJsonString(self) -> str:
        """
        Creates json representation of the storage node for posting or putting to the API. 
        """
       
        node = {'fullname': self.fullname,
                'name': self.name,
                'rankid': self.rank,
                'parent': f'/api/specify/storage/{self.parent_id}/', 
                'definitionitem': f'/api/specify/storagetreedefitem/{self.definitionitem}/'
            }
        
        return node 

class StorageRank(Enum):
    """
    Storage names paired with rank ids as derived from a standard Specify setup
    """
    Institution = 0 
    Collection = 150 
    Room = 200 
    Aisle = 250 
    Cabinet = 300 
    Shelf = 350 
    Box = 400 
    Rack = 450 
    Vial = 500 
    Site = 75 
    CryoBox = 475 
    Empty = -1