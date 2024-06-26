from typing import Tuple
from neo4j import GraphDatabase, Driver
import torch
from torch_geometric.data import Data

class Neo4jConnection:
    def __init__(self, uri, user, password, database):
        self.driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self.database = database

    def close(self):
        self.driver.close()

    def run_query(self, query):
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            return result

# global variables
nodes = {
    'Biological_sample': [],
    'Protein': [],
    'Gene': [],
    'Disease': []
}

relationship_to_edge  = {
    'HAS_DAMAGE': 'Biological_sample-Gene',
    'HAS_PROTEIN': 'Biological_sample-Protein',
    'TRANSLATED_INTO':'Gene-Protein',
    'ASSOCIATED_WITH':'Protein-Disease-Associated',
    'IS_BIOMARKER_OF_DISEASE':'Protein-Disease-Biomarker'
}

edges = {
    'Biological_sample-Gene': [],
    'Biological_sample-Protein': [],
    'Gene-Protein': [],
    'Protein-Disease-Associated': [],
    'Protein-Disease-Biomarker': []
}

source_nodes = []
target_nodes = []
edge_types = []
node_types = []

def connect_to_db() -> Neo4jConnection:
    uri = "bolt://83.229.84.12:7687"
    user = "tumaiReadonly"
    password = "MAKEATHON2024"
    database = "graph2.db"
    conn = Neo4jConnection(uri, user, password, database)
    return conn

def close_connection_to_db(database: Neo4jConnection):
    database.close()

def query_db(database: Neo4jConnection, query: str, filename: str):
    results = database.run_query(query)
    return results

def convert_result_to_lists(result, nodes, edge):
    global source_nodes, target_nodes, edge_types, node_types
    for record in result:
        """source_ids =  nodes[record["source_type"][0]] 
        target_ids =  nodes[record["target_type"][0]] 

        if record["target"] not in target_ids:
            target_ids.append(record["target"])
            nodes[record["target_type"][0]] = target_ids
        
        if record["source"] not in source_ids:
            source_ids.append(record["source"])
            nodes[record["source_type"][0]] = source_ids
        
        edges[relationship_to_edge[record["edge_type"]]].append((record["source"],record["target"]))"""

        source_nodes.append(record["source"])
        target_nodes.append(record["target"])
        edge_types.append(record["edge_type"])
        node_types.append(record["node_type"][0])  # Assuming each node has exactly one label

def create_data() -> Data:
    # lists to tensor
    edge_index = torch.tensor([source_nodes, target_nodes], dtype=torch.long)
    edge_type = torch.tensor(edge_types, dtype=torch.long)
    x = torch.tensor(node_features, dtype=torch.float)
    node_type = torch.tensor(node_types, dtype=torch.long)
    # tensor to Data object
    data = Data(x=x, edge_index=edge_index, edge_attr=edge_type, node_type=node_type)

    return data


def runner_data_generation():
    conn = connect_to_db()

    # relationship bs to gene and protein
    convert_result_to_lists(query_db(conn,"Biological_sample", "" "MATCH (bs:Biological_sample)-[r:HAS_PROTEIN|HAS_DAMAGE]-(related_node) RETURN id(bs) as source, labels(bs) as node_type,type(r) as edge_type, bs.features as node_features, id(related_node) as target"))
    # relationship gene to protein
    convert_result_to_lists(query_db(conn, "MATCH (g:Gene)-[r:TRANSLATED_INTO]-(p:Protein) RETURN id(g) as source, labels(g) as node_type,type(r) as edge_type, id(p) as target"))
    # relationship disease to protein
    convert_result_to_lists(query_db(conn, "MATCH (d:Disease)-[r:ASSOCIATED_WITH|IS_BIOMARKER_OF_DISEASE]-(p:Protein) RETURN CASE WHEN d.name = 'control' THEN 0 ELSE 1 END AS source, labels(d) as node_type,type(r) as edge_type, id(p) as target"))

    close_connection_to_db(conn)

    return create_data()



    


