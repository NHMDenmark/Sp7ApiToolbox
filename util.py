# -*- coding: utf-8 -*-
"""
  Created on June 24, 2022
  @author: Fedor Alexander Steeman, NHMD / Jan K. Legind, NHMD
  Copyright 2022 Natural History Museum of Denmark (NHMD)
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at::
  http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

  PURPOSE: Assemblage of generic utility functions used across the application. 
"""

import os, sys
from os import system, name
from pathlib import Path
import time
import logging
from datetime import datetime
import random

logger = logging.getLogger()

def cls():
    """
    Clear Command Line Interface screen
    """
    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux
    else:
        _ = system('clear')


def buildLogger():  # moduleName):
    """
    Sets up logging
    """
    # 1. Create log file name including directory path
    sTime = time.strftime('{%Y%m%d%H%M%S}').replace("{", "").replace("}", "")
    logName = f"log-{sTime}.log"
    logFilePath = str(Path(getLogsPath()).joinpath(logName))

    # 2. Set up file handler for logger
    fileHandler = logging.FileHandler(filename=logFilePath)
    # logFileFormatter = logging.Formatter(fmt=f"%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    logFileFormatter = logging.Formatter(
        '[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', '%m-%d %H:%M:%S')
    fileHandler.setFormatter(logFileFormatter)
    fileHandler.setLevel(level=logging.DEBUG)

    # 3. Start logger
    logger.addHandler(fileHandler)
    logger.setLevel(logging.DEBUG)

    logger.debug('Logging set up')
    logger.debug('--------------')


def getLogsPath():
    return str(Path(getUserPath()).joinpath('logs'))


def getUserPath():
    """
    Get user documents path agnostic of OS or presence of OneDrive setup
    """
    # Assuming regular system; Get regular user home path
    homePath = str(Path(os.path.expanduser('~')))

    # Now check for existance of OneDrive user documents path
    if "oneDrive" in os.environ:
        # OneDrive system if full user documents path exists,
        #  because that is where installer creates it:
        oneDrivePath = os.environ['OneDrive']
        # If the full path exists then use the onedrivepath as home path
        if os.path.exists(str(Path(oneDrivePath).joinpath('Documents').joinpath('DaSSCo'))):
            homePath = oneDrivePath

            # Extend the user home path to point to DaSSCo documents folder
    userPath = str(Path(homePath).joinpath('Documents').joinpath('DaSSCo'))

    return userPath


def logLine(line, level='info'):
    """
    Write a line to the log using the logging module initialized.
    """

    if (level == 'info'):
        logger.info(line)
    elif (level == 'debug'):
        logger.debug(line)
    elif (level == 'warning'):
        logger.warning(line)
    elif (level == 'error'):
        logger.error(line)
    else:
        logger.info(line)

    return line


def shrink_dict(original_dict, input_string):
    """
    Filter entries in dictionary based on initial string (starts with)
    """
    shrunken_dict = {}

    for j in original_dict:
        if j[0:len(input_string)] == input_string:
            shrunken_dict[j] = original_dict[j]
    return shrunken_dict


def convert_dbrow_list(list, addEmptyRow=False):
    """
    Converts datarow list to name array
    """
    new_list = []
    if addEmptyRow: new_list.append('-please select-')
    for item in list:
        new_list.append(item['name'])

    return new_list


def getRandomNumberString():
    """
    Returns positive random number string based on date/time hash
    """
    r1 = random.randint(0, 10000)
    randomNumberString = hash(f"{datetime.now()}{r1}")  # Get random number as container name
    if randomNumberString < 0: randomNumberString += sys.maxsize  # Ensure that it's a positive number
    return randomNumberString
    
def pretty_print_POST(req):
    """
    Format HTTP request header and body into easily legible output
    """
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
      '-----------START-----------',
      req.method + ' ' + req.url,
      '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
      req.body,
    ))
    print('------------END------------')
