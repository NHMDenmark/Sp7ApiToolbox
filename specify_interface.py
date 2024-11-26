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

  PURPOSE: Interface to the Specify API 
"""

import requests # Documentation: https://requests.readthedocs.io/en/latest/api/ 
import json 
import urllib3
import traceback

# Internal Dependencies
import util
import global_settings as app

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SpecifyInterface():
  """
  The Specify Interface class acts as a wrapper around a selection of API functions offered by Specify7. 
  The URL of the specify server to be accessed is set in global_settings.py 
  Interactions with Specify7 require a token to prevent Cross Site Request Forgery (CSRF). 
  In order to log in, an initial CSRF token must be acquired by accessing .../context/login/ (getCSRFToken).
  The initial CSRF token kan be used to subsequently log in using a Specify username/password combination (specifyLogin). 
  """

  def __init__(self, token=None) -> None:
    """ 
    CONSTRUCTOR
    Creates a session for storing cookies  
    """      
    self.spSession = requests.Session() 
    self.csrfToken = ''
    self.verifySSL = True
    self.baseURL = app.settings['baseURL']

  def getInitialCollections(self):
    """ 
    Specify7 will return a list of the institution's collections upon initial contact.
    CONTRACT
      RETURNS collections list (dictionary)
    """ 
    util.logger.debug('Get initial collections')
    response = self.spSession.get(self.baseURL + "context/login/", verify=self.verifySSL)
    util.logger.debug(' - Response: ' + str(response.status_code) + " " + response.reason)
    collections = json.loads(response.text)['collections'] # get collections from json string and convert into dictionary
    util.logger.debug(' - Received %d collection(s)' % len(collections))
    util.logger.debug('------------------------------')

    return collections

  def getCSRFToken(self):
    """ 
    Specify7 requires a token to prevent Cross Site Request Forgery 
    This will also return a list of the institution's collections 
    CONTRACT
       Returns csrftoken (String)
    """   
    #util.logger.debug('Get CSRF token from ', self.baseURL)
    response = self.spSession.get(self.baseURL + 'context/login/', verify=self.verifySSL)
    self.csrfToken = response.cookies.get('csrftoken')
    util.logger.debug(' - Response: %s %s' %(str(response.status_code), response.reason))
    util.logger.debug(' - CSRF Token: %s' % self.csrfToken)
    util.logger.debug('------------------------------')
    return self.csrfToken

  def specifyLogin(self, username, passwd, collection_id):
      """ 
      Function for logging in to the Specify7 API and getting the CSRF token necessary for further interactions in the session 
      CONTRACT
        username (String) : Specify account user name  
        passwd   (String) : Specify account password  
        RETURNS  (String) : The CSRF token necessary for further interactions in the session 
      """
      util.logger.debug('Connecting to Specify7 API at: ' + self.baseURL)
      token = self.login(username, passwd, collection_id, self.getCSRFToken())
      util.logger.debug(' - Log in CSRF Token: %s' % token)
      if self.verifySession(token):
          return token
      else:
          return '' 

  def login(self, username, passwd, collectionid, csrftoken):
    """ 
    Username and password should be passed to the login function along with CSRF token 
    After successful login a new CSRF token is issued that should be used for the continuing session 
    CONTRACT 
      username  (String) : The Specify account's username 
      passwd    (String) : The password for the Specify account
      csrftoken (String) : The CSRF token is required for security reasons  
    """
    util.logger.debug('Log in using CSRF token & username/password')
    headers = {'content-type': 'application/json', 'X-CSRFToken': csrftoken, 'Referer': self.baseURL}
    response = self.spSession.put(self.baseURL + "context/login/", json={"username": username, "password": passwd, "collection": collectionid}, headers=headers, verify=self.verifySSL) 
    
    if response.status_code > 299:
      csrftoken = ''
      util.logger.error('Error logging in to Specify! ')
      util.logger.error(response.text)
    else:
      csrftoken = response.cookies.get('csrftoken') # Keep and use new CSRF token after login

    util.logger.debug(' - Response: %s %s' %(str(response.status_code), response.reason))
    util.logger.debug(f' - New CSRF Token: {csrftoken}')
    util.logger.debug('------------------------------')
    return csrftoken

  def verifySession(self, token):
    """ 
    Attempt to fetch data on the current user being logged in as a way to verify the session  
    CONTRACT 
      token (String) : The CSRF token is required for security reasons
      RETURNS boolean to indicate session validity
    """  
    validity = None

    headers = {'content-type': 'application/json', 'X-CSRFToken': token, 'Referer': self.baseURL}
    response = self.spSession.get(self.baseURL + "context/user.json", headers=headers, verify=self.verifySSL)
    
    if response.status_code > 299:
      validity = False 
    else:
      validity = True
      self.csrfToken = token
    
    return validity

  def specifyLogout(self):
      """ 
      Function for logging out of the Specify7 API again 
      """
      util.logger.debug('logging out of Specify...')
      self.logout(self.csrftoken)

  def getCollObject(self, collectionObjectId):
    """ 
    Fetches collection objects from the Specify API using their primary key 
    CONTRACT 
      collectionObjectId (Integer) : The primary key of the collectionObject, which is not the same as catalog number  
      NOTE DEPRECATED: csrftoken          (String)  : The CSRF token is required for security reasons 
      RETURNS fetched object 
    """   
    util.logger.debug('Query collection object')
    headers = {'content-type': 'application/json', 'X-CSRFToken': self.csrfToken, 'Referer': self.baseURL}
    response = self.spSession.get(self.baseURL + "api/specify/collectionobject/" + str(collectionObjectId)  + "/", headers=headers)
    util.logger.debug(' - Response: %s %s' %(str(response.status_code), response.reason))
    if response.status_code < 299:
      object = response.json()
      catalogNr = response.json()['catalognumber']
      util.logger.debug(f' - Catalog number: {catalogNr}')
    else:
      object = {}
    util.logger.debug('------------------------------')
    return object 

  def getSpecifyObjects(self, objectName, limit=100, offset=0, filters={}):
    """ 
    Generic method for fetching object sets from the Specify API based on object name 
    CONTRACT 
      objectName (String)     : The API's name for the objects to be queried  
      limit      (Integer)    : Maximum amount of records to be retrieve at a time. Default value: 100 
      offset     (Integer)    : Offset of the records to be retrieved for enabling paging. Default value: 0 
      filters    (Dictionary) : Optional filters as a key, value pair of strings 
      RETURNS fetched object set 
    """ 
    util.logger.debug(f'Fetching "{objectName}" with limit {limit} and offset {offset} ')
    objectSet = {}
    headers = {'content-type': 'application/json', 'X-CSRFToken': self.csrfToken, 'Referer': self.baseURL}
    filterString = ""
    for key in filters:
      filterString += f"&{key}={filters[key]}"
    apiCallString = f'{self.baseURL}api/specify/{objectName}/?limit={limit}&offset={offset}{filterString}'
    response = self.spSession.get(apiCallString, headers=headers, verify=False)
    util.logger.debug(f' - Response: {str(response.status_code)} {response.reason}')
    if response.status_code < 299:
      objectSet = json.loads(response.text)['objects'] # get collections from json string and convert into dictionary
      util.logger.debug(' - Received %d object(s)' % len(objectSet))
    else:
      util.logger.debug(' - Failure. ')
    
    return objectSet 

  def getSpecifyObject(self, objectName, objectId):
    """ 
    Generic method for fetching objects from the Specify API using their primary key
    CONTRACT 
      objectName (String)  : The API's name for the object to be fetched  
      objectId   (Integer) : The primary key of the object
      RETURNS fetched object 
    """ 
    util.logger.debug('Fetching ' + objectName + ' object on id: ' + str(objectId))
    headers = {'content-type': 'application/json', 'X-CSRFToken': self.csrfToken, 'Referer': self.baseURL}
    apiCallString = f'{self.baseURL}api/specify/{objectName}/{objectId}/' 
    util.logger.debug(apiCallString)
    response = self.spSession.get(apiCallString, headers=headers, verify=False)
    util.logger.debug(f' - Response: {str(response.status_code)} {response.reason}')
    util.logger.debug(f' - Session cookies: {self.spSession.cookies.get_dict()}')
    if response.status_code < 299:
      object = response.json()
    else: 
      raise Exception(f"Response error: {response.status_code}")

    return object 

  def putSpecifyObject(self, objectName, objectId, specifyObject):
    """ 
    Generic method for putting changes to an existing object to the Specify API using their primary key 
    CONTRACT 
      objectName    (String)  : The API's name for the object to be fetched  
      objectId      (Integer) : The primary key of the object 
      specifyObject (JSON)    : The (possibly altered) state of the object 
      RETURNS response status code (String)
    """
    headers = {'content-type': 'application/json', 'X-CSRFToken': self.csrfToken, 'referer': self.baseURL}
    apiCallString = f"{self.baseURL}api/specify/{objectName}/{objectId}/"
    util.logger.debug(apiCallString)
    util.logger.debug(specifyObject)
    response = self.spSession.put(apiCallString, data=json.dumps(specifyObject), headers=headers)
    #response = requests.put(apiCallString, data=specifyObject, json=specifyObject, headers=headers)
    util.logger.debug(f' - Response: {str(response.status_code)} response.reason')
    # if response.status_code < 299:
    #   object = response.json()
    # else: 
    #  object = None
    # return object 
    return response.status_code 

  def postSpecifyObject(self, objectName, specifyObject):
    """ 
    Generic method for posting a new object to the Specify API including a primary key
    CONTRACT 
      objectName    (String)  : The API's name for the object to be fetched  
      specifyObject (JSON)    : The state of the object to be created 
      RETURNS response  
    """ 
    headers = {'content-type': 'application/json', 'X-CSRFToken': self.csrfToken, 'referer': self.baseURL}
    apiCallString = f"{self.baseURL}api/specify/{objectName}/"
    util.logger.debug(apiCallString)
    response = self.spSession.post(apiCallString, headers=headers, json=specifyObject, verify=False)
    util.logger.debug(' - Response: %s %s' %(str(response.status_code), response.reason))
    if response.status_code < 299:
       return response.json()
    else: 
      raise Exception(f"Response error: {response.status_code}")
    #return response.status_code 

  def directAPIcall(self, callString):#, csrftoken):
    """ 
    Generic method for allowing a direct call to the API using a call string that is appended to the baseURL
    CONTRACT
      callString (String) : The string to the appended to the base URL of the API
      NOTE DEPRECATED: csrftoken  (String) : The CSRF token is required for security reasons  
      RETURNS response object  
    """ 
    apiCallString = "%s%s" %(self.baseURL, callString)
    util.logger.debug(apiCallString)
    headers = {'content-type': 'application/json', 'X-CSRFToken': self.csrfToken, 'Referer': self.baseURL}
    response = self.spSession.get(apiCallString, headers=headers)
    util.logger.debug(' - Response: %s %s' %(str(response.status_code), response.reason))
    
    if response.status_code < 299:
      return json.loads(response.text)
    else:
      raise Exception(f"Response error: {response.status_code}") 

  def logout(self):#, csrftoken):
    """ 
    Logging out closes the session on both ends 
    CONTRACT 
      NOTE DEPRECATED: csrftoken (String) : The CSRF token is required for security reasons
    """ 
    util.logger.debug('Log out')
    headers = {'content-type': 'application/json', 'X-CSRFToken': self.csrfToken, 'Referer': self.baseURL}
    response = self.spSession.put(self.baseURL + "context/login/", data="{\"username\": null, \"password\": null, \"collection\": 688130}", headers=headers)
    util.logger.debug(' - %s %s ' %(str(response.status_code), response.reason))
    util.logger.debug('------------------------------')

  def mergeTreeNodes(self, tree_name, source_id, target_id):
    """
    Special function for merging tree nodes. 
    Merging is done from the source node to the target node. 
    The source node will be deleted and the target node and its Specify id will prevail. 
    CONTRACT 
      tree_name (string) : Name of the Specify Tree to be handled: {"taxon", "storage", "geography"} 
      source_id (int)    : Specify ID of the node to be merged into the target node 
      target_id (int)    : Specify ID of the node to be merged with (the target node)
      RETURNS response object 
    """   
    headers = {'X-CSRFToken': self.csrfToken, 'referer': self.baseURL, } 
    apiCallString = f"{self.baseURL}api/specify_tree/{tree_name}/{source_id}/merge/"
    util.logger.debug(" - API call: %s"%apiCallString)
    exception = False
    
    try:
      response = self.spSession.post(apiCallString, headers=headers, data={'target' : target_id }, timeout=960) 
    except Exception as e:
      util.logger.error(str(e))
      traceBack = traceback.format_exc()
      util.logger.error(traceBack)
      exception = True
      util.logger.debug(f' - Response: {str(response.status_code)} {response.reason} {response.text}.')
      response = util.Struct(status_code='408')

    return response

  def moveTreeNode(self, tree_name, source_id, target_id):
    """
    Special function for moving a node to another parent. 
    The parent node to be moved to is termed the target node. 
    CONTRACT 
      tree_name (string) : Name of the Specify Tree to be handled: {"taxon", "storage", "geography"} 
      source_id (int)    : Specify ID of the node to be moved to the target node being the new parent 
      target_id (int)    : Specify ID of the new parent node to be moved to (the target node)
      RETURNS response object 
    """   
    headers = {'X-CSRFToken': self.csrfToken, 'referer': self.baseURL, } 
    apiCallString = f"{self.baseURL}api/specify_tree/{tree_name}/{source_id}/move/"
    # TODO target_id into header as "target"
    util.logger.debug(" - API call: %s"%apiCallString)
    exception = False

    #input('ready?')
    
    try:
      response = self.spSession.post(apiCallString, headers=headers, data={'target' : target_id }, timeout=960) 
    except Exception as e:
      util.logger.error(str(e))
      traceBack = traceback.format_exc()
      util.logger.error(traceBack)
      exception = True
      #util.logger.debug(f' - Response: {str(response.status_code)} {response.reason} {response.text}.')
      response = util.Struct(status_code='408')
    
    #print(response) 

    return response
