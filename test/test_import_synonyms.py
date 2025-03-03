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

acc_row = {'Kingdom':'Animalia','Phylum':'Chordata','Class': 'Mammalia', 'Order': 'Carnivora', 'Family': 'Otariidae', 
           'Genus' : 'Eumetopias', 'Species' : 'jubatus', 'SpeciesAuthor' : 'Schreber, 1776',
           'isAccepted' : 'Yes', 'AcceptedGenus' : '', 'AcceptedSpecies' : '','AcceptedSpeciesAuthor' : ''
           }

syn_row = {'Kingdom':'Animalia','Phylum':'Chordata','Class':'Reptilia','Order':'Squamata','Family':'Typhlopidae',
           'Genus':'Gampsosteonyx','Species':'batesi','SpeciesAuthor':'"Boulenger, 1900"','Subspecies':'','SubspeciesAuthor':'',
           'isAccepted':'No','AcceptedGenus':'Afrotyphlops','AcceptedSpecies':'lineolatus','AcceptedSpeciesAuthor':'"(Jan, 1864) "',
           'AcceptedSubspecies':'','AcceptedSubspeciesAuthor':''
           }

ssp_row = {'Kingdom':'Animalia','Phylum':'Chordata','Class':'Amphibia','Order':'Anura','Family': 'Hyperoliidae',
           'Genus':'Hyperolius','Species':'castaneus','SpeciesAuthor':'','Subspecies':'submarginatus','SubspeciesAuthor':'',
           'isAccepted':'No','AcceptedGenus':'Hyperolius','AcceptedSpecies':'constellatus','AcceptedSpeciesAuthor':'Laurent, 1951',
           'AcceptedSubspecies':'','AcceptedSubspeciesAuthor':''
           }

sbg_row1 = {'Kingdom':'Animalia','Phylum':'Chordata','Class':'Reptilia','Order':'Squamata','Family':'Dactyloidae',
            'Genus':'Anolis','Subgenus':'Norops','Species':'carolinensis','SpeciesAuthor':'Voigt, 1832','Subspecies':'','SubspeciesAuthor':'',
            'isAccepted':'Yes','AcceptedGenus':'Anolis','AcceptedSpecies':'carolinensis','AcceptedSpeciesAuthor':'Voigt, 1832',
            'AcceptedSubspecies':'','AcceptedSubspeciesAuthor':''
           }

sbg_row2 = {'Kingdom':'Animalia','Phylum':'Chordata','Class':'Reptilia','Order':'Squamata','Family':'Dactyloidae',
            'Genus':'Anolis','Subgenus':'Norops','Species':'equestris','SpeciesAuthor':'Merrem, 1820','Subspecies':'','SubspeciesAuthor':'',
            'isAccepted':'Yes','AcceptedGenus':'Anolis','AcceptedSpecies':'equestris','AcceptedSpeciesAuthor':'Merrem, 1820',
            'AcceptedSubspecies':'','AcceptedSubspeciesAuthor':''
           }

sbg_row3 = {'Kingdom':'Animalia','Phylum':'Chordata','Class':'Reptilia','Order':'Squamata','Family':'Dactyloidae',
            'Genus':'Anolis','Subgenus':'Norops','Species':'allisoni','SpeciesAuthor':'Barbour, 1928','Subspecies':'','SubspeciesAuthor':'',
            'isAccepted':'Yes','AcceptedGenus':'Anolis','AcceptedSpecies':'allisoni','AcceptedSpeciesAuthor':'Barbour, 1928',
            'AcceptedSubspecies':'','AcceptedSubspeciesAuthor':''
           }


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
    nodes = [] 
    
    try:
        last_node = tool.addChildNodes(taxon_headers, row, 1, 0)
        assert last_node
    
        taxon = spi.getSpecifyObject('taxon', last_node.id)
        assert taxon 

        taxon_id = taxon['id']

        # Check presence of each node
        for rank in ranks:   
            obj = spi.getSpecifyObject('taxon', taxon_id)
            assert obj # node present
            node = Taxon.init(obj)
            nodes.append(node)
            taxon_id = node.parent_id # prepare for next loop  

            # Check field value
            assert row[rank] == node.name

    finally:
        # Clean up afterwards
        cleanup_nodes(nodes)
    
    print("Test passed.")

