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

        # Keep synonymy headers separate 
        hitax_index = headers.index('Genus')        # Higher taxonomy columns index
        acc_index   = headers.index('isAccepted')+1 # Accepted taxon columns index
        acc_headers = headers[acc_index:]           # Accepted taxon headers        
        syn_headers = headers[:acc_index]           # Synonym headers
        
        # Remove "Accepted" from accepted headers
        #acc_headers = [header.replace('Accepted', '') for header in acc_headers]

        # Remove author fields for validation
        acc_headers = [header for header in acc_headers if "Author" not in header]
        
        # Merge accepted taxon headers with higher taxonomy headers
        acc_headers = headers[0:hitax_index] + acc_headers

        # get root of tree (Life?)
        root = self.sp.getSpecifyObjects('taxon', limit=1)[0]
        
        # Add accepted taxa nodes if they don't already exist
        acc_node = self.addChildNodes(acc_headers, row, root['id'], 0)

        # Merge synonym taxon headers with higher taxonomy headers
        syn_headers = syn_headers + headers[hitax_index:acc_index]

        # Add synonym node to tree 
        self.createSynonymNode(syn_headers, row, acc_node)

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
        try:
            index = headers.index('isAccepted')
        except ValueError:
            # 'isAccepted' not found in headers
            return False

        index = headers.index('isAccepted')
        if index <= 0:
            return False
                
        #if headers[index-1] == 'Author': pass

        taxon_headers = [header for header in headers[:index] if 'Author' not in header]

        valid = super().validateHeaders(taxon_headers)

        return valid


    def addChildNodes(self, headers, row, parent_id, index) -> dict:
        """
        """
        return super().addChildNodes(headers, row, parent_id, index)

    def createTreeNode(self, headers, row, parent_id, index):
        """
        Specific method for creating taxon tree node. 
        """

        rank = self.getTreeDefItem(headers[index])
        treedefitemid = str(rank['treeentries']).split('=')[1]
        name = row[headers[index]]
        rank_id = rank['rankid']
        
        # Generate full name when infrageneric 
        fullname = name
        if rank_id > 180:
            fullname = ''
            for r in reversed(self.TreeDefItems):
                if r['name'] in row:
                    fullname = row[r['name']] + ' ' + fullname
                if r['name'] == "Genus": 
                    break
            fullname = fullname.strip()

        # Add author if available
        author = ''
        if headers[index]+'Author' in row:
            author = row[headers[index]+'Author']
        
        # Create the taxon node object
        taxon_node = Taxon(0, name, fullname, author, parent_id, rank_id, treedefitemid, self.tree_definition)

        # TODO Handle synonymy 
        is_accepted = (row['isAccepted'] == 'Yes')        
        if not is_accepted and rank_id > 190:
            # Create as synonym node object 

            accepted_node = None
            # Species synonym 
            if rank_id == 220 and row.get('Subspecies') == '':
                # Accepted species
                if row.get('AcceptedSubspecies') == '':
                    accepted_node = Taxon(0,
                                          row['AcceptedSpecies'],
                                          row['Genus'] + ' ' + row['AcceptedSpecies'],
                                          row['AcceptedSpeciesAuthor'],
                                          parent_id, rank_id, treedefitemid, self.tree_definition)

                # Accepted subspecies
                elif row.get('AcceptedSubspecies') != '':
                    accepted_node = Taxon(0,
                                          row['AcceptedSubspecies'],
                                          row['Genus'] + ' ' + row['AcceptedSpecies'] + ' ' + row['AcceptedSubspecies'],
                                          row['AcceptedSpeciesAuthor'],
                                          parent_id, 230, treedefitemid, self.tree_definition)

            # Subspecies synonym 
            if rank_id == 230 and row.get('Subspecies') != '':
                # Accepted species
                if row['AcceptedSubspecies'] == '':
                    accepted_node = Taxon(0,
                                          row['AcceptedSpecies'],
                                          row['Genus'] + ' ' + row['AcceptedSpecies'],
                                          row['AcceptedSpeciesAuthor'],
                                          parent_id, rank_id, treedefitemid, self.tree_definition)
                    
                # Accepted subspecies
                elif row.get('AcceptedSubspecies') != '':
                    accepted_node = Taxon(0,
                                          row['AcceptedSubspecies'],
                                          row['Genus'] + ' ' + row['AcceptedSpecies'] + ' ' + row['AcceptedSubspecies'],
                                          row['AcceptedSpeciesAuthor'],
                                          parent_id, 230, treedefitemid, self.tree_definition)
            
            if accepted_node:
                
                # TODO Check if accepted taxon already exists
                pass

                if taxon_node.name == 'stenodactylus':
                    pass # TODO Debugging

                # Post the accepted taxon node to the API
                jsonString = accepted_node.createJsonString()
                sp7_obj = self.sp.postSpecifyObject(self.sptype, jsonString)

                # Adjust the synonym taxon accordingly 
                taxon_node.is_accepted = False
                taxon_node.accepted_taxon_id = sp7_obj['id']

        if taxon_node.name == 'stenodactylus':
            pass # TODO Debugging

        # Post the taxon node to the API
        jsonString = taxon_node.createJsonString()
        sp7_obj = self.sp.postSpecifyObject(self.sptype, jsonString)

        # Assign the ID from the API response
        taxon_node.id = sp7_obj['id']

        return taxon_node
  
    def createSynonymNode(self, headers, row, acc_node) -> None:
        """
        TODO: Add synonym node to tree
        """

        syn_name = row[headers[2]]
        full_name = row[headers[3]] + row[headers[2]]
        author = row[headers[3]]
        
        syn_node = Taxon(0, name = syn_name, 
                            fullname = full_name, 
                            taxon_author = author,
                            parent_id = acc_node['parent_id'], 
                            rank_id = acc_node['rank_id'], 
                            treedefitemid = acc_node['treedefitemid'], 
                            treedefid = self.tree_definition,
                            is_accepted=False,
                            accepted_taxon_id=acc_node['id'],
                            is_hybrid=False)

       


        pass

    def __str__(self) -> None:
        return "ImportSynonymTool"
