# -*- coding: utf-8 -*-
"""
  Created on Tuesday June 14, 2022
  @author: Fedor Alexander Steeman, NHMD
  Copyright 2022 Natural History Museum of Denmark (NHMD)
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

  PURPOSE: Interface to the GBIF API 
"""

import requests
import json 
import urllib3
from pathlib import Path

# Internal Dependencies
import util 
import global_settings as gs
from models import taxon

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class GBIFInterface():
  """
  The GBIF Interface class acts as a wrapper around a selection of API functions offered by Specify7. 
  """
    
  def __init__(self) -> None:
    """
    ...
    """
    # Create a session for storing cookies 
    self.spSession = requests.Session() 
    self.baseURL = 'https://api.gbif.org/v1/'

  def fetchObject(self, object_name, id):
    """
    ...
    """
    # fetch API object 
    response = self.spSession.get(self.baseURL + f'{object_name}/{id}/', verify=False)

    # If succesful, load into json object 
    if response.status_code < 299:
      return json.loads(response.text)
    else: 
      return None

  def fetchSpecies(self, id):
    """
    ...
    """
    return self.fetchObject('species', id)

  def getSpecies(self, id):
    """
    ...
    """
    # Get species from API
    species = self.fetchSpecies(id)

    # Convert species data to taxon model instance 
    speciesTaxon = taxon.Taxon(0)
    speciesTaxon.fill(species, 'GBIF')

    return speciesTaxon

  def matchName(self, object_name, taxon_name, collection_id, kingdom=''):
    """
    ...
    """
    
    matches = {}
    acceptedNames = []

    # Fetch possible alternatives with matching taxon names 
    # https://api.gbif.org/v1/species/?kingdom=Plantae&name=Potentilla&limit=999
    urlString = self.baseURL + f'{object_name}/?kingdom={kingdom}&name={taxon_name}&limit=999'
    util.logger.debug(urlString)
    try:
      response = self.spSession.get(urlString)    
      # If succesful, load response into json object 
      if response.status_code < 299:
        response_text = json.loads(response.text)
    
      for result in response_text['results']:

        # Add main entry
        if result['taxonomicStatus'] == 'ACCEPTED':
          if 'taxonID' in result:
            if 'gbif' in result['taxonID']: 
              mainSpecies = self.fetchSpecies(int(result['key']))
              acceptedNames.append(mainSpecies)
        else:
          pass #print(f"Not accepted name: {result['scientificName']}")
                
        # Check for suggested alternatives and add to accepted names list, thereby removing synonyms
        #if 'alternatives' in result:
        #  matches = result['alternatives']
        #  for m in matches: 
        #    if 'matchtype' in m and 'status' in m: 
        #      if m['matchType'] == 'EXACT' and (m['status'] == 'ACCEPTED' or m['status'] == 'DOUBTFUL'):
        #        acceptedNames.append(self.getSpecies(int(m['usageKey'])))
    except:
        util.logger.error("Error occurred fetching accepting names at GBIF API!")
        pass

    return acceptedNames

def testcode():
  #
  gi = GBIFInterface()

  acceptedNameMatches = gi.matchName('species', 'Potentilla tridentata', 688130, 'Plantae')

  print(f' Found {len(acceptedNameMatches)} accepted name(s)' )
  for match in acceptedNameMatches:
    print(match.author)

#testcode()