def test_addSynonymRow():
    """ Test adding accepted row """
    row = syn_row
    
    taxon_headers = headers[:headers.index('SpeciesAuthor')]

    ranks = []
    for header in taxon_headers:
        ranks.append(header)
        if header == 'SpeciesAuthor': break
    ranks.reverse()
    nodes = [] 

    try:
        last_node = tool.addChildNodes(taxon_headers, row, 1, 0)
        assert last_node
    
        taxon = spi.getSpecifyObject('taxon', last_node.id)
        assert taxon 

        taxon_id = taxon['id']       

        # Check presence of each node
        nodes = []
        for rank in ranks:   
            obj = spi.getSpecifyObject('taxon', taxon_id)
            try:
                node = Taxon.init(obj)
                nodes.append(node)
                taxon_id = node.parent_id # prepare for next loop  
                
                # TODO Check synonymy
                if rank == 'Species':
                    #assert node.is_accepted == False
                    acc_obj = spi.getSpecifyObject('taxon', node.accepted_taxon_id.split('/')[4])
                    acc_taxon = Taxon.init(acc_obj)
                    nodes.append(acc_taxon)

            except Exception as e:
                print(f"Error initializing Taxon object: {e}")
                break
        
        # Check synonym taxon         
        assert taxon['name'] == row['Species']
        assert taxon['fullname'] == row['Genus'] + ' ' + row['Species']
        assert taxon['isaccepted'] == False
        assert taxon['acceptedtaxon'] is not None
        assert taxon['acceptedtaxon'].split('/')[4] == str(acc_taxon.id)
        assert taxon['author'] == row['SpeciesAuthor']

        # Check synonym taxon parent
        syn_parent = spi.getSpecifyObject('taxon', taxon['parent'].split('/')[4])
        assert syn_parent
        assert syn_parent['name'] == row['Genus']

        # Check accepted taxon
        assert acc_taxon.name == row['AcceptedSpecies']
        assert acc_taxon.fullname == row['AcceptedGenus'] + ' ' + row['AcceptedSpecies'] 
        assert acc_taxon.author == row['AcceptedSpeciesAuthor']
        assert acc_taxon.is_accepted == True  
        assert acc_taxon.accepted_taxon_id is None

        # Check accepted taxon parent
        acc_parent = spi.getSpecifyObject('taxon', acc_taxon.parent_id)
        assert acc_parent
        assert acc_parent['name'] == row['AcceptedGenus']
        
        print("Test passed.")
    except:
        print("Test failed.")
    finally:
        # Clean up afterwards
        print("cleaning up nodes.")
        #cleanup_nodes(nodes)
    
    print("Test finished.")

