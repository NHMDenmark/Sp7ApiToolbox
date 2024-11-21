from enum import Enum

class StorageRank(Enum):
    """
    Storage names paired with rank ids as derived from a standard Specify setup
    """
    Institution = 0 
    Collection = 150 
    Room = 200 
    Aisle = 250 
    Cabinet = 300 
    Shelf = 350 
    Box = 400 
    Rack = 450 
    Vial = 500 
    Site = 75 
    CryoBox = 475 