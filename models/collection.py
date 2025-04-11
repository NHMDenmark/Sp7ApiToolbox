# -*- coding: utf-8 -*-
"""
  Created on September 28, 2022
  @author: Fedor Alexander Steeman, NHMD
  Copyright 2022 Natural History Museum of Denmark (NHMD)
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

  PURPOSE: Represent collection data record as "Model" in the MVC pattern  
"""

# Internal dependencies
from models import model
import models.discipline as discipline

class Collection(model.Model):
    """
    Class representing a collection data record  
    """

    def __init__(self, collection_id, specifyInterface) -> None:
        # Set up blank record 
        model.Model.__init__(self, collection_id, specifyInterface)
        self.table           = 'collection'
        self.sptype          = 'collection'
        self.institutionId   = 0
        self.taxonTreeDefId  = 0
        self.disciplineId    = 0
        self.discipline      = None 
        self.catalogNrLength = 9
        self.useTaxonNumbers  = None

        # Predefined data fields
        self.storageLocations = None 
        self.prepTypes = None 
        self.typeStatuses = None 
        self.geoRegions = None 
        self.geoRegionSources = None 

        self.fetch(collection_id)

# Overriding inherited functions
   
    def getFieldsAsDict(self):
        """
        Generates a dictonary with database column names as keys and specimen records fields as values 
        RETURNS said dictionary for passing on to data access handler 
        """
        
        fieldsDict = {
                'id':               f'{self.id}', 
                'spid':             f'{self.spid}', 
                'name':             f'"{self.name}"', 
                'institutionid':    f'{self.institutionId}', 
                'taxontreedefid':   f'{self.taxonTreeDefId}', 
                'visible':          f'{self.visible}', 
                'catalognrlength':  f'{self.catalogNrLength}',
                'usetaxonnumbers':  f'{self.useTaxonNumbers}'
                }
        
        return fieldsDict

    def setFields(self, jsonObject):
        """
        Function for setting collection object data field from record 
        CONTRACT 
           record: sqliterow object containing record data 
        """

        self.id              = jsonObject['id']
        self.spid            = jsonObject['spid']
        self.name            = jsonObject['name']
        self.institutionId   = jsonObject['institutionid']
        self.taxonTreeDefId  = jsonObject['taxontreedefid']
        self.visible         = jsonObject['visible']      
        self.catalogNrLength = jsonObject['catalognrlength']   
        self.useTaxonNumbers = jsonObject['usetaxonnumbers']
        pass 

# Specify Interfacing functions 

    def fill(self, jsonObject, source="Specify"):
        """
        Function for filling collection model's fields with data record fetched from external source
        CONTRACT 
            jsonObject (json)  : Data record fetched from external source
            source (String)    : String describing external source. 
                                 Options:
                                     "Specify = "Specify API 
        """
        self.source = source
        if jsonObject:
            if source=="Specify":
                self.id = jsonObject['id']
                self.guid = jsonObject['guid']
                self.name = jsonObject['collectionname']
                #self.fullname = jsonObject['collectionname'] 
                self.disciplineId = int(jsonObject['discipline'].split('/')[4])
                pass
                self.fetchDiscipline(source)
        else:
            self.remarks = 'Could not set values, because empty object was passed. '

    # Collection class specific functions 

    def fetchDiscipline(self, source="Specify"):
        """
        Method for fetching the discipline from the Specify API and filling it with data
        """
        self.discipline = discipline.Discipline(self.id)
        disciplineObj = self.sp.getSpecifyObject('discipline', self.disciplineId)
        self.discipline.fill(disciplineObj, source)

# Generic functions

    def __str__ (self):
        return f'[{self.table}] id:{self.id}, spid:{self.spid}, name:{self.name}, taxontreedefid = {self.taxonTreeDefId}'        