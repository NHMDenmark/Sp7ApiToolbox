import csv
import configuration
import specify_interface as sp
import tools.treenode_tool
import tools.import_synonyms

cfg = configuration.ConfigurationHandler()
cfg.loadConfiguration('unit')
cfg.loadTools()

spi = sp.SpecifyInterface()

tool = tools.import_synonyms.ImportSynonymTool(spi)

headers = ['Class', 'Order', 'Family','Genus','Species', 'SpeciesAuthor', 'isAccepted', 'AcceptedGenus', 'AcceptedSpecies','AcceptedSpeciesAuthor']
acc_row = {'Class': 'Mammalia', 'Order': 'Carnivora', 'Family': 'Otariidae', 'Family': 'Otariidae', 'Family': 'Otariidae', 
            'Genus' : 'Eumetopias', 'Species' : 'jubatus', 'SpeciesAuthor' : 'Schreber, 1776', 'isAccepted' : 'Yes', 
            'AcceptedGenus' : '', 'AcceptedSpecies' : '','AcceptedSpeciesAuthor' : ''}
syn_row = {'Class': 'Mammalia', 'Order': 'Carnivora', 'Family': 'Otariidae', 'Family': 'Otariidae', 'Family': 'Otariidae', 
            'Genus' : 'Phoca', 'Species' : 'jubata', 'SpeciesAuthor' : 'Schreber, 1776', 'isAccepted' : 'No', 
            'AcceptedGenus' : 'Eumetopias', 'AcceptedSpecies' : 'jubatus','AcceptedSpeciesAuthor' : 'Schreber, 1776'}

def test_initialization():
    """ Test whether class initializes properly """
    assert tool is not None 
    assert tool.sptype == 'taxon'

def test_validateHeaders():
    """ Test whether headers are properly validated """
    with open('data/import_synonyms.csv', mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file, delimiter=',')
        headers = csv_reader.fieldnames

    assert tool.validateHeaders(headers)

def test_createTreeNode():
    """ """
    row = acc_row
    node = tool.createTreeNode(headers, row, 1, 4)
    assert node
    assert node.name == row['Species']
    assert node.fullname == row['Genus'] + ' ' + row['Species']

def test_createSynTreeNode():
    """ """
    row = syn_row
    node = tool.createTreeNode(headers, row, 1, 4)
    assert node
    assert node.name == row['Species']
    assert node.fullname == row['Genus'] + ' ' + row['Species']

def test_addChildNodes():
    """ Test adding child nodes """
    


    tool.addChildNodes(headers, acc_row, 1, 0)
    
    ranks = []
    for header in headers:
        ranks.append(tool.getTreeDefItem(header)['rankid'])

    # Check presence of each node


    # Clean up afterwards




def test_runTool():
    """ Test whether nodes were added as expected and clean up again """
    pass


