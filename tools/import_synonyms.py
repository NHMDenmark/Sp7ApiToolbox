# -*- encoding: utf-8 -*-
"""
  Created on November 18, 2024
  @author: Fedor Alexander Steeman, NHMD
  Copyright 2024 Natural History Museum of Denmark (NHMD)
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

  PURPOSE: Tool for merging storage nodes upwards towards their nearest parent 
"""

# Internal Dependencies 
from tools.treenode_tool import TreeNodeTool
from models.taxon import Taxon
import specify_interface

class ImportSynonymTool(TreeNodeTool):
    """
    Tool 
    """        

    def __init__(self, specifyInterface: specify_interface.SpecifyInterface) -> None:
        """
        
        """

        self.sptype = 'taxon'
        
        super().__init__(specifyInterface)
        
    def processRow(self, headers, row) -> None:
        """
        Handle row by ...
        """

        index = headers.index('isAccepted')

        # First add accepted taxa nodes if they don't already exist
        

        # Get primary keys of accepted taxa node 

        # Add synonym node to tree 

        pass

    def addSynonymNode(self, headers, row):
        """
        
        """

        pass


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

        index = headers.index('isAccepted')
        if index <= 0:
            return False
                
        if headers[index-1] == 'Author': 
            pass

        tax_headers = headers[:index]
        syn_headers = headers[index:]

        # Remove author fields for validation
        tax_headers = [header for header in tax_headers if "Author" not in header]

        valid = super().validateHeaders(tax_headers)

        return valid

    def createTreeNode(self, headers, row, parent_id, index):
        """
        Specific method for creating taxon tree node 
        """

        rank = self.getTreeDefItem(headers[index])
        treedefitemid = str(rank['treeentries']).split('=')[1]
        name = row[headers[index]]
        rank_id = rank['rankid']
        
        # TODO generate full name when infrageneric 
        fullname = ''
        if rank_id > 180:
            for r in reversed(self.TreeDefItems):
                if r['name'] in row:
                    fullname = row[r['name']] + ' ' + fullname
                if r['name'] == "Genus": 
                    break
        fullname = fullname.strip()

        author = ''
        if headers[index]+'Author' in row:
            author = row[headers[index]+'Author']
        node = Taxon(0, name, fullname, author, parent_id, rank['rankid'], treedefitemid, 0)

        return node
    

    def __str__(self) -> None:
        """
        """
        return "ImportSynonymTool"


"""

Species Author
Subspecies
Subspecies Author
isAccepted
AcceptedGenus
AcceptedSpecies
AcceptedSpeciesAuthor
AcceptedSubspecies
AcceptedSubspeciesAuthor

"""