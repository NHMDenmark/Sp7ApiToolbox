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
from tools.sp7api_tool import Sp7ApiTool
import specify_interface
from tools.sp7api_tool import Sp7ApiTool

class ImportSynonymTool(Sp7ApiTool):
    """
    Tool 
    """        

    def __init__(self, specifyInterface: specify_interface.SpecifyInterface) -> None:
        """
        
        """
        
        super().__init__(specifyInterface)
        
    def processRow(self, headers, row) -> None:
        """
        Handle row by ...
        """

        pass

    def addTaxonNode(self, headers, row):
        """
        
        """

        


    def validateRow(self, row) -> bool:
        """
        Unfinished method for evaluating whether row format is valid. 
        """
        print(row)
        return True

    def validateHeaders(self, headers) -> bool:
        """
        Method for ensuring that the file format can be used by the tool.
        """
        # Check headers to see if these fit the expected file format
        if len(headers) < 2:
            raise Exception("Wrong header count. Expected: at least 2")
            #return False
        else:
            if headers[0] != "Class": 
                raise Exception("Wrong first header (parent node). Expected: Class")
                #return False
            else:
                return True
        
        #return False

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