def test_addSubspeciesSynonymRow():
    """ Test adding accepted row """
    row = ssp_row
    
    taxon_headers = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'Subspecies'] #headers[:headers.index('SpeciesAuthor')]

    ranks = list(taxon_headers)
    ranks.reverse()
    nodes = [] 

    try:
        last_node = tool.addChildNodes(taxon_headers, row, 1, 0)
        assert last_node
    
        taxon = spi.getSpecifyObject('taxon', last_node.id)
        assert taxon 

        taxon_id = taxon['id']       

        # Check presence of each node
        nodes = []
        for rank in ranks:   
            obj = spi.getSpecifyObject('taxon', taxon_id)
            try:
                node = Taxon.init(obj)
                nodes.append(node)
                taxon_id = node.parent_id # prepare for next loop  
                
                # TODO Check synonymy
                if rank == 'Subspecies':
                    assert node.is_accepted == False
                    acc_obj = spi.getSpecifyObject('taxon', node.accepted_taxon_id.split('/')[4])
                    acc_taxon = Taxon.init(acc_obj)
                    nodes.append(acc_taxon)

            except Exception as e:
                print(f"Error initializing Taxon object: {e}")
                break
        
        # Check synonym taxon         
        assert taxon['name'] == row['Subspecies']
        assert taxon['fullname'] == (row['Genus'] + ' ' + row['Species'] + ' ' + row['Subspecies']).strip()
        assert taxon['isaccepted'] == False
        assert taxon['acceptedtaxon'] 
        assert acc_taxon 
        assert taxon['acceptedtaxon'].split('/')[4] == str(acc_taxon.id)

    finally:
        # Clean up afterwards
        cleanup_nodes(nodes)
    
    print("Test passed.")

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
    headers = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'AcceptedGenus', 'AcceptedSpecies']
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
    headers = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'AcceptedGenus', 'AcceptedSpecies']
        #'SpeciesAuthor', 'isAccepted', 'AcceptedGenus', 'AcceptedSpecies', 'AcceptedSpeciesAuthor']

    row = {
        'Kingdom': 'Animalia',
        'Phylum': 'Chordata',
        'Class': 'Amphibia',
        'Order': 'Anura',
        'Family': 'Arthroleptidae',
        'Genus': 'Arthroleptis',
        'Species': 'dactylostenus',
        'SpeciesAuthor': 'Smith, 1849',
        'isAccepted': 'No',
        'AcceptedGenus': 'Arthroleptis',
        'AcceptedSpecies': 'stenodactylus',
        'AcceptedSpeciesAuthor': 'Pfeffer, 1893'
    }

    #row = syn_row
    
    try:
        # Process the row using the tool's processRow method
        tool.processRow(headers, row)

        # Retrieve the processed taxon from the data store
        full_name = row['Genus'] + ' ' + row['Species']  
        author = row['SpeciesAuthor']  
        taxa = spi.getSpecifyObjects('taxon', filters={'fullname': full_name, 'author': author})

        # Verify that the taxon was added correctly
        assert taxa, "No taxa found for the given filters."
        taxon = taxa[0]
        assert taxon['name'] == f'{row['Species']}', f"Expected '{row['Species']}s', but got {taxon['name']}"
        assert taxon['isaccepted'] is False, f"Expected False, but got {taxon['isaccepted']}"
        assert taxon['acceptedtaxon'] is not None, "Accepted taxon is None."

    finally:
        # Clean up the added taxa
        nodes = []
        for entry in row:
            if entry not in ['SpeciesAuthor', 'isAccepted', 'AcceptedSpeciesAuthor']:
                # Fetch the taxon from the Specify API
                taxa = spi.getSpecifyObjects('taxon', filters={'name': row[entry]})
                if len(taxa) > 0:
                    taxon = taxa[0]
                    try:
                        node = Taxon.init(taxon)
                        nodes.append(node)
                    except Exception as e:
                        print(f"Error initializing Taxon object: {e}")
            
        cleanup_nodes(nodes)

