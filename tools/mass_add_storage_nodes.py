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

  PURPOSE: Tool for mass adding storage nodes based on data file with a column for each level.

  The first column is supposed to represent the collection level. 
  Subordinate child nodes are flexible as long as they correspond to the Specify levels. 
  Please check enums.StorageRank for possible column names. 

  Example data file format (csv): 
  
  Collection;Cabinet;Shelf
  some collection; cabinet 1; shelf 1

"""

# Internal Dependencies 
from tools.sp7api_tool import Sp7ApiTool
import specify_interface
from models.storage_node import StorageNode
from models.storage_node import StorageRank

class MassAddStorageNodeTool(Sp7ApiTool):
    """
    Tool for merging storage nodes upwards towards their nearest parent.
    """

    def __init__(self, specifyInterface: specify_interface.SpecifyInterface) -> None:
        """
        CONSTRUCTOR
            specifyInterface (obj) : Dependency injection of API wrapper. 
        """

        super().__init__(specifyInterface)

    def processRow(self, headers, row) -> None:
        """
        Handle row by adding child storage location 
        """

        self.addStorageLocation(headers, row)
  
    def addStorageLocation(self, headers, row):
        """
        Add storage location nodes recursively.
        """

        # Get parent of storage node 
        parent_name = row[headers[0]]
        parent_id = self.getParentId(parent_name)
                
        if parent_id is None: 
            raise Exception("Could not retrieve parent node!")        

        # Start recursive addition of child nodes
        self.addChildNodes(headers, row, parent_id, 1)

    def addChildNodes(self, headers, row, parent_id, index):
        """
        Recursively add child nodes.
        """
        # Exit recursion when last column reached
        if index >= len(headers):
            return

        # Check if child node does not already exist 
        child_name = row[headers[index]]
        child_nodes = self.sp.getSpecifyObjects("storage", 1000, 0, {'fullname': child_name, 'parent': parent_id})

        # Get current rank item 
        rankid = StorageRank[headers[index]].value
        rank = self.sp.getSpecifyObjects('storagetreedefitem', 15, 0, {"rankid": rankid})[0]
        treedefitemid = str(rank['treeentries']).split('=')[1]
        
        # If no corresponding child nodes found, proceed to add child node
        if len(child_nodes) == 0:
            #storage_dict = {"name" : child_name,"fullname" : child_name,"parentid" : parent_id,"rankid" : rank['rankid'],"defitemid" : treedefitemid}
            storage_node = StorageNode(0, child_name, child_name, parent_id, rank['rankid'], treedefitemid, 0)
            jsonString = storage_node.createJsonString()
            child_node = self.sp.postSpecifyObject('storage', jsonString)
        else: 
            child_node = child_nodes[0]

        # If there is a next column that represents a subordinate child node, add that recursively
        if index < len(headers) - 1:
            # Recursively add any subordinate child node
            self.addChildNodes(headers, row, child_node['id'], index + 1)

    def getParentId(self, parent_name):
        """
        Retrieve the parent id for a given parent name
        """
        parent_nodes = self.sp.getSpecifyObjects("storage", 100, 0, {'fullname': parent_name})
        if not parent_nodes:
            return None
        
        return parent_nodes[0]['id']

    def validateRow(self, row) -> bool:
        """
        Unfinished method for evaluating whether row format is valid. 
        """
        print(row)
        return True

    def validateHeaders(self, headers) -> bool:
        """
        Method for ensuring that the file format can be used by the tool.
        """
        # Check headers to see if these fit the expected file format
        if len(headers) < 2:
            raise Exception("Wrong header count. Expected: at least 2")
            #return False
        else:
            if headers[0] != "Collection": 
                raise Exception("Wrong first header (parent node). Expected: Collection")
                #return False
            else:
                return True
        #return False
        
    def __str__(self) -> str:
        """
        String representation of the tool.
        """
        return "MassAddStorageNodeTool"
    
