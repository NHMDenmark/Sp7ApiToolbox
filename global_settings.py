# -*- coding: utf-8 -*-
"""
  Created on August 16, 2022
  @author: Fedor Alexander Steeman, NHMD
  Copyright 2022 Natural History Museum of Denmark (NHMD)
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

  PURPOSE: Assemblage of global settings used across the application. 
"""

settings = {
    'baseURL': '',
    'database': {
        'name': 'db',
        'in_memory': False
    },
    'session': {
        'institutionId': 0,
        'institutionName': '',
        'collection': None,
        'collectionId': 0,
        'collectionName': '',
        'firstName': '',
        'middleInitial': '',
        'lastName': '',
        'userName': '',
        'password': '',
        'spUserId': -1,
        'csrfToken': '',
        'lengthCatalogNumber': 0
    }
}

def clear_session():
    settings['session'].update({
        'institutionId': 0,
        'institutionName': '-not set-',
        'collectionId': 0,
        'collectionName': '-not set-',
        'userName': '-not set-',
        'password': '',
        'spUserId': -1,
        'csrfToken': ''
    })