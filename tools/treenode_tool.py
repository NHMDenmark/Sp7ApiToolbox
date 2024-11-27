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

  PURPOSE: Methods for manipulating a given Specify tree through the Specify7 API 
"""

# Internal Dependencies 
from models.treenode import TreeNode
from tools.sp7api_tool import Sp7ApiTool
import specify_interface

class TreeNodeTool(Sp7ApiTool):
    """
    Generic class for SP7 API tools that handle nodes in one of the Specify tree structures 
    """

    def __init__(self, specifyInterface: specify_interface.SpecifyInterface) -> None:
        """
        CONSTRUCTOR
            specifyInterface (obj) : Dependency injection of API wrapper. 
        """

        super().__init__(specifyInterface)

        self.getTreeDefItems()

    def runTool(self, args):
        """
        Execute the tool for operation. 
        CONTRACT 
            args (dict) : Must include the following items  
                            1. 'filename': name of the data file 
                            2. 'sptype': name of the type of tree i.e. 'storage', 'taxon' or 'geography'
        """

        super().runTool(args)


    def processRow(self, headers, row) -> None:
        """
        Generic empty method for handling individual data file rows
        """
        pass
  
    def addTreeNode(self, headers, row):
        """
        Add tree nodes recursively.
        """

        # Get parent of tree node 
        parent_rank = headers[0]
        parent_name = row[parent_rank]
        parent_id = self.getParentId(parent_name, parent_rank)
                
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
        child_nodes = self.sp.getSpecifyObjects(self.sptype, 1000, 0, {'fullname': child_name, 'parent': parent_id})

        # Get current rank item 
        rank = self.getTreeDefItem(headers[index]) 
        treedefitemid = str(rank['treeentries']).split('=')[1]
        
        # If no corresponding child nodes found, proceed to add child node
        if len(child_nodes) == 0:
            tree_node = TreeNode(0, child_name, child_name, parent_id, rank['rankid'], treedefitemid, 0, self.sptype)
            jsonString = tree_node.createJsonString()
            child_node = self.sp.postSpecifyObject(self.sptype, jsonString)
        else: 
            child_node = child_nodes[0]

        # If there is a next column that represents a subordinate child node, add that recursively
        if index < len(headers) - 1:
            # Recursively add any subordinate child node
            self.addChildNodes(headers, row, child_node['id'], index + 1)

    def getParentId(self, parent_name, parent_rank):
        """
        Retrieve the parent id for a given parent name
        """
        # Attempt to retrieve the parent node on name and rank id
        parent_rank_id = self.getRankId(parent_rank)
        parent_nodes = self.sp.getSpecifyObjects(self.sptype, 1, 0, {'fullname' : parent_name, 'rankid' : parent_rank_id})

        if not parent_nodes:
            # Not found: Create new parent node at tree root 
            root_parent = self.sp.getSpecifyObjects(self.sptype, 1, 0, {})[0]
            parent_defitemid = str(root_parent['definitionitem']).split('/')[4]
            tree_defid = str(root_parent['definition']).split('/')[4]
            next_child_defitem = self.sp.getSpecifyObjects(f'{self.sptype}treedefitem', 1, 0, 
                                {'parent':parent_defitemid, 'treedef':tree_defid})[0]
            print(next_child_defitem)
            new_parent = TreeNode(0,parent_name, parent_name, 
                                    root_parent['id'], 
                                    root_parent['rankid'], 
                                    next_child_defitem['id'], 
                                    tree_defid, 
                                    self.sptype)
             
            # Return newly created parent node 
            return self.sp.postSpecifyObject(self.sptype, new_parent.createJsonString())['id'] 
        
        # Return retrieved parent node
        return parent_nodes[0]['id']


    def validateRow(self, row) -> bool:
        """
        Unfinished method for evaluating whether row format is valid. 
        """
        
        return True

    def validateHeaders(self, headers) -> bool:
        """
        Method for ensuring that the file format can be used by the tool.
        """
        
        valid = super().validateHeaders(headers)
        
        # Create a dictionary with 'name' as key for quick lookup
        rank_names = {item['name']: item for item in self.TreeDefItems}
        
        for header in headers:
            if header not in rank_names:
                return False

        return valid

    def getTreeDefItems(self):
        """
        
        """
        
        self.TreeDefItems = self.sp.getSpecifyObjects(f"{self.sptype}treedefitem")

    def getTreeDefItem(self, header):
        """
        Get the tree definition item AKA node rank for a given header by looking it up in self.TreeDefItems.
        """

        for item in self.TreeDefItems:
            if item['name'] == header:
                return item
        
        raise Exception("Tree Def Item not found!")

    def getRankId(self, header):
        """
        Get the rank ID for a given header by looking it up in self.TreeDefItems.
        """
        for item in self.TreeDefItems:
            if item['name'] == header:
                return item['rankid']
        return 0 
    
    def __str__(self) -> str:
        """
        String representation of the tool.
        """
        return "TreeNodeTool"




    
    