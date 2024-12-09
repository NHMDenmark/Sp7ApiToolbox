import csv
import datetime 
import configuration
import specify_interface as sp
from models.treenode import TreeNode
import tools.treenode_tool
import tools.import_synonyms

cfg = configuration.ConfigurationHandler()
cfg.loadConfiguration('unit')
cfg.loadTools()

spi = sp.SpecifyInterface()

tool = tools.import_synonyms.ImportSynonymTool(spi)


base_row = {'Kingdom':'Animalia','Phylum':'Chordata','Class': 'Mammalia', 'Order': 'Carnivora', 'Family': 'Otariidae', 
           'Genus' : 'Eumetopias', 'Species' : 'jubatus', 'SpeciesAuthor' : 'Schreber, 1776', 'isAccepted' : 'Yes'}
 
acc_ext = {'AcceptedGenus' : '', 'AcceptedSpecies' : '','AcceptedSpeciesAuthor' : ''}
syn_ext = {'AcceptedGenus' : 'Eumetopias', 'AcceptedSpecies' : 'jubatus','AcceptedSpeciesAuthor' : 'Schreber, 1776'}

acc_row = {**base_row, **acc_ext}
syn_row = {**base_row, **syn_ext}

headers = {}

with open('data/import_synonyms.csv', mode='r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file, delimiter=',')
    headers = csv_reader.fieldnames
pass

def test_initialization():
    """ Test whether class initializes properly """
    assert tool is not None 
    assert tool.sptype == 'taxon'

def test_validateHeaders():
    """ Test whether headers are properly validated """

    assert tool.validateHeaders(headers)

def test_createTreeNode():
    """ Test creating a tree node """
    row = acc_row
    nodes = []

    index = 0
    parent_id = 1
    for header in headers:
        if header == 'SpeciesAuthor': break

        node = tool.createTreeNode(headers, row, parent_id, index)
        index = index + 1
        
        assert node

        if node:
            parent_id = node.id
            nodes.append(node)
            assert node.name == row[header]
            if node.rank == 220:
                assert node.fullname == row['Genus'] + ' ' + row['Species']
                assert node.author == row['SpeciesAuthor']

            taxon = spi.getSpecifyObject('taxon', node.id)
            
            assert taxon
            if taxon: 
                assert taxon['name'] == row[header]
                if node.rank == 220:
                    assert node.fullname == row['Genus'] + ' ' + row['Species']
                    assert node.author == row['SpeciesAuthor']
                    
    # Clean up afterwards
    nodes.reverse()
    for node in nodes: 
        spi.deleteSpecifyObject('taxon', node.id)

def test_addAcceptedRow():
    """ Test adding accepted row """
    row = acc_row
    
    taxon_headers = headers[:headers.index('SpeciesAuthor')]

    ranks = []
    for header in taxon_headers:
        ranks.append(header)
        if header == 'SpeciesAuthor': break
    ranks.reverse()

    node = tool.addChildNodes(taxon_headers, row, 1, 0)

    assert node
    passed = True
 
    taxon = spi.getSpecifyObject('taxon', node.id)
    assert taxon 

    taxon_id = taxon['id']

    # Check presence of each node
    nodes = []
    for rank in ranks:   
        obj = spi.getSpecifyObject('taxon', taxon_id)
        assert obj # node present
        node = TreeNode.init(obj)
        nodes.append(node)
        taxon_id = node.parent_id # prepare for next loop  

        # Check field value
        assert row[rank] == node.name

    # Clean up afterwards
    for node in nodes: 
        # Check if each nodes was just created: 
        current_datetime = datetime.datetime.now()
        same_minute = (node.create_datetime.year == current_datetime.year and
                       node.create_datetime.month == current_datetime.month and
                       node.create_datetime.day == current_datetime.day and
                       node.create_datetime.hour == current_datetime.hour - 1 and
                       node.create_datetime.minute == current_datetime.minute)
        
        if same_minute:
            # Safely delete object created during test 
            spi.deleteSpecifyObject('taxon', node.id)

    assert passed

    return passed

def test_addSynonymRow():
    """ Test adding accepted row """
    
    row = syn_row
    
    taxon_headers = headers[:headers.index('SpeciesAuthor')]

    ranks = []
    for header in taxon_headers:
        ranks.append(header)
        if header == 'SpeciesAuthor': break
    ranks.reverse()

    node = tool.addChildNodes(taxon_headers, row, 1, 0)

    assert node
    passed = True
 
    taxon = spi.getSpecifyObject('taxon', node.id)
    assert taxon 

    taxon_id = taxon['id']

    # Check presence of each node
    nodes = []
    for rank in ranks:   
        obj = spi.getSpecifyObject('taxon', taxon_id)
        assert obj # node present
        node = TreeNode.init(obj)
        nodes.append(node)
        taxon_id = node.parent_id # prepare for next loop  

        # Check field value
        assert row[rank] == node.name

        # TODO Check synonymy
        assert node.is_accepted == False


    # Clean up afterwards
    for node in nodes: 
        # Check if each nodes was just created: 
        current_datetime = datetime.datetime.now()
        same_minute = (node.create_datetime.year == current_datetime.year and
                       node.create_datetime.month == current_datetime.month and
                       node.create_datetime.day == current_datetime.day and
                       node.create_datetime.hour == current_datetime.hour - 1 and
                       node.create_datetime.minute == current_datetime.minute)
        
        if same_minute:
            # Safely delete object created during test 
            spi.deleteSpecifyObject('taxon', node.id)

    assert passed

    return passed

def test_runTool():
    """ Test whether nodes were added as expected and cleaned up again """
    pass




