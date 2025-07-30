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

  PURPOSE: Tool for merging duplicate taxa in Specify7 based on primary keys provided in data file and then based on similar full name, author and parent.
"""

import os
import time
import traceback
import datetime

from tools.sp7api_tool import Sp7ApiTool

import util
import GBIF_interface
import global_settings as app

from models import taxon
from models import collection as col
from models import discipline as dsc

class MergeDuplicateTaxaTool(Sp7ApiTool):
    """
    Tool for merging duplicate taxa in Specify7.
    """

    def __init__(self, args) -> None:
        """
        Initialize the tool with necessary arguments.
        """
        self.sptype = 'taxon'
        
        # Initialize parent class
        super().__init__(args)

        # Prepare variable base values  
        self.resultCount = -1    
        self.batchSize = 1000
        self.ambivalentCases = []
        
        self.gbif = GBIF_interface.GBIFInterface()
        #self.dx = data_exporter.DataExporter()
        #db = data_access.DataAccess('db')

    def runTool(self, args):
        """
        
        """
        #super().initialize()

        print("Running MergeDuplicateTaxaTool...")
        print("Arguments: ", args)
        print("specifyAPI token:", self.sp.csrfToken)
        print("Collection Id:", self.collection.id)
        print("Discipline Id:", self.collection.discipline.id)
        print("Taxon tree def id:", self.collection.discipline.taxontreedefid)
        
        self.printLegend()

        #self.handleQualifiedTaxa()

        filename = args.get('filename')
        if filename: self.checkPrecollectedTaxa(filename)
        
        print()
        print('(Proceeding with general scan)')

        self.scan()
        print('Scan complete!')
        
        self.SaveAmbivalentCases()
        
        print('----------------------------------')

    def checkPrecollectedTaxa(self, filename):
        """
        Function for going through list of collection taxon ids that are likely to have duplicates to be merged.  
        The list is retrieved from a simple text file with a taxon id for each line. 
        The text file itself is based on the results of a query joining taxa on fullname (GetTaxonDuplicates.sql in 'sql' folder). 
        """
        util.logger.info('**** Checking pre-collected taxon ids ****')
        
        try:
            if not os.path.isfile(f'data/{filename}'):
                raise Exception(f"File {filename} does not exist.")
            
            idList = open(f'data/{filename}', 'r')
            taxonIds = idList.readlines()  

            if len(taxonIds) > 0:
                print(f'Checking {len(taxonIds)} pre-collected taxa...')
                for taxonId in taxonIds: 
                    taxonId = int(taxonId)
                    #print(f'Fetching taxon with id: {taxonId}')
                    specifyTaxon = self.sp.getSpecifyObject('taxon', int(taxonId))
                    if specifyTaxon:
                        # If 
                        self.handleSpecifyTaxon(specifyTaxon)
                    else:
                        print('#', end='') #[Could not retrieve taxon]   
            else:
                print('No taxon ids found in the file...')
                util.logger.info('No taxon ids found in the file...')
                
        except Exception as e:
            # Handle any exceptions that occur during the process  
            util.logger.error(f'Error opening file "{filename}"...')
            util.logger.error(e)
            #print(f'An error occurred while processing the file with precollected taxon ids... ({filename})')
            print('@', end='') # output token to indicate error 

    def scan(self):
        """
        Function for scanning and iterating taxa retrieved from the Specify API in batches per taxon rank.         
        """
        
        util.logger.info(f'Scanning {self.collection.id}  ...')

        taxontreedefid = self.collection.discipline.taxontreedefid

        # Fetch taxon ranks from selected collection's discipline taxon tree 
        taxonranks = self.sp.getSpecifyObjects('taxontreedefitem', 100, 0, {"treedef":str(taxontreedefid)})

        taxonranks_reversed = taxonranks[::-1]  # Reverse the order of the ranks

        # Iterate taxon ranks for analysis
        for rank in taxonranks_reversed:
            # Extract rank id & display 
            rankId = int(rank['rankid'])
            rankName = str(rank['name'])
            util.logger.info(f'RANK "{rankName}" ({rankId})')
            print(f'<{rankId}>', end='')  # Handling taxon

            # Only look at ranks below genera 
            if rankId >= 180:
                offset = 0
                resultCount = -1
                while resultCount != 0:
                    # Fetch batches from API
                    util.logger.info(f'Fetching batch with offset: {offset}')
                    batch = self.sp.getSpecifyObjects('taxon', self.batchSize, offset, {'definition':taxontreedefid, 'rankid':f'{rankId}'})
                    resultCount = len(batch)

                    util.logger.info(f' - Fetched {resultCount} taxa')

                    # Iterate taxa in batch 
                    for specifyTaxon in batch:
                        try:
                            t = taxon.Taxon(self.collection.id)
                            t.fill(specifyTaxon)
                            self.resolveAuthorName(t)
                            self.handleSpecifyTaxon(specifyTaxon)
                        except Exception as e:
                            # Handle any exceptions that occur during the process  
                            util.logger.error(f'Error handling taxon "{specifyTaxon.get("fullname", "<unknown>")}"...')
                            util.logger.error(e)
                            util.logger.error(traceback.format_exc())
                            print('@', end='') # output token to indicate error 

                    # Prepare for fetching next batch, by increasing offset with batchsize 
                    offset += self.batchSize

    def SaveAmbivalentCases(self):
        """
        Function for saving ambivalent cases to file 
        """
        # Handle Ambivalent cases: Save & export to file 
        util.logger.info('Handle ambivalent cases...')
        print('Saving ambivalent cases to file...')

        try:    
            f = open(f'output/merge_ambivalent_cases_{datetime.datetime.now().strftime("%Y%m%d%H%M")}.csv', 'a', encoding='utf-8') 

            if self.ambivalentCases:
                f.write(self.ambivalentCases[0].get_headers() + '\n')
                seen_cases = set()
                for case in self.ambivalentCases: 
                    util.logger.info(f' - Ambivalent case: {case}')
                    if str(case) not in seen_cases:
                        seen_cases.add(str(case))
                        util.logger.info('   * Writing ambivalent case to file')
                        f.write(f'{case}\n')
                    else:
                        util.logger.info(f'   * Duplicate case: {case} already seen...')
            else:
                util.logger.info('No ambivalent cases found...')
                print('No ambivalent cases found...')
        except Exception as e:
            # Handle any exceptions that occur during the process  
            util.logger.error(f'Error writing ambivalent cases to file...')
            util.logger.error(e)
            print('An error occurred while writing ambivalent cases to file...')
        finally:
            f.close()

    def handleSpecifyTaxon(self, specifyTaxon):
        """
        Handle Specify taxon json object through the following steps: 
          - Create taxon model object instance
          - Look up possible duplicates at Specify7 API 
          - Performing merge of any unambiguous duplicates after updating author info if needed 
          - Recording any ambivalent cases
        """

        try:
            print('◘', end='')  # Handling taxon 
            specifyTaxonId = specifyTaxon['id']
            print(f'[{specifyTaxonId}]', end='')  # Handling taxon 
            # Create local taxon instance from original Specify taxon data 
            original = taxon.Taxon(self.collection.id)
            original.fill(specifyTaxon)
            #original.parent.fill(self.sp.getSpecifyObject(self.sptype, original.parentId))
            original.getParent(self.sp)
            fullname = original.fullname#.replace(' ','%20')
            rankId = original.rank

            util.logger.info(f'Handling taxon {fullname} [{specifyTaxonId}] of rank {rankId}')
            
            # Look up taxa with matching fullname & rank
            taxonLookup = self.sp.getSpecifyObjects('taxon', 100000, 0, 
                {'definition':str(self.collection.discipline.taxontreedefid), 'rankid':f'{rankId}', 'fullname':f'{fullname}'}) #, 'parent':f'{original.parentid}'})
            
            if original.fullname == 'Draba incana':
                pass

            # If more than one result is returned, there will be duplicates 
            if len(taxonLookup) > 1:
                util.logger.info('Potential duplicates detected...')
                # Iterate taxa with identical names to original                             
                for tl in taxonLookup:
                    # Create local taxon instance from looked up Specify taxon data 
                    lookup = taxon.Taxon(self.collection.id)
                    lookup.fill(tl)
                    #lookup.parent.fill(self.sp.getSpecifyObject(self.sptype, lookup.parentId))
                    lookup.getParent(self.sp)

                    # If the looked up taxon isn't the same record (as per 'id') then treat as potential duplicate 
                    # NOTE We need to compare the Specify id ('id') and not the local id, which is always 0 until saved
                    if lookup.id != original.id:
                        
                        # If the parents match then treat as duplicate 
                        if lookup.parent_id == original.parent_id:
                            self.handleDuplicate(original, lookup)
                        else:
                            # Found taxa with matching names, but different parents: Add to ambivalent cases 
                            ambivalence = f'Ambivalence on parent taxa: {original.parent.fullname} [{original.parent.id}] vs {lookup.parent.fullname} [{lookup.parent.id}] '
                            util.logger.info(ambivalence)
                            original.remarks = str(original.remarks) + f' | {ambivalence}'
                            original.duplicateid = lookup.id
                            self.ambivalentCases.append(original)
                            lookup.remarks = str(lookup.remarks) + f' | {ambivalence}'
                            lookup.duplicateid = original.id
                            self.ambivalentCases.append(lookup)
                            print('¿', end='')

                            # Attempt to resolve parentage and move duplicate taxon to certified parent
                            criterium1 = self.resolveParentTaxon(original)
                            criterium2 = self.resolveParentTaxon(lookup) 

                            if criterium1 and criterium2:
                                # If both taxa have been moved, then treat as duplicate 
                                self.handleDuplicate(original, lookup)
            else:
                util.logger.info(f'Duplicate {fullname} no longer found! (Original taxon Specify id: {original.id})')
                print('x', end='') # Duplicate no longer found 
        except Exception as e:
            # Handle any exceptions that occur during the process  
            util.logger.error(f'Error handling taxon "{specifyTaxon["fullname"]}"...')
            util.logger.error(e)
            print('@', end='') # output token to indicate error  
    
    def handleDuplicate(self, original, lookup):
        """

        """
        print('!', end='') # possible duplicate hit! 
        util.logger.info('Duplicate detected!')
        util.logger.info(f' - original : "{original}"')
        util.logger.info(f' - duplicate : "{lookup}"')
        
        # Reset variables for weighting the two candidates for merging 
        originalWeight  = 0
        duplicateWeight = 0

        # If original author is empty, but lookup author isn't, then weight lookup higher
        if original.author == None and lookup.author is not None: 
            duplicateWeight += 1
        else:
            originalWeight += 1
        
        # Weight according to ID number (lower is better)
        if original.id < lookup.id:
            originalWeight += 1
        else:
            duplicateWeight += 1

        # Weight according to number of children (higher is better)
        original_childcount = original.getChildCount(self.sp)
        lookup_childcount = lookup.getChildCount(self.sp)
        if original_childcount > lookup_childcount:
            originalWeight += 1
        else:
            if original_childcount != lookup_childcount:
                duplicateWeight += 1
        
        # TODO more weighting rules ? 
        
        # If both original and lookup contain author data and the author is not identical, 
        #   retrieve authorship from GBIF 
        unResolved = self.resolveAuthorNames(original, lookup)

        if unResolved and (original.author is None and lookup.author is None):
            pass # ??? 

        if unResolved:
        # If authorship could not be resolved, add to ambivalent cases 
            ambivalence = f'Ambivalence on authors: {original.author} vs {lookup.author} '
            util.logger.info(ambivalence)
            original.remarks = str(original.remarks) + f' | {ambivalence}'
            original.duplicateid = lookup.id
            self.ambivalentCases.append(original)
            lookup.remarks = str(lookup.remarks) + f' | {ambivalence}'
            lookup.duplicateid = original.id
            self.ambivalentCases.append(lookup)
            print('?', end='')
        else: 
            # Prepare for merging by resetting target & source before evaluation 
            target = None
            source = None
            # Determine target and source taxon record as based on weighting 
            if duplicateWeight > originalWeight: 
                # Prefer looked up duplicate over original 
                target = lookup
                source = original 
            else: 
                # Prefer original 
                target = original
                source = lookup 

            # Output token to indicate merging of taxa 
            print('*', end='')

            self.mergeTaxa(source, target)

    def mergeTaxa(self, source, target):
        """
        TODO Function contract 
        """
        if target is not None and source is not None: 
            # Stop latch for user interaction (disabled)
            if True: # input(f'Do you want to merge {source.id} with {target.id} (y/n)?') == 'y':
                # Do the actual merging 
                print(f'|{source.id}->{target.id}|', end='')
                print('{', end='')
                start = time.time()
                response = self.sp.mergeTreeNodes(self.sptype, source.id, target.id)
                if response.status_code == "404":
                    util.logger.info(' - 404: Taxon already merged.')
                elif response.status_code == "500":
                    util.logger.info(' - 500: Internal Server Error.')
                    print('@', end= '')
                end = time.time()
                timeElapsed = end - start
                print(round(timeElapsed, 2), end='}')
                util.logger.info(f'Merged {source.id} with {target.id}; Time elapsed: {timeElapsed} ')

    def resolveAuthorNames(self, original, lookup):
        # If both original and lookup contain author data and the author is not identical, 
        #   retrieve authorship from GBIF 
        unResolved = True 
        if (original.author != lookup.author) and (original.author is not None or lookup.author is not None) and (original.author != '' or lookup.author != ''): # and (original.author is not None and lookup.author is not None): 
            #util.logger.info('Both original and lookup contain author data and the author is not identical! ')
            util.logger.info('Original author and lookup author are not identical and neither is empty!')
            util.logger.info('Retrieving authorship from GBIF...')
            
            criterium1 = self.resolveAuthorName(original)
            criterium2 = self.resolveAuthorName(lookup)
            unResolved = criterium1 and criterium2 
        else:
            if (original.author is None and lookup.author is None):
                util.logger.info('Author info is missing...')
                # Update authorname at Specify also 
                criterium1 = self.resolveAuthorName(original)
                criterium2 = self.resolveAuthorName(lookup)
                unResolved = criterium1 and criterium2

                # TODO Forcing through merge if both author names are empty
                if unResolved:
                    print('¤', end='')
                    unResolved = False
            else:
                util.logger.info('Original and lookup have no author data or the author is identical. ')
                unResolved = False  
        
        return unResolved
            
    def resolveAuthorName(self, taxonInstance):
        """
        Method for resolve the author name of a given taxon class instance by consulting the GBIF API 
        CONTRACT 
            taxonInstance (taxon.Taxon) : Taxon class instance for which the author should be resolved
        RETURNS boolean : Flag to indicate whether the resolution was succesful 
        """
        util.logger.info('Resolving author name...')
        acceptedNameMatches = self.gbif.matchName('species', taxonInstance.fullname, self.collection.id, 'Plantae')
        nrOfMatches = len(acceptedNameMatches)
        
        # Check whether any multiple GBIF name matches are identical to each other
        if nrOfMatches > 1:
            sameAcceptedName = self.checkNameMatches(taxonInstance, acceptedNameMatches)
        else: sameAcceptedName = False # To make sure the boolean is initalized 

        if nrOfMatches == 1 or sameAcceptedName:
            util.logger.info('Retrieved unambiguous accepted name from GBIF...')
            # Update the authorname at Specify 
            res = self.updateSpecifyTaxonAuthor(taxonInstance, acceptedNameMatches[0]['authorship'])
            if res != '500':
                unResolved = False
            else:
                unResolved = True
        else:
            util.logger.info(f'Could not retrieve unambiguous accepted name from GBIF... ({nrOfMatches} matches)')
            unResolved = True
        return unResolved
    
    def checkNameMatches(self, taxonInstance, acceptedNameMatches):
        """
        Method for checking whether multiple GBIF name matches are identical to each other
        CONTRACT 
            taxonInstance (taxon.Taxon) : Taxon class instance for which the author should be resolved
            acceptedNameMatches (list) : List of GBIF name matches        
        """
        
        same_AcceptedName = False
        last_nub_key = acceptedNameMatches[0]['nubKey']
        for match in acceptedNameMatches:
            # Check if the author name in the match is identical to the taxon instance's author name
            if match['nubKey'] == last_nub_key:
                same_AcceptedName = True
            else:
                same_AcceptedName = False 

        return same_AcceptedName

    def resolveParentTaxon(self, taxonInstance):
        """
        Method for resolve the parent taxon of a given taxon class instance by consulting the GBIF API 
        CONTRACT 
            taxonInstance (taxon.Taxon) : Taxon class instance for which the parent taxon should be resolved
        RETURNS boolean : Flag to indicate whether the resolution was succesful 
        """
        util.logger.info('Resolving parent taxon...')
        success = False

        # Get taxon's currently set parent from Specify
        currentParent = self.sp.getSpecifyObject('taxon', taxonInstance.parent.id)
        if currentParent is not None: 
            currentParentName = currentParent['fullname']
            util.logger.info(f'Checking current parent taxon: {currentParentName} ')
            # Get taxon's certified parent name from GBIF 
            matches = self.gbif.matchName('species', taxonInstance.fullname, self.collection.id, 'Plantae')
            if len(matches) >= 1:
                # Found parent name match in GBIF 
                match = matches[0]

                parentName = ''                
                if match['rank'] == "SUBSPECIES":
                    parentName = match['species']
                elif match['rank'] == "SPECIES":
                    parentName = match['genus']
                elif match['rank'] == "GENUS":
                    parentName = match['family']
                elif match['rank'] == "FAMILY":
                    parentName = match['order']
                elif match['rank'] == "ORDER":
                    parentName = match['class']            
                if parentName == '': 
                    util.logger.error(f'Error retrieving parent taxon to "{taxonInstance.fullname}" from GBIF...')
                    print('@', end='') # output token to indicate issue with retrieving parent 
                else: 
                    util.logger.info(f'Retrieved GBIF certified parent taxon match: {parentName} ')

                # Check if GBIF certified parent taxon name differs from current parent taxon name  
                if parentName != currentParent['fullname']:
                    # Get certified (target) parent taxon from Specify 
                    parentLookup = self.sp.getSpecifyObjects('taxon', 10, 0, {'fullname':f'{parentName}','definition':'13'})
                    
                    if len(parentLookup) > 0:
                        # Instantiate parent taxon from Specify record 
                        targetParent = taxon.Taxon(self.collection.id)
                        targetParent.fill(parentLookup[0])

                        # Output token to indicate move of taxon to new parent taxon 
                        util.logger.info(f'Parents differ; Moving taxon to GBIF certified parent taxon: {parentName} ')
                        print('*', end='')

                        # Update the parent taxon at Specify 
                        success = self.updateSpecifyTaxonParent(taxonInstance, targetParent)
                    else:
                        util.logger.info(f'Could not find parent taxon: {parentName} in Specify!')
                        success = False
                else: 
                    util.logger.info(f'Parent taxa identical; No move action performed. ')
                    success = False
        else:
            util.logger.info(f'Could not retrieve unambiguous accepted name from GBIF... ({len(matches)} matches)')
            success = False
        return success

    def updateSpecifyTaxonAuthor(self, taxonInstance, acceptedAuthor):
        """
        Function for direct call to Specify7 API to set a new author name. 
        """
        util.logger.info(f'Updating author name at Specify for: [{taxonInstance}] to: "{acceptedAuthor}"')
        
        # Get original specify taxon record  
        spobjOriginal = self.sp.getSpecifyObject('taxon',taxonInstance.id)
        if spobjOriginal: 
            # Update the author name of the original specify taxon record 
            spobjOriginal['author'] = acceptedAuthor
            # Update the original specify taxon record through API PUT
            return self.sp.putSpecifyObject('taxon', taxonInstance.id, spobjOriginal)
        else: 
            return 500 

    def updateSpecifyTaxonParent(self, taxonInstance, targetParent):
        """
        Function for direct call to Specify7 API to move a taxon to a new parent  
        """
        # Update the parent taxon at Specify 
        util.logger.info(f'Updating parent taxon at Specify for: [{taxonInstance}] to: "{targetParent}"')
        success = False

        # 
        print(f'|{taxonInstance.id}=>{targetParent.id}|', end='')
        print('{', end='')
        start = time.time()
        result = self.sp.moveTreeNode(self.sptype, taxonInstance.id, targetParent.id)
        end = time.time()
        timeElapsed = end - start
        print(round(timeElapsed, 2), end='}')
        if result.status_code == "500": 
            util.logger.info(' - 500: Internal Server Error.')
            print('@', end= '')
        util.logger.info(f'Moved {taxonInstance.id} to target parent {targetParent.id}; Time elapsed: {timeElapsed} ')
                        
        # If result is OK, then mark as resolved  
        if result.status_code == '200':
            success = True

        return success

    def recordAmbivalentCase(self, original, lookup, ambivalence):
        """
        Function for recording ambivalent duplicate cases for export 
        """
        # 
        util.logger.info(ambivalence)
        original.remarks = str(original.remarks) + f' | {ambivalence}'
        self.ambivalentCases.append(original)
        lookup.remarks = str(lookup.remarks) + f' | {ambivalence}'
        self.ambivalentCases.append(lookup)


    def printLegend(self):
        print('LEGEND:')
        print('◘      = Handling taxon ')
        print('<rank> = Taxon rank id (Genus:180, Species:220, Subspecies:230)')
        print('[id]   = Single taxon entry (id = primary key)')
        print('!      = Possible duplicate ')
        print('#      = Could not retrieve taxon ')
        print('?      = Ambivalence on authors ')
        print('¿      = Ambivalence on parent taxa ')
        print('x      = Duplicates not found ')
        print('¤      = Author names missing: Force merge ')
        print('*      = Ambiguity resolved for merge/move ')
        print('|s->t| = Merge/move request (s = taxon id, t = target id)')
        print('|s=>t| = Merge/move request (s = taxon id, t = target parent id)')
        print(r'{t}   = Merge/move duration (t = time elapsed)')
        print('@      = An error occurred' )
        print('----------------------------------')
        #print('[    = Start of batch ')
        #print(']    = End of batch ')

    def __str__(self) -> None:
        """
        """
        return "MergeDuplicateTaxaTool"

