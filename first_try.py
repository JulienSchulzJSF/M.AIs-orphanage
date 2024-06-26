from typing import Tuple
from neo4j import GraphDatabase
import pandas as pd

"""
This script can query the database to get subject_id from the biological_sample and the name from the disease node
and saves the subject_id in one col and 0 for control or 1 for diseased in an other col to a csv.
"""

class Neo4jConnection:
    def __init__(self, uri, user, password, database):
        self.driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self.database = database

    def close(self):
        self.driver.close()

    def run_query(self, query):
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            return [record for record in result]
        
def connect_to_db():
    uri = "bolt://83.229.84.12:7687"
    user = "tumaiReadonly"
    password = "MAKEATHON2024"
    database = "graph2.db"
    conn = Neo4jConnection(uri, user, password, database)
    return conn

def close_connection_to_db(database: Neo4jConnection):
    database.close()

def parse_query_data(results: list) -> Tuple[list,list]:
    """
    Parses query data into list with
    """
    subject_id = []
    disease = []
    for record in results:
        subject_id.append(record["bs.subjectid"])
        if record["d.name"] == "control":
            disease.append(0)
        else:
            disease.append(1)
    return subject_id, disease

def result_to_csv(subject_id: list, disease: list, filename: str):
    results_df = pd.DataFrame({"subject_id": subject_id, "disease":disease})

    results_df.to_csv("./data/"+filename, index=False)

def extract_data(database: Neo4jConnection, query: str, filename: str):
    results = database.run_query(query)

    

    subject_id, disease = parse_query_data(results)
    result_to_csv(subject_id, disease, filename)

if __name__ == "__main__":
    get_train_query = "MATCH (bs:Biological_sample)-[r:HAS_DISEASE]->(d:Disease) WHERE NOT d.name = 'control' RETURN bs.subjectid,d.name"
    get_control_query = "MATCH (bs:Biological_sample)-[r:HAS_DISEASE]-> (d:Disease {name: 'control'}) RETURN bs.subjectid,d.name"
    get_results_query = "MATCH (bs:Biological_sample)-[r:HAS_DISEASE]->(d:Disease) RETURN bs.subjectid,d.name"

    database = connect_to_db()

    extract_data(database, get_train_query, "train_data.csv")
    extract_data(database, get_control_query, "control_data.csv")
    extract_data(database, get_results_query, "results_data.csv")

    close_connection_to_db(database)


