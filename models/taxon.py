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
import util
from models.treenode import TreeNode

class Taxon(TreeNode):
    """
    Class encapsulating storage tree node relevant methods 
    """

    def __init__(self, id=None, name=None, fullname=None, taxon_author=None, parent_id=None, rank_id=None, 
                 treedefitemid=None, treedefid=None, is_accepted = True, accepted_taxon_id = None, is_hybrid = False,
                 taxon_key=None, taxon_key_source=None) -> None:
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

        self.taxon_key = taxon_key  # This is the taxon key in Specify, not the primary key
        self.taxon_key_source = taxon_key_source  # This is the source of the taxon key, e.g., 'GBIF', 'Wikidata', etc.

        self.version = 0

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
            'acceptedtaxon': f'/api/specify/{self.sptype}/{self.accepted_taxon_id}/' if not self.is_accepted else None, 
            'ishybrid': bool(self.is_hybrid),
            'text1' : self.taxon_key,  # Assuming text1 is used for the taxon key
            'text2' : self.taxon_key_source,  # Assuming text2 is used for the taxon key source
            'version': self.version
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
        else:
            pass
        self.definitionitem_id = jsonObject['definitionitem'].split('/')[4]
        self.treedef_id = jsonObject['definition'].split('/')[4] 
        self.rank = jsonObject['rankid']

        self.is_accepted = bool(jsonObject['isaccepted'])
        if not self.is_accepted:
            self.accepted_taxon_id = jsonObject['acceptedtaxon']
        
        self.is_hybdrid = bool(jsonObject['ishybrid'])
        self.create_datetime = datetime.datetime.strptime(jsonObject['timestampcreated'], '%Y-%m-%dT%H:%M:%S')
        self.sptype = jsonObject['resource_uri'].split('/')[3] 

        self.version = jsonObject['version']

    def getParent(self, specify_interface):
        """ """
        self.parent = Taxon()
        try:
            parentTaxonObj = specify_interface.getSpecifyObject(self.sptype, self.parent_id)
            self.parent.fill(parentTaxonObj)
        except:
            util.logLine("ERROR: Failed to retrieve parent taxon.",'error')
            
        return self.parent 
    
    def getChildCount(self, specify_interface):
        """ 
        Get the number of children for this taxon. If the children have not been retrieved yet, it will fetch them from the API.
        """
        if len(self.children) > 0:
            return len(self.children)
        
        self.getChildren(specify_interface)
            
        return len(self.children)
      
    def getChildren(self, specify_interface):
        """ 
        

        """
        
        try:
            childTaxonObj = specify_interface.getSpecifyObjects(self.sptype,limit=1000, offset=0, 
                                                                filters={'parent': f'{self.id}'})
            for childObj in childTaxonObj:
                childTaxon = Taxon()
                childTaxon.fill(childObj)
                self.children.append(childTaxon)
        except:
            util.logLine("ERROR: Failed to retrieve parent taxon.",'error')
            
        return self.children
    
    def get_headers(self):
        return f'"{self.sptype}id", "name", "fullname", "author"'        

    def __str__(self):
        return f'{self.id},"{self.name}","{self.fullname}","{self.author}"'

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
Variety = 240 
Subvariety = 250
Forma = 260 
Subforma = 270

"""       