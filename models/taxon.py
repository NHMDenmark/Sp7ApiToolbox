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

from enum import Enum
from models import treenode

class Taxon(treenode.TreeNode):
    """
    Class encapsulating storage tree node relevant methods 
    """

    def __init__(self, id, name, fullname, parent_id, rank_id, treedefitemid, treedefid) -> None:
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
        
        self.sptype = 'taxon'
        
        treenode.TreeNode.__init__(self, id, name, fullname, parent_id, rank_id, treedefitemid, treedefid)

        self.rank = TaxonRank(rank_id).value


class TaxonRank(Enum):
    """
    Taxon names paired with rank ids as derived from a standard Specify setup
    """
    Life = 0 
    Kingdom = 10 
    Phylum = 30 
    Subphylum = 40 
    Superclass = 50 
    Class = 60 
    Subclass = 70 
    Infraclass = 80 
    Superorder = 90 
    Order = 100 
    Suborder = 110 
    Infraorder = 120 
    Superfamily = 130 
    Family = 140 
    Subfamily = 150 
    Tribe = 160 
    Subtribe = 170 
    Genus = 180 
    Subgenus = 190 
    Species = 220 
    Subspecies = 230 
    Empty = -1