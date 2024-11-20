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

  PURPOSE: Tool for merging storage nodes upwards towards their nearest parent 
"""

import os
import csv

# Internal Dependencies 
from tools.sp7api_tool import Sp7ApiTool
import specify_interface
from enums import StorageRank

class MassAddStorageNodeTool(Sp7ApiTool):
    """
    Tool for merging storage nodes upwards towards their nearest parent.
    """

    def __init__(self, specifyInterface: specify_interface.SpecifyInterface) -> None:
        """
        CONSTRUCTOR

        """
        super().__init__(specifyInterface)

    def runTool(self, args):
        """
        
        """
        filename = args.get('filename')
        if not filename:
            raise Exception("No filename provided in args.")

        if not os.path.isfile(f'data/{filename}'):
            raise Exception(f"File {filename} does not exist.")

        with open(f'data/{filename}', mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, delimiter=';')
            headers = csv_reader.fieldnames
            print(f"CSV Headers: {headers}")

            if self.validateHeaders(headers):
                for row in csv_reader:
                    if self.validateRow(row):
                        self.addStorageLocation(headers, row)

    def validateRow(self, row) -> bool:
        """
        """
        print(row)
        return True

    def validateHeaders(self, headers) -> bool:
        """
        
        """
        # Check headers to see if these fit the expected file format
        if len(headers) != 3:
            raise Exception("Wrong header count. Expected: 3")
            #return False
        else:
            if headers[0] != "Collection": 
                raise Exception("Wrong first header (parent node). Expected: Collection")
                #return False
            else:
                return True
        
        #return False
        

    def addStorageLocation(self, headers, row):
        """
        
        """

        #1. Get parent of storage node 
        parent_id = ''
        parent_name = row[headers[0]]
        parent_nodes = self.sp.getSpecifyObjects("storage", 100, 0, {'fullname': parent_name})
        if not parent_nodes:
            raise Exception("Could not retrieve parent node!")
        else:
            parent_id = parent_nodes[0]['id']

        #2. Check if child node does not already exist 
        child_name = row[headers[1]]        
        child_nodes = self.sp.getSpecifyObjects("storage", 1000, 0, {'fullname': child_name, 'parent': parent_id})
        if len(child_nodes) == 0:
            # Child node not present; Proceed to add child node
            storage_node = self.createStorageNodeJson(child_name, child_name, parent_id, headers[1])
            self.sp.postSpecifyObject('storage', storage_node)
            pass

        pass

    def createStorageNodeJson(self, name, fullname, parent_id, rankname, ) -> str:
        """
        
        """

        rankid = StorageRank[rankname].value

        node = {'fullname': fullname,
                'name': name,
                'rankid': rankid,
                'parent': f'/api/specify/storage/{parent_id}/'
            }
        
        return node

    def __str__(self) -> str:
        """
        String representation of the tool.
        """
        return "MassAddStorageNodeTool"
    
