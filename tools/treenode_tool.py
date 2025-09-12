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
import specify_interface
import global_settings as app
from models.treenode import TreeNode
from tools.sp7api_tool import Sp7ApiTool
import util

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

        self.tree_definition = self.getTreeDefinition()

        self.getTreeDefItems()
        pass

    def runTool(self, args):
        """
        Execute the tool for operation. 
        CONTRACT 
            args (dict) : Must include the following item(s):
                            1. 'filename': name of the data file 
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

    def addChildNodes(self, headers, row, parent_id, index, filters) -> dict:
        """
        Recursively add child nodes and return the last child node added.
        """
        
        # Exit recursion when last column reached
        if index >= len(headers): return None

        # Check if child node already exists
        child_name = row[headers[index]].strip()

        # Skip empty entries and continue with the next index
        if child_name == '':
            return self.addChildNodes(headers, row, parent_id, index + 1)

        # Attempt to retrieve the child node from Specify7
        child_node = self.getTreeNode(child_name, parent_id, filters)

        # If no corresponding child node is found, proceed to add new child node
        if not child_node:
            # Create a new node if none was found 
            child_node = self.createTreeNode(headers, row, parent_id, index)
        
        # Recursive call for the next child node
        if index < len(headers) - 1:
            if child_node:
                last_child_node = self.addChildNodes(headers, row, child_node.id, index + 1)
            else:
                if last_child_node:
                    return last_child_node

        # Return the current child node if it's the last one added
        return child_node
    
    def createTreeNode(self, headers, row, parent_id, index) -> dict:
        """
        Generic method for creating tree node 
        """

        rank = self.getTreeDefItem(headers[index])
        treedefitemid = str(rank['treeentries']).split('=')[1]
        name = row[headers[index]]
        rank_id = rank['rankid']

        # Create the tree node object
        node = TreeNode(0, name, name, parent_id, rank_id, treedefitemid, self.tree_definition, self.sptype)

        # Post the taxon node to the API
        jsonString = node.createJsonString()
        sp7_obj = self.sp.postSpecifyObject(self.sptype, jsonString)

        # Assign the ID from the API response
        node.id = sp7_obj['id']

        return node

    def getTreeNode(self, child_name, parent_id, filters={}) -> dict:
        """ 
        Attempt to fetch tree node instance from Specify7 based on name and parent id. 
        """

        filters.update({
            'name': child_name,
            'parent': parent_id, 
            'definition': self.tree_definition
        })

        child_dict = self.sp.getSpecifyObjects(self.sptype, 1000, 0, filters)

        child_nodes = []
        for child in child_dict:
            node = TreeNode.init(child)
            child_nodes.append(node)
        
        # Use the first matching existing node
        if len(child_nodes) > 0:
            return child_nodes[0]

        return None

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
            next_child_defitem = self.sp.getSpecifyObjects(f'{self.sptype}treedefitem', 1, 0, 
                                {'parent':parent_defitemid, 'treedef':self.tree_definition})[0]
            new_parent = TreeNode(0,parent_name, parent_name, 
                                    root_parent['id'], 
                                    root_parent['rankid'], 
                                    next_child_defitem['id'], 
                                    self.tree_definition, 
                                    self.sptype)
             
            # Return newly created parent node 
            return self.sp.postSpecifyObject(self.sptype, new_parent.createJsonString())['id'] 
        
        # Return retrieved parent node
        return parent_nodes[0]['id']

    def validateRow(self, row) -> bool:
        """
        Unfinished method for evaluating whether row format is valid. 
        """

        valid = super().validateRow(row)

        return valid

    def validateHeaders(self, headers) -> bool:
        """
        Method for ensuring that the file format can be used by the tool.
        """
        
        valid = super().validateHeaders(headers)
        
        # Create a dictionary with 'name' as key for quick lookup
        rank_names = {item['name']: item for item in self.TreeDefItems}

        for header in headers:
            if 'TaxonKey' or 'Accepted' in header:
                # Skip TaxonKey & Accepted taxon headers as they are not part of the tree definition
                continue
            if header not in rank_names:
                print("Validation failed: Header '{}' is not a valid rank in the tree definition.".format(header))
                util.logger.debug(f"Validation failed: Header '{header}' is not a valid rank in the tree definition.")
                return False

        return valid

    def getTreeDefinition(self):
        """
        Retrieve the tree definition for the tree type specified in self.sptype 
        """
        
        if self.sptype != 'storage':
            collections = self.sp.getSpecifyObjects('collection', 1, 0, {'collectionname': app.settings['collectionName']})
            if not collections: raise ValueError("No collections found with the specified name.")
            collection = collections[0]
            discipline = self.sp.getSpecifyObject('discipline', collection['discipline'].split('/')[4])   
            treedef_id =  discipline[f'{self.sptype}treedef'].split('/')[4]
        else:  
            treedef_id = 1

        return treedef_id

    def getTreeDefItems(self):
        """
        
        """
        
        self.TreeDefItems = self.sp.getSpecifyObjects(f"{self.sptype}treedefitem", sort='rankid', filters={"treedef":self.tree_definition})

    def getTreeDefItem(self, header):
        """
        Get the tree definition item AKA node rank for a given header by looking it up in self.TreeDefItems.
        """

        # Removed "Accepted" prefix if present
        if 'Accepted' in header: header = header.replace('Accepted', '').strip()

        for item in self.TreeDefItems:
            if item['name'] == header:
                return item
        
        #return None
        raise Exception(f"Tree Def Item '{header}' not found!")

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




    
    