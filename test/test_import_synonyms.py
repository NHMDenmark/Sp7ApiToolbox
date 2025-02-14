import csv
import datetime 
import configuration
import specify_interface as sp
from models.treenode import TreeNode
from models.taxon import Taxon
import tools.treenode_tool
import tools.import_synonyms

cfg = configuration.ConfigurationHandler()
cfg.loadConfiguration('unit')
cfg.loadTools()

spi = sp.SpecifyInterface()

tool = tools.import_synonyms.ImportSynonymTool(spi)

base_row = {'Kingdom':'Animalia','Phylum':'Chordata','Class': 'Mammalia', 'Order': 'Carnivora', 'Family': 'Otariidae', 
           'Genus' : 'Eumetopias', 'Species' : 'jubatus', 'SpeciesAuthor' : 'Schreber, 1776'}
 
acc_ext = {'isAccepted' : 'Yes', 'AcceptedGenus' : '', 'AcceptedSpecies' : '','AcceptedSpeciesAuthor' : ''}
#syn_ext = {'isAccepted' : 'No', 'AcceptedGenus' : 'Eumetopias', 'AcceptedSpecies' : 'jubatus','AcceptedSpeciesAuthor' : 'Schreber, 1776'}

acc_row = {**base_row, **acc_ext}
#syn_row = {**base_row, **syn_ext}
syn_row = {'Kingdom':'Animalia','Phylum':'Chordata','Class':'Reptilia','Order':'Squamata','Family':'Typhlopidae',
           'Genus':'Gampsosteonyx','Species':'batesi','SpeciesAuthor':'"Boulenger, 1900"','Subspecies':'','SubspeciesAuthor':'',
           'isAccepted':'No','AcceptedGenus':'Afrotyphlops','AcceptedSpecies':'lineolatus','AcceptedSpeciesAuthor':'"(Jan, 1864) "',
           'AcceptedSubspecies':'','AcceptedSubspeciesAuthor':''
           }

ssp_row = {'Kingdom':'Animalia','Phylum':'Chordata','Class':'Amphibia','Order':'Anura','Family': 'Hyperoliidae',
           'Genus':'Hyperolius','Species':'castaneus','SpeciesAuthor':'','Subspecies':'submarginatus','SubspeciesAuthor':'',
           'isAccepted':'No','AcceptedGenus':'Hyperolius','AcceptedSpecies':'constellatus','AcceptedSpeciesAuthor':'Laurent, 1951',
           'AcceptedSubspecies':'','AcceptedSubspeciesAuthor':''}

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

def test_createAcceptedTaxonTreeNode():
    """ Test creating an accepted taxon tree node """
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

def test_createSynonymTaxonTreeNode():
    """ Test creating an accepted taxon tree node """
    row = syn_row
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
        node = Taxon.init(obj)
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
        node = Taxon.init(obj)
        nodes.append(node)
        taxon_id = node.parent_id # prepare for next loop  

        # Check field value
        assert row[rank] == node.name

        # TODO Check synonymy
        if rank == 'Species':
            assert node.is_accepted == False
            acc_obj = spi.getSpecifyObject('taxon', node.accepted_taxon_id.split('/')[4])
            acc_node = Taxon.init(acc_obj)
            nodes.append(acc_node)

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

def test_addSubspeciesSynonymRow():
    """ Test adding accepted row """
    
    row = ssp_row
    
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
        node = Taxon.init(obj)
        nodes.append(node)
        taxon_id = node.parent_id # prepare for next loop  

        # Check field value
        assert row[rank] == node.name

        # TODO Check synonymy
        if rank == 'Subspecies':
            assert node.is_accepted == False
            acc_obj = spi.getSpecifyObject('taxon', node.accepted_taxon_id.split('/')[4])
            acc_node = Taxon.init(acc_obj)
            nodes.append(acc_node)

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

def test_validateRow():
    """ Test validating a row """
    row = {'Kingdom': 'Animalia', 'Phylum': 'Chordata', 'Class': 'Mammalia', 'Order': 'Carnivora', 'Family': 'Otariidae', 
            'Genus': 'Eumetopias', 'Species': 'jubatus', 'SpeciesAuthor': 'Schreber, 1776', 'isAccepted': 'Yes', 
            'AcceptedGenus': '', 'AcceptedSpecies': '', 'AcceptedSpeciesAuthor': ''}
    
    valid = tool.validateRow(row)
    assert valid

def test_validateHeaders():
    """ Test validating headers """
    headers = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'SpeciesAuthor', 'isAccepted', 'AcceptedGenus', 'AcceptedSpecies', 'AcceptedSpeciesAuthor']
    
    valid = tool.validateHeaders(headers)
    assert valid
 
