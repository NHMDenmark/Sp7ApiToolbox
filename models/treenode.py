# -*- coding: utf-8 -*-
"""
  Created on November 25, 2024
  @author: Fedor Alexander Steeman, NHMD
  Copyright 2022 Natural History Museum of Denmark (NHMD)
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

  PURPOSE: Generic base class "TreeNode" for Specify objects that are (also) nodes in hierarchical tree structures.
"""



class TreeNode:
    """
    The model class is a base class for data models inheriting & re-using a suite of shared functions
    """

    def __init__(self, id, name, fullname, parent_id, rank_id, treedefitemid, treedefid, specify_type) -> None:
        """
        Constructor
        CONTRACT 
            name (String)           : name of the node 
            fullname (String)       : full name of the node
            parent_id (Integer)     : parent node's primary key in specify 
            rank_id (String)        : node rank's identifier 
            treedefitemid (Integer) : node rank's primary key in specify 
            treedefid (Integer)     : node tree's primary key in specify 
        """
        
        self.id = id
        self.name = name
        self.fullname = fullname
        self.parent_id = parent_id
        self.definitionitem_id = treedefitemid
        self.treedef_id = treedefid
        self.sptype = specify_type
        self.rank = rank_id

    def createJsonString(self) -> str:
        """
        Creates json representation of the object for posting or putting to the API. 
        """
       
        obj = {'fullname': self.fullname,
                'name': self.name,
                'rankid': self.rank,
                'parent': f'/api/specify/{self.sptype}/{self.parent_id}/', 
                'treedefid': f'/api/specify/{self.sptype}/{self.treedef_id}/', 
                'definitionitem': f'/api/specify/{self.sptype}treedefitem/{self.definitionitem_id}/'
            }
        
        return obj 

    def __str__(self):
        return f'[{self.sptype}] id:{self.id}, name:{self.name}, fullname = {self.fullname} '
