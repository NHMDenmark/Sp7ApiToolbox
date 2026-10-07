# Sp7ApiToolbox

The Specify7 Api Toolbox aims to gather different code classes, named tools, for interacting with the Specify7 API allowing for bulk actions. For the time being it will run from a command line and can be run directly in a development environment. Pending needs, a fully functional release may be published eventually, perhaps even with a graphical user interface. 

## Configuration 

Configuration can be done using multiple config files that reside in the root folder. The config.json is the default that can serve as a template for interaction with the Specify7 Demo site. It is possible to differentiate and add several optional config files that can be selected during runtime using the "mode" as argument. For this to work, the "mode" name, e.g. "debug" should be made part of the config filename like so: config.debug.json. The name of the mode can be chosen freely, but should not include spaces or punctuation characters. Since the config file contains passwords, it is recommended to retain it locally and not commit it to the online repository. 

### VS Code 

In VS Code the following could be added to the launch.json in order to launch a "debug" mode, specified in a "config.debug.json" file. 

        {
            "name": "Debug",
            "type": "debugpy",
            "request": "launch",
            "program": "main.py",
            "console": "integratedTerminal",
            "args": ["debug"]
        }

## Data 

The data to be used by the various tools are placed in the data folder. The common format is a tabular csv format. The precise data file definitions depends on the tool that uses it. 

## Tools

Tools are placed in the "tools" folder and added dynamically during runtime, so they can be selected during operation. The following tools have been added so far, and may be work in progress: 

### Mass Add Storage Nodes

This tool bulk adds nodes to the storage tree. The first column is interpreted as the parent and the subsequent column the different subordinate children. For now, the parent column has to be collection level, though this may be changed in the future. The child columns can be any number of subordinate nodes as long as the column headers correspond to the level names defined in enums.py (StorageRank). 

The example file cabinet_shelf_numbers test.csv has three columns (Collection;Cabinet;Shelf)

The tool is fully functional. 

### Collapse Storage Nodes 

Under construction

### Import Synonyms 

Under construction

### Merge Duplicate Taxa

Under construction


