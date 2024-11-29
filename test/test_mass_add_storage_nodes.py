import csv
import configuration
import specify_interface as sp
import tools.treenode_tool
import tools.mass_add_storage_nodes

cfg = configuration.ConfigurationHandler()
cfg.loadConfiguration('unit')
cfg.loadTools()

spi = sp.SpecifyInterface()

tool = tools.mass_add_storage_nodes.MassAddStorageNodeTool(spi)

def test_initialization():
    """ Test whether class initializes properly """
    assert tool is not None 
    assert tool.sptype == 'storage'

def test_validateHeaders():
    """ Test whether headers are properly validated """
    with open('data/mass_add_storage_nodes.csv', mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file, delimiter=',')
        headers = csv_reader.fieldnames

    assert tool.validateHeaders(headers)

def test_addChildNodes():
    """ Test adding child nodes """
    
    headers = ['Building', 'Room', 'Freezer']
    row = {'Building': 'Main Site', 'Room': 'Double Room', 'Freezer': 'Cryo 1'}
    
    tool.addChildNodes(headers, row, 1, 0)
    
    ranks = []
    for header in headers:
        ranks.append(tool.getTreeDefItem(header)['rankid'])

    # Check presence of each node
    buildings = spi.getSpecifyObjects('storage', 1, 0, {'name': row['Building'], 'rankid': ranks[0]})
    assert len(buildings) > 0 
    if len(buildings) > 0:
        building = buildings[0]
        assert building['name'] == row['Building']
        rooms = spi.getSpecifyObjects('storage', 1, 0, {'name': row['Room'], 'parent': building['id'], 'rankid': ranks[1]})
        assert len(rooms) > 0
        if len(rooms) > 0:
            room = rooms[0]
            assert room['name'] == row['Room']
            freezers = spi.getSpecifyObjects('storage', 1, 0, {'name': row['Freezer'], 'parent': room['id'], 'rankid': ranks[2]})
            assert len(freezers) > 0 
            if len(freezers) > 0:
                freezer = freezers[0]
                assert freezer['name'] == row['Freezer']

    # Clean up afterwards
    if freezer: 
        spi.deleteSpecifyObject('storage', freezer['id'])
    if room:
        spi.deleteSpecifyObject('storage', room['id'])
    if building: 
        spi.deleteSpecifyObject('storage', building['id'])


def test_runTool():
    """ Test whether nodes were added as expected and clean up again """
    pass


