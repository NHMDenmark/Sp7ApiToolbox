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
import traceback
import util

class ImportSynonymTool(TreeNodeTool):
    """
    Tool for importing taxon synonyms into the Specify7 database. 
    """        

    def __init__(self, specifyInterface: specify_interface.SpecifyInterface) -> None:
        self.sptype = 'taxon'
        super().__init__(specifyInterface)
        
    def processRow(self, headers, row) -> None:
        """
        Process the data file row by adding its constituent taxa to the tree.
        """
        try:
            root = self.sp.getSpecifyObjects('taxon', limit=1, filters={'definition': self.tree_definition})[0]
            taxon_headers = self.extractTaxonHeaders(headers)
            node = self.addChildNodes(taxon_headers, row, root['id'], 0)
            print(".", end='')
        except Exception as e:
            # Handle exceptions that may occur during processing
            util.logger.debug(f"Error processing row: {row}. Exception: {e}")   
            traceback.print_exc()

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
            print("Validation Failed: The 'isAccepted' header is missing from the file.")
            return False

        taxon_headers = self.extractTaxonHeaders(headers)

        # Check if the higher taxonomy above family is present
        rank_names = {item['name']: item for item in self.TreeDefItems}        
        for rank in rank_names:
            if rank == 'Life': continue
            if rank == 'Family': break
            if rank not in taxon_headers:
                print(f"Validation failed: The header '{rank}' is missing from the file.")
                util.logger.debug(f"Validation failed: The header '{rank}' is missing from the file.")
                return False

        valid = super().validateHeaders(taxon_headers)
        
        return valid

    def extractTaxonHeaders(self, headers):
        """
        Extracts the taxon headers from the given headers list.
        """
        
        index = headers.index('isAccepted')
        if index <= 0:
            return False

        taxon_headers = [header for header in headers[:index] if 'Author' not in header and 'TaxonKey' not in header]

        return taxon_headers

    def addChildNodes(self, headers, row, parent_id, index, filters={}) -> dict:
        """
        """
        if index >= len(headers):
            return None  # No more headers to process

        filters = {}
        full_name = self.generateFullname(row, headers, index)
        if row.get(headers[index] + 'Author'): 
            author = row.get(headers[index] + 'Author').strip()
            filters['author'] = author
        filters['fullname'] = full_name
        filters['rankid'] = self.getTreeDefItem(headers[index])['rankid']

        return super().addChildNodes(headers, row, parent_id, index, filters)

    def createTreeNode(self, headers, row, parent_id, index):
        """
        Specific method for creating taxon tree node.
        
        Parameters:
        headers (list): List of header names.
        row (dict): Dictionary containing row data.
        parent_id (int): ID of the parent node.
        index (int): Index of the current header.
        
        Returns:
        Taxon: The created taxon node.
        """

        rank = self.getTreeDefItem(headers[index].replace('Accepted', ''))
        if headers[index] not in rank['name']:
            return None
        else:
            treedefitemid = str(rank['treeentries']).split('=')[1]
            name = row[headers[index]].strip()
            rank_id = rank['rankid']
            
            # Generate full name
            fullname = self.generateFullname(row, headers, index, rank_id)

            # Add author if available
            author = row.get(headers[index] + 'Author', '').strip()
            
            if not name:
                return None

            # Create the taxon node object
            taxon_node = Taxon(0, name, fullname, author, parent_id, rank_id, treedefitemid, self.tree_definition)

            # Handle synonymy 
            if row.get('isAccepted') == 'No' or row.get('isAccepted') == 'Yes':
                is_accepted = not (row.get('isAccepted') == 'No')
                if not is_accepted and rank_id > 190:
                    spec_acc = self.getOrCreateAcceptedTaxon(row, headers, index, rank_id, parent_id)
                    if spec_acc:
                        taxon_node.is_accepted = False
                        taxon_node.accepted_taxon_id = spec_acc['id']
                    else:
                        print(f"Error creating accepted taxon for {name}")
                        return None
            else:
                raise ValueError(f"Invalid value for 'isAccepted': {row.get('isAccepted')} in row {row}")

            # Handle taxon key and source
            taxon_key = row.get(headers[index] + 'TaxonKey', '').strip()
            taxon_key_source = row.get(headers[index] + 'TaxonKeySource', '').strip()
            if taxon_key:
                taxon_node.taxon_key = taxon_key
            if taxon_key_source:
                taxon_node.taxon_key_source = taxon_key_source

            # TODO Handle hybrid taxa
            if row.get('isHybrid') == 'Yes':
                taxon_node.is_hybrid = True

            # Double check if the taxon already exists
            matching_taxa = self.sp.getSpecifyObjects(self.sptype, limit=1, filters={
                'fullname': taxon_node.fullname,
                'rankid': taxon_node.rank,
                'author': taxon_node.author,
                'parent': parent_id,
                'definition': self.tree_definition
            })

            if not matching_taxa:

                # # Check if parent is a synonym                
                # # TODO How can I make Specify7 add a infraspecific taxon to a parent that is a synonym? 
                # # TODO Apparently by adding the following setting to Specify7 Remote Preferences:
                # #      sp7.allow_adding_child_to_synonymized_parent.Taxon=true
                # #      https://discourse.specifysoftware.org/t/enable-creating-children-for-synonymized-nodes/987 
                # parent_is_synonym = False
                # parent_node = self.sp.getSpecifyObject(self.sptype, parent_id)
                # if parent_node['isaccepted'] is False:
                #     parent_is_synonym = True
                #     # If parent is a synonym, use its accepted taxon ID
                #     taxon_node.parent_id = parent_node['acceptedtaxon'].split('/')[4]
                    
                #     # Circumvent business logic rule that prevents adding synonym children to a synonym
                #     parent_json = self.sp.getSpecifyObject(self.sptype, parent_node['id']) 
                #     parent_taxon = Taxon()
                #     parent_taxon.fill(parent_json)
                #     parent_taxon.is_accepted = True
                #     parent_taxon_accepted_taxon_id = taxon_node.parent_id #parent_taxon.accepted_taxon_id
                #     res = self.sp.putSpecifyObject(self.sptype, parent_taxon.id, parent_taxon.createJsonString())
                # else:
                #     pass

                # Add taxon key and taxon key source to the taxon node
                taxon_node.taxon_key = row.get(headers[index] + 'TaxonKey', None)
                if taxon_node.taxon_key == '': taxon_node.taxon_key = None
                taxon_node.taxon_key_source = row.get(headers[index] + 'TaxonKeySource', None)
                if taxon_node.taxon_key_source == '': taxon_node.taxon_key_source = None

                # Ensure empty string fields are set to None
                if taxon_node.author == '': taxon_node.author = None

                # Create the taxon node in Specify7
                jsonString = taxon_node.createJsonString()
                sp7_taxon = self.sp.postSpecifyObject(self.sptype, jsonString)

                # if parent_is_synonym:
                #     # If the parent was a synonym, we need to reinstate it as a synonym
                #     parent_taxon.is_accepted = False
                #     parent_taxon.accepted_taxon_id = parent_taxon_accepted_taxon_id 
                #     parent_taxon.version = parent_taxon.version + 1
                #     res = self.sp.putSpecifyObject(self.sptype, parent_taxon.id, parent_taxon.createJsonString())
            else:
                # If the taxon already exists, use the existing one
                sp7_taxon = matching_taxa[0]

            if sp7_taxon:
                taxon_node.id = sp7_taxon['id']

        return taxon_node

    def generateFullname(self, row, headers, index, rank_id=None):
        """
        Generate the full name for the taxon node.
        """

        header = headers[index]
        accepted = 'Accepted' if 'Accepted' in header else ''

        # Determine rank_id if not provided
        if not rank_id and index < len(headers):
            base_header = header.replace('Accepted', '')
            rank_id = self.getTreeDefItem(base_header)['rankid']

        # Define templates for each rank
        templates = {
            220: "{genus}{subgenus} {species}",
            230: "{genus}{subgenus} {species} {subspecies}",
            240: "{genus}{subgenus} {species} var. {variety}",
            250: "{genus}{subgenus} {species} subvar. {subspecies}",
            260: "{genus}{subgenus} {species} forma {forma}",
            270: "{genus}{subgenus} {species} subforma {subforma}",
        }

        # Prepare values
        genus = row.get(f"{accepted}Genus", "").strip()
        subgenus = f" {row.get(f'{accepted}Subgenus', '').strip()}" if row.get(f"{accepted}Subgenus") else ""
        species = row.get(f"{accepted}Species", "").strip()
        subspecies = row.get(f"{accepted}Subspecies", "").strip()
        variety = row.get(f"{accepted}Variety", "").strip()
        forma = row.get(f"{accepted}Forma", "").strip()
        subforma = row.get(f"{accepted}Subforma", "").strip()

        # Select template or fallback
        if rank_id in templates:
            fullname = templates[rank_id].format(
                genus=genus,
                subgenus=subgenus,
                species=species,
                subspecies=subspecies,
                variety=variety,
                forma=forma,
                subforma=subforma
            )
        else:
            fullname = row.get(header, "").strip()

        return fullname.strip()

    def createAcceptedNode(self, row, acc_rank_id, treedefitemid, parent_id):
        """
        Create the accepted node for the synonym.
        """
        accepted_node = Taxon(0, '', '', '', 0, acc_rank_id, treedefitemid, self.tree_definition)

        if acc_rank_id == 220:
            # Species rank accepted name
            accepted_node.name = row['AcceptedSpecies'].strip()
            accepted_node.fullname = f"{row['AcceptedGenus'].strip()} {row['AcceptedSpecies'].strip()}"
            accepted_node.author = row['AcceptedSpeciesAuthor'].strip()
            accepted_node.parent = row['AcceptedGenus'].strip()
            accepted_node.taxon_key = row.get('AcceptedSpeciesTaxonKey', None)
            accepted_node.taxon_key_source = row.get('AcceptedSpeciesTaxonKeySource', None)
            subgenus = f" {row['Subgenus'].strip()}" if row.get('Subgenus') else ''
            parent_rank_name = 'Genus' if subgenus == '' else 'Subgenus'
            grandparent_id = self.getGrandParentId(parent_id)
        elif acc_rank_id == 230:
            # Subspecies rank accepted name
            accepted_node.name = row['AcceptedSubspecies'].strip()
            accepted_node.fullname = f"{row['AcceptedGenus'].strip()} {row['AcceptedSpecies'].strip()} {row['AcceptedSubspecies'].strip()}"
            accepted_node.author = row['AcceptedSubspeciesAuthor'].strip()
            accepted_node.parent = row['AcceptedGenus'].strip() + ' ' + row['AcceptedSpecies'].strip()
            accepted_node.taxon_key = row.get('AcceptedSubspeciesTaxonKey', None)
            accepted_node.taxon_key_source = row.get('AcceptedSubspeciesTaxonKeySource', None)
            parent_rank_name = 'Species'
            grandparent_id = parent_id  # Subspecies parent is the species 
        elif acc_rank_id == 240:
            # Variety rank accepted name
            accepted_node.name = row['AcceptedVariety'].strip()
            accepted_node.fullname = f"{row['AcceptedGenus'].strip()} {row['AcceptedSpecies'].strip()} var. {row['AcceptedVariety'].strip()}"
            accepted_node.author = row['AcceptedVarietyAuthor'].strip()
            accepted_node.parent = row['AcceptedGenus'].strip() + ' ' + row['AcceptedSpecies'].strip()
            accepted_node.taxon_key = row.get('AcceptedVarietyTaxonKey', None)
            accepted_node.taxon_key_source = row.get('AcceptedVarietyTaxonKeySource', None)
            parent_rank_name = 'Species'
            grandparent_id = parent_id  # Variety parent is the species
        elif acc_rank_id == 250:
            # Subvariety rank accepted name
            accepted_node.name = row['AcceptedSubvariety'].strip()
            accepted_node.fullname = f"{row['AcceptedGenus'].strip()} {row['AcceptedSpecies'].strip()} subvar. {row['AcceptedSubvariety'].strip()}"
            accepted_node.author = row['AcceptedSubvarietyAuthor'].strip()
            accepted_node.parent = row['AcceptedGenus'].strip() + ' ' + row['AcceptedSpecies'].strip()
            accepted_node.taxon_key = row.get('AcceptedSubvarietyTaxonKey', None)
            accepted_node.taxon_key_source = row.get('AcceptedSubvarietyTaxonKeySource', None)
            parent_rank_name = 'Species'
            grandparent_id = parent_id  # Subvariety parent is the species
        elif acc_rank_id == 260:
            # Forma rank accepted name
            accepted_node.name = row['AcceptedForma'].strip()
            accepted_node.fullname = f"{row['AcceptedGenus'].strip()} {row['AcceptedSpecies'].strip()} forma {row['AcceptedForma'].strip()}"
            accepted_node.author = row['AcceptedFormaAuthor'].strip()
            accepted_node.parent = row['AcceptedGenus'].strip() + ' ' + row['AcceptedSpecies'].strip()
            accepted_node.taxon_key = row.get('AcceptedFormaTaxonKey', None)
            accepted_node.taxon_key_source = row.get('AcceptedFormaTaxonKeySource', None)
            parent_rank_name = 'Species'
            grandparent_id = parent_id  # Forma parent is the species
        elif acc_rank_id == 270:
            # Subforma rank accepted name
            accepted_node.name = row['AcceptedSubforma'].strip()
            accepted_node.fullname = f"{row['AcceptedGenus'].strip()} {row['AcceptedSpecies'].strip()} subforma {row['AcceptedSubforma'].strip()}"
            accepted_node.author = row['AcceptedSubformaAuthor'].strip()
            accepted_node.parent = row['AcceptedGenus'].strip() + ' ' + row['AcceptedSpecies'].strip()
            accepted_node.taxon_key = row.get('AcceptedSubformaTaxonKey', None)
            accepted_node.taxon_key_source = row.get('AcceptedSubformaTaxonKeySource', None)
            parent_rank_name = 'Species'
            grandparent_id = parent_id  # Subforma parent is the species    
        
        # Ensure empty string fields are set to null
        if accepted_node.author == '': accepted_node.author = None
        if accepted_node.taxon_key == '': accepted_node.taxon_key = None
        if accepted_node.taxon_key_source == '': accepted_node.taxon_key_source = None

        # Get or create the parent node using only row, parent_rank_name, and grandparent_id
        parent_node = self.getOrCreateParentNode(row, parent_rank_name, grandparent_id)
        if parent_node:
            accepted_node.parent_id = parent_node['id']
            accepted_node.getParent(self.sp)

        return accepted_node
    
    def getGrandParentId(self, parent_id): 
        """
        Get the grandparent ID for the accepted taxon.
        """
        parent = self.sp.getSpecifyObject('taxon', parent_id)
        if parent and 'parent' in parent:
            grandparent_id = parent['parent'].split('/')[4]
            return grandparent_id
        return 0

    def getOrCreateParentNode(self, row, parent_rank_name, grandparent_id):
        """
        Get or create the parent node using only the row, parent rank name, and grandparent id.
        """
        #parent_name = row.get(f'Accepted{parent_rank_name}', '').strip()
        parent_fullname = self.generateFullname(row, [f'Accepted{parent_rank_name}'], 0)
        #parent_author = row.get(f'Accepted{parent_rank_name}Author', '').strip()
        parent_rank_id = self.getTreeDefItem(parent_rank_name)['rankid']

        acc_parent = self.sp.getSpecifyObjects(
            'taxon',
            limit=1,
            filters={
                'fullname': parent_fullname,
                'rankid': parent_rank_id,
                'definition': self.tree_definition
            }
        )
        if not acc_parent:
            return self.createParentNode(row, parent_rank_name, grandparent_id)
        return acc_parent[0]

    def createParentNode(self, row, parent_rank_name, grandparent_id):
        """
        Create the parent node if it doesn't exist, extracting all info from the row.
        """
        parent_name = row.get(f'Accepted{parent_rank_name}', '').strip()
        parent_fullname = self.generateFullname(
            row,
            [f'Accepted{parent_rank_name}'],
            0,
            self.getTreeDefItem(parent_rank_name)['rankid']
        )
        parent_author = row.get(f'Accepted{parent_rank_name}Author', '').strip()
        parent_rank_id = self.getTreeDefItem(parent_rank_name)['rankid']
        parent_treedefitem_id = str(self.getTreeDefItem(parent_rank_name)['treeentries']).split('=')[1]
        taxon_key = row.get(f'Accepted{parent_rank_name}TaxonKey', '').strip()
        taxon_key_source = row.get(f'Accepted{parent_rank_name}TaxonKeySource', '').strip()

        acc_parent_node = Taxon(
            0,
            parent_name,
            parent_fullname,
            parent_author,
            grandparent_id,
            parent_rank_id,
            parent_treedefitem_id,
            self.tree_definition,
            taxon_key=taxon_key,
            taxon_key_source=taxon_key_source
        )

        acc_parent = self.sp.postSpecifyObject('taxon', acc_parent_node.createJsonString())
        parent_id = acc_parent['id'] if acc_parent else grandparent_id
        parent_node = self.sp.getSpecifyObject('taxon', parent_id)
        return parent_node
    
    def getOrCreateAcceptedTaxon(self, row, headers, index, rank_id, parent_id):
        """
        TODO Get or create the accepted taxon.
        """
        
        # Determine the rank of the accepted name
        acc_rank_id = rank_id
        if row.get('AcceptedSubforma') != '' and row.get('AcceptedSubforma') is not None:
            acc_rank_id = 270
            treedefitemid = str(self.getTreeDefItem('Subforma')['treeentries']).split('=')[1]
        elif row.get('AcceptedForma') != '' and row.get('AcceptedForma') is not None:
            acc_rank_id = 260
            treedefitemid = str(self.getTreeDefItem('Forma')['treeentries']).split('=')[1]
        elif row.get('AcceptedSubvariety') != '' and row.get('AcceptedSubvariety') is not None: 
            acc_rank_id = 250
            treedefitemid = str(self.getTreeDefItem('Subvariety')['treeentries']).split('=')[1]
        elif row.get('AcceptedVariety') != '' and row.get('AcceptedVariety') is not None: 
            acc_rank_id = 240
            treedefitemid = str(self.getTreeDefItem('Variety')['treeentries']).split('=')[1]
        elif row.get('AcceptedSubspecies') != '' and row.get('AcceptedSubspecies') is not None:   
            acc_rank_id = 230
            treedefitemid = str(self.getTreeDefItem('Subspecies')['treeentries']).split('=')[1]
        elif row.get('AcceptedSpecies') != '' and row.get('AcceptedSpecies') is not None: 
            acc_rank_id = 220
            treedefitemid = str(self.getTreeDefItem('Species')['treeentries']).split('=')[1]
        else:
            print(f"Error: No accepted name found for {row[headers[index]]}.")
            raise Exception("No accepted name found for the taxon.")
            
        accepted_node = self.createAcceptedNode(row, acc_rank_id, treedefitemid, parent_id)
        filters = {
            'name': accepted_node.name,
            'fullname': accepted_node.fullname,
            'parent': accepted_node.parent.id
        }
        if accepted_node.author:
            filters['author'] = accepted_node.author
        check_acc = self.sp.getSpecifyObjects(self.sptype, limit=1, filters=filters)

        if check_acc:
            accepted_node.id = check_acc[0]['id']
            spec_acc = check_acc[0]
        else:            
            jsonString = accepted_node.createJsonString()
            spec_acc = self.sp.postSpecifyObject(self.sptype, jsonString)
        return spec_acc

    def __str__(self) -> None:
        return "ImportSynonymTool"