def test_processAcceptedRow():
    """ Test processing a row """
    headers = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'SpeciesAuthor', 'isAccepted', 'AcceptedGenus', 'AcceptedSpecies', 'AcceptedSpeciesAuthor']
    row = {'Kingdom': 'Animalia', 'Phylum': 'Chordata', 'Class': 'Mammalia', 'Order': 'Carnivora', 'Family': 'Otariidae', 
            'Genus': 'Eumetopias', 'Species': 'jubatus', 'SpeciesAuthor': 'Schreber, 1776', 'isAccepted': 'Yes', 
            'AcceptedGenus': '', 'AcceptedSpecies': '', 'AcceptedSpeciesAuthor': ''}
    
    tool.processRow(headers, row)
    
    # Verify that the nodes were added correctly
    taxa = spi.getSpecifyObjects('taxon', filters={'fullname': 'Eumetopias jubatus', 'author': 'Schreber, 1776'})
    assert taxa
    assert taxa.__len__() > 0
    taxon = taxa[0]
    assert taxon
    assert taxon['name'] == 'jubatus'
    assert taxon['fullname'] == 'Eumetopias jubatus'
    assert taxon['author'] == 'Schreber, 1776'
    assert taxon['isaccepted'] == True

def test_processSynonymRow():
    """Test processing a taxonomic synonym row and verify its correct insertion."""
    # Define the headers and a sample row of taxonomic data
    headers = [
        'Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species',
        'SpeciesAuthor', 'isAccepted', 'AcceptedGenus', 'AcceptedSpecies', 'AcceptedSpeciesAuthor'
    ]
    row = {
        'Kingdom': 'Animalia',
        'Phylum': 'Chordata',
        'Class': 'Amphibia',
        'Order': 'Anura',
        'Family': 'Arthroleptidae',
        'Genus': 'Arthroleptis',
        'Species': 'stenodactylus',
        'SpeciesAuthor': 'Smith, 1849',
        'isAccepted': 'No',
        'AcceptedGenus': 'Arthroleptis',
        'AcceptedSpecies': 'stenodactylus',
        'AcceptedSpeciesAuthor': 'Pfeffer, 1893'
    }

    # Process the row using the tool's processRow method
    tool.processRow(headers, row)

    # Retrieve the processed taxon from the data store
    taxa = spi.getSpecifyObjects('taxon', filters={'fullname': 'Arthroleptis stenodactylus', 'author': 'Pfeffer, 1893'})

    # Verify that the taxon was added correctly
    assert taxa, "No taxa found for the given filters."
    taxon = taxa[0]
    assert taxon['name'] == 'Arthroleptis', f"Expected 'Arthroleptis', but got {taxon['name']}"
    assert taxon['fullname'] == 'Arthroleptis stenodactylus', f"Expected 'Arthroleptis stenodactylus', but got {taxon['fullname']}"
    assert taxon['author'] == 'Pfeffer, 1893', f"Expected 'Pfeffer, 1893', but got {taxon['author']}"
    assert taxon['isaccepted'] is False, f"Expected False, but got {taxon['isaccepted']}"
    assert taxon['acceptedtaxon'] is not None, "Accepted taxon is None."


def test_runTool():
    """ 
    Test whether nodes were added as expected and cleaned up again 
    """
    filename = 'import_synonyms.csv'
    tool.runTool({'filename':filename, 'sptype':'taxon'})

    # Read the CSV file
    with open(f'data/{filename}', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Extract the taxon name and other relevant fields
            taxon_name = row['Species'] if row['Species'] else row['Genus']
            parent_name = row['Genus'] if row['Species'] else row['Family']
            
            # Fetch the added node from the Specify API
            filters = {'name': taxon_name}
            if parent_name:
                result = spi.getSpecifyObjects('taxon', filters={'name': parent_name})
                if result:
                    parent_node = result[0]
                    filters['parent'] = parent_node['id']
            
                    added_nodes = spi.getSpecifyObjects('taxon', filters=filters)
                    
                    # Check that the node was added
                    assert len(added_nodes) > 0, f"Node {taxon_name} not found"
                    
                    # Verify the node's attributes
                    added_node = added_nodes[0]
                    assert added_node['name'] == taxon_name, f"Expected name {taxon_name}, got {added_node['name']}"
                    assert added_node['fullname'] == row['SpeciesAuthor'], f"Expected fullname {row['SpeciesAuthor']}, got {added_node['fullname']}"
                    assert added_node['author'] == row['SpeciesAuthor'], f"Expected author {row['SpeciesAuthor']}, got {added_node['author']}"
                    assert added_node['isaccepted'] == (row['isAccepted'] == 'Yes'), f"Expected isaccepted {row['isAccepted']}, got {added_node['isaccepted']}"
                    
                    # Additional checks for synonyms
                    if row['isAccepted'] == 'No':
                        assert added_node['acceptedtaxon'] is not None, f"Expected acceptedtaxon for {taxon_name}, got None"
                        accepted_taxon = spi.getSpecifyObjects('taxon', filters={'id': added_node['acceptedtaxon'].split('/')[-2]})[0]
                        assert accepted_taxon['name'] == row['AcceptedSpecies'], f"Expected accepted species {row['AcceptedSpecies']}, got {accepted_taxon['name']}"
                else:
                    print(f"Problem fetching parent node: {parent_name}")
                    assert False
            
    print("All nodes were added and verified successfully.")
   

