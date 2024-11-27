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
from tools.treenode_tool import TreeNodeTool
import specify_interface

class MassAddStorageNodeTool(TreeNodeTool):
    """
    Tool for merging storage nodes upwards towards their nearest parent.
    """

    def __init__(self, specifyInterface: specify_interface.SpecifyInterface) -> None:
        """
        CONSTRUCTOR
            specifyInterface (obj) : Dependency injection of API wrapper. 
        """

        self.sptype = 'storage'

        super().__init__(specifyInterface)

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
        Handle row by adding child storage location 
        """

        print(f'Adding node: {row}')

        self.addTreeNode(headers, row)
    
    def validateRow(self, row) -> bool:
        """
        Unfinished method for evaluating whether row format is valid. 
        """

        valid = super().validateHeaders(row)
        
        return valid

    def validateHeaders(self, headers) -> bool:
        """
        Method for ensuring that the file format can be used by the tool.
        """

        valid = super().validateHeaders(headers)
        
        return valid
        
    def __str__(self) -> str:
        """
        String representation of the tool.
        """
        return "MassAddStorageNodeTool"
    
