# -*- encoding: utf-8 -*-
"""
  Created on July 29, 2025
  @author: Fedor Alexander Steeman, NHMD
  Copyright 2024 Natural History Museum of Denmark (NHMD)
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

  PURPOSE: Tool for merging duplicate taxon pairs in Specify7 based on data file with primary key pairs.
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

class MergeTaxonPairsTool(Sp7ApiTool):
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
        
        self.gbif = GBIF_interface.GBIFInterface()

    def runTool(self, args):
        """
        
        """

        print("Running MergeTaxonPairs...")
        print("Arguments: ", args)
        print("specifyAPI token:", self.sp.csrfToken)
        print("Collection Id:", self.collection.id)
        print("Discipline Id:", self.collection.discipline.id)
        print("Taxon tree def id:", self.collection.discipline.taxontreedefid)
        
        #self.printLegend()        
        #print('----------------------------------')

        super().runTool(args)
    
    def processRow(self, headers, row) -> None:
        """
        Generic empty method for handling individual data file rows
        """
        from_id = row.get('from_id')
        to_id = row.get('to_id')    
        
        print(f"[{from_id} -> {to_id}]", end='... ')
        start = time.time()
        res = self.sp.mergeTreeNodes("taxon", from_id, to_id)
        end = time.time()
        timeElapsed = end - start
        print(f'[{res.status_code}]({timeElapsed:.2f}s)')
        pass

    def validateRow(self, row) -> bool:
        """
        Make sure that both TaxonID values are valid numbers. 
        """
        valid = str.isdigit(row.get('from_id')) and str.isdigit(row.get('to_id'))

        if not valid:
            print("Invalid row: ", row)
            util.logger.error(f"Invalid row: {row}")
        
        return valid

    def validateHeaders(self, headers) -> bool:
        """
        Method for ensuring that the file format can be used by the tool.
        """
        try:
            valid = headers == ['from_id', 'to_id']
        except Exception as e:
            util.logger.error(f"Error validating headers: {e}")
            print(f"Error validating headers: {e}")
            valid = False

        if not valid:
            print("Invalid headers. Expected: ['from_id', 'to_id']")
            util.logger.error("Invalid headers. Expected: ['from_id', 'to_id']")

        return valid

    def __str__(self) -> str:
        """
        String representation of the tool.
        """
        return "Sp7ApiTool"