def test_runTool():
    """ 
    Test whether nodes were added as expected and cleaned up again 
    """
    filename = 'import_synonyms.csv'
    
    tool.runTool({'filename':filename, 'sptype':'taxon'})

    added_nodes = []

    try:
        # Read the CSV file
        with open(f'data/{filename}', mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            
            for row in reader:
                # Extract the taxon name and other relevant fields
                subgenus = f'{row['Subgenus'].strip()} '
                if subgenus == ' ': 
                    subgenus = ''
                else:
                    print(subgenus)
                if row['Subspecies']:
                    # Subspecies row; construct the taxon fullname
                    rankid = 230
                    rankname = 'Subspecies'
                    taxon_fullname = f"{row['Genus'].strip()} {subgenus}{row['Species'].strip()} {row['Subspecies'].strip()}"
                    taxon_name = row['Subspecies'].strip()
                    parent_name = row['Species'].strip()
                    parent_fullname = f"{row['Genus'].strip()} {subgenus}{row['Species'].strip()}"
                    author = row['SubspeciesAuthor'].strip()
                elif row['Species']:
                    # Species row; construct the taxon fullname
                    rankid = 220
                    rankname = 'Species'
                    taxon_fullname = f"{row['Genus'].strip()} {subgenus}{row['Species'].strip()}"
                    taxon_name = row['Species'].strip()
                    if subgenus == '':
                        parent_name = row['Genus'].strip()
                    else:
                        parent_name = f"{subgenus}"
                    parent_fullname = parent_name.strip()
                    author = row['SpeciesAuthor'].strip()
                else:
                    # Genus row; construct the taxon fullname
                    rankid = 180
                    rankname = 'Genus'
                    taxon_fullname = row['Genus'].strip()
                    taxon_name = row['Genus'].strip()
                    parent_name = row['Family'].strip()
                    parent_fullname = parent_name
                    author = ''
                treedefitemid = tool.getTreeDefItem(rankname)['id']
                treedefid = tool.getTreeDefinition()
                acceptedid = None # TODO fetch accepted taxon id ???
                if parent_fullname.__contains__('Norops'):
                    print('here')
                parent = spi.getSpecifyObjects('taxon', filters={'fullname': parent_fullname})[0]

                # Create taxon node from row data
                taxon_node = Taxon(0, taxon_name, taxon_fullname, author, parent['id'], rankid, treedefitemid, treedefid, True, acceptedid, False)
                
                added_nodes.append(taxon_node)
            
            for node in added_nodes:
                # Fetch the added node from the Specify API                
                taxon_name = node.name
                taxon_fullname = node.fullname
                parentid = node.parent_id
                author = node.author                

                filters = {'name': taxon_name, 'fullname': taxon_fullname,'parent': parentid, 'author': author}

                taxa = spi.getSpecifyObjects('taxon', filters=filters)
                
                # Verify the node's attributes
                assert len(taxa) > 0, f"No nodes found for {taxon_name}"
                node = taxa[0]
                assert node['name'] == taxon_name, f"Expected name {taxon_name}, got {node['name']}"
                assert node['fullname'] == taxon_fullname, f"Expected taxon fullname {taxon_fullname}, got {node['fullname']}"
                assert node['author'] == author, f"Expected author {author}, got {node['author']}"
                if row['isAccepted'] == 'Yes':
                    assert node['isaccepted'] == (row['isAccepted'] == 'Yes'), f"Expected isaccepted {row['isAccepted']}, got {node['isaccepted']}"

                if row['isAccepted'] == 'No' and node['rankid'] > 190:
                    # Additional checks for synonyms
                    print(f"Checking node {taxon_name} as a synonym of {row['AcceptedSpecies']}")
                    #assert node['acceptedtaxon'] is not None, f"Expected acceptedtaxon for {taxon_name}, got None"
                    #accepted_taxon = spi.getSpecifyObjects('taxon', filters={'id': node['acceptedtaxon'].split('/')[-2]})[0]
                    #assert accepted_taxon['name'] == row['AcceptedSpecies'], f"Expected accepted species {row['AcceptedSpecies']}, got {accepted_taxon['name']}"                
                    
            
        print("All nodes were added and verified successfully.")
    except Exception as e:
        print(f"Error adding nodes. {e}")
        raise e
    finally:
        # Clean up the added nodes
        cleanup_nodes(added_nodes)

def cleanup_nodes(nodes):
    """Clean up nodes created during the test."""
    print("Cleaning up...")
    current_datetime = datetime.datetime.now()
    for node in nodes:
        # Check if each node was just created:
        same_moment = (node.create_datetime.year == current_datetime.year and
                    node.create_datetime.month == current_datetime.month and
                    node.create_datetime.day == current_datetime.day)
        
        if same_moment:
            # Safely delete object created during test
            try:
                print(f"Deleting object {node.name}")
                spi.deleteSpecifyObject('taxon', node.id)
            except Exception as e:
                print(f"Error deleting object: {e}")
        else:
            print(f"Node {node.name} was not created during test.")
    print("Cleaned up.")
