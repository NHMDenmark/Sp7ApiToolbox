# -*- encoding: utf-8 -*-
"""
  Created on November 25, 2024
  @author: Fedor Alexander Steeman, NHMD
  Copyright 2024 Natural History Museum of Denmark (NHMD)
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

  PURPOSE:

"""

import datetime

# Internal Dependencies 
from models.treenode import TreeNode

class Taxon(TreeNode):
    """
    Class encapsulating storage tree node relevant methods 
    """

    def __init__(self, id=None, name=None, fullname=None, taxon_author=None, parent_id=None, rank_id=None, treedefitemid=None, treedefid=None, is_accepted = True, accepted_taxon_id = None, is_hybrid = False) -> None:
        """
        Constructor
        CONTRACT 
            name (String)           : name of the storage tree node 
            fullname (String)       : full name of the storage tree node
            parent_id (Integer)     : parent storage node's primary key in specify 
            rank_id (String)        : taxon rank's identifier 
            treedefitemid (Integer) : taxon rank's primary key in specify 
            treedefid (Integer)     : taxon tree's primary key in specify 
        """
        
        TreeNode.__init__(self, id, name, fullname, parent_id, rank_id, treedefitemid, treedefid)
        
        self.sptype = 'taxon'        
        self.author = taxon_author
        self.rank = rank_id

        self.is_accepted = is_accepted
        self.accepted_taxon_id = accepted_taxon_id
        self.is_hybrid = is_hybrid

    def createJsonString(self) -> str:
        """
        Creates JSON representation of the object for posting or putting to the API.
        """

        # Create the JSON object
        obj = {
            'fullname': self.fullname,
            'name': self.name,
            'rankid': self.rank,
            'parent': f'/api/specify/{self.sptype}/{self.parent_id}/',
            'definition': f'/api/specify/{self.sptype}treedef/{self.treedef_id}/',
            'definitionitem': f'/api/specify/{self.sptype}treedefitem/{self.definitionitem_id}/',
            'author': self.author,
            'isaccepted': bool(self.is_accepted),
            'ishybrid': bool(self.is_hybrid)
        }

        # Conditionally add acceptedtaxon key
        if not self.is_accepted:
            obj['acceptedtaxon'] = f'/api/specify/taxon/{self.accepted_taxon_id}/'

        return obj
    
    @classmethod
    def init(cls, jsonObject):
        """
        Initialize treenode by filling it from json string contents as returned from API
        """
        instance = cls()
        instance.fill(jsonObject)
        return instance

    def fill(self, jsonObject):
        """
        Fill treenode from json string contents as returned from API
        """

        self.id = jsonObject['id']
        self.name = jsonObject['name']
        self.fullname = jsonObject['fullname']
        self.author = jsonObject['author']
        if jsonObject['parent']:
            self.parent_id = jsonObject['parent'].split('/')[4]
        self.definitionitem_id = jsonObject['definition'].split('/')[4]
        self.treedef_id = jsonObject['definitionitem'].split('/')[4] 
        self.rank = jsonObject['rankid']

        self.is_accepted = bool(jsonObject['isaccepted'])
        if not self.is_accepted:
            self.accepted_taxon_id = jsonObject['acceptedtaxon']
        
        self.is_hybdrid = bool(jsonObject['ishybrid'])
        self.create_datetime = datetime.datetime.strptime(jsonObject['timestampcreated'], '%Y-%m-%dT%H:%M:%S')
        self.sptype = jsonObject['resource_uri'].split('/')[3] 

"""

Life= 0 
Kingdom= 10 
Phylum= 30 
Subphylum= 40 
Superclass= 50 
Class= 60 
Subclass= 70 
Infraclass= 80 
Superorder= 90 
Order= 100 
Suborder= 110 
Infraorder= 120 
Superfamily= 130 
Family= 140 
Subfamily= 150 
Tribe= 160 
Subtribe= 170 
Genus= 180 
Subgenus= 190 
Species= 220 
Subspecies= 230 

"""       