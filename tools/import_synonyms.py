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
    Tool for importing taxon synonyms into the Specify7 database. 
    """        

    def __init__(self, specifyInterface: specify_interface.SpecifyInterface) -> None:
        """
        
        """

        self.sptype = 'taxon'
        
        super().__init__(specifyInterface)
        
    def processRow(self, headers, row) -> None:
        """
        Process the data file row by adding its constituent taxa to the tree.
        """

        root = self.sp.getSpecifyObjects('taxon', limit=1)[0]
        
        taxon_headers = self.extractTaxonHeaders(headers)

        node = self.addChildNodes(taxon_headers, row, root['id'], 0)

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

        taxon_headers = self.extractTaxonHeaders(headers)

        valid = super().validateHeaders(taxon_headers)
        
        return valid

    def extractTaxonHeaders(self, headers):
        """
        Extracts the taxon headers from the given headers list.
        """
        taxon_headers = None
        index = headers.index('isAccepted')
        if index <= 0:
            return False

        taxon_headers = [header for header in headers[:index] if 'Author' not in header]

        return taxon_headers

    def addChildNodes(self, headers, row, parent_id, index) -> dict:
        """
        """
        return super().addChildNodes(headers, row, parent_id, index)

    def createTreeNode(self, headers, row, parent_id, index):
        """
        Specific method for creating taxon tree node. 
        """

        # Remove any "Accepted" prefix from header
        #if 'Accepted' in headers[index]:
        #    headers[index] = headers[index].replace('Accepted', '')

        rank = self.getTreeDefItem(headers[index].replace('Accepted', ''))
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
        
        if name != '':
            # Create the taxon node object
            taxon_node = Taxon(0, name, fullname, author, parent_id, rank_id, treedefitemid, self.tree_definition)

            # TODO Handle synonymy 
            is_accepted = (row.get('isAccepted') == 'Yes')        
            if not is_accepted and rank_id > 190:            
                # Create as synonym node object 
                accepted_node = None

                # Get synonym parent node (Genus)
                acc_parent = self.sp.getSpecifyObjects('taxon', limit=1, filters={'name': row['AcceptedGenus'], 'definition': self.tree_definition})
                if not acc_parent:
                    parent_id = self.createParentNode(row, parent_id, rank)
                else:
                    parent_id = acc_parent[0]['id']

                # Species synonym 
                if rank_id == 220 and not row.get('Subspecies'):
                    # ...to accepted species
                    if row.get('AcceptedSubspecies') == '' or row.get('AcceptedSubspecies') == None:
                        accepted_node = Taxon(0,
                                            row['AcceptedSpecies'],
                                            row['AcceptedGenus'] + ' ' + row['AcceptedSpecies'],
                                            row['AcceptedSpeciesAuthor'],
                                            parent_id, rank_id, treedefitemid, self.tree_definition)
                        pass
                    # ...to accepted subspecies
                    elif row.get('AcceptedSubspecies') != '':
                        accepted_node = Taxon(0,
                                            row['AcceptedSubspecies'],
                                            row['AcceptedGenus'] + ' ' + row['AcceptedSpecies'] + ' ' + row['AcceptedSubspecies'],
                                            row['AcceptedSubspeciesAuthor'],
                                            parent_id, 230, treedefitemid, self.tree_definition)
                        pass
                    else:
                        pass

                # Subspecies synonym 
                if rank_id == 230 and row.get('Subspecies') != '':
                    #pass
                    # Adjust taxon node to subspecies
                    taxon_node.rank = 230
                    taxon_node.name = row['Subspecies']
                    taxon_node.fullname = row['Genus'] + ' ' + row['Species'] + ' ' + row['Subspecies']
                    taxon_node.author = row['SubspeciesAuthor']
                    # TODO bump up header index ? 

                    # ...to accepted species
                    if row['AcceptedSubspecies'] == '':
                        accepted_node = Taxon(0,
                                            row['AcceptedSpecies'],
                                            row['AcceptedGenus'] + ' ' + row['AcceptedSpecies'],
                                            row['AcceptedSpeciesAuthor'],
                                            parent_id, rank_id, treedefitemid, self.tree_definition)
                        pass                    
                    # ...to accepted subspecies
                    elif row.get('AcceptedSubspecies') != '':
                        accepted_node = Taxon(0,
                                            row['AcceptedSubspecies'],
                                            row['AcceptedGenus'] + ' ' + row['AcceptedSpecies'] + ' ' + row['AcceptedSubspecies'],
                                            row['AcceptedSpeciesAuthor'],
                                            parent_id, 230, treedefitemid, self.tree_definition)
                        pass
                    else:
                        pass
                
                if accepted_node:
                    
                    # Check if accepted taxon already exists
                    spec_acc = self.sp.getSpecifyObject(self.sptype, accepted_node.id)

                    if not spec_acc:
                        double_check = self.sp.getSpecifyObjects(self.sptype, limit=1, 
                                                                filters={'name': accepted_node.name, 
                                                                        'fullname': accepted_node.fullname,
                                                                        'author': accepted_node.author,
                                                                        'parent': accepted_node.parent_id})
                        if double_check:
                            spec_acc = double_check[0]
                    
                    if spec_acc:
                        # If so, take over the accepted taxon id 
                        accepted_node.id = spec_acc['id']
                    else:
                        # Otherwise, post the accepted taxon node to the API
                        jsonString = accepted_node.createJsonString()
                        spec_acc = self.sp.postSpecifyObject(self.sptype, jsonString)

                    # Adjust the synonym taxon accordingly 
                    taxon_node.is_accepted = False
                    taxon_node.accepted_taxon_id = spec_acc['id']
            
            # Post the taxon node to the API
            jsonString = taxon_node.createJsonString()
            # TODO WTF is going wrong! Step through the code and find out!
            sp7_taxon = self.sp.postSpecifyObject(self.sptype, jsonString)

            # Assign the ID from the API response
            if sp7_taxon:
                taxon_node.id = sp7_taxon['id']
        else:
            taxon_node is None

        return taxon_node

    def createParentNode(self, row, parent_id, rank):
        # Create the parent node if it doesn't exist
        grand_parent_id = self.sp.getSpecifyObject('taxon', parent_id)['parent'].split('/')[4]

        str(rank['treeentries']).split('=')[1]
        genus_rank_id = str(self.getTreeDefItem('Genus')['treeentries']).split('=')[1]
        acc_parent_node = Taxon(0, row['AcceptedGenus'], row['AcceptedGenus'], '', grand_parent_id, 180, genus_rank_id, self.tree_definition)

        acc_parent = self.sp.postSpecifyObject('taxon', acc_parent_node.createJsonString())
            
        parent_id = acc_parent['id']

        return parent_id

    def __str__(self) -> None:
        return "ImportSynonymTool"
