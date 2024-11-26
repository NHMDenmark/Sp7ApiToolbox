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
from models import treenode

class StorageNode(treenode.TreeNode):
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
            rank_id (String)        : storage node rank's identifier 
            treedefitemid (Integer) : storage node rank's primary key in specify 
        """
        
        self.sptype = 'storage'

        treenode.TreeNode.__init__(self, id, name, fullname, parent_id, rank_id, treedefitemid, treedefid)

        self.rank = StorageRank(rank_id).value


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