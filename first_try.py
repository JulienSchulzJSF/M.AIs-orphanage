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

uri = "bolt://83.229.84.12:7687"
user = "tumaiReadonly"
password = "MAKEATHON2024"
database = "graph2.db"

conn = Neo4jConnection(uri, user, password, database)

get_train_data_query = "MATCH (bs:Biological_sample)-[r:HAS_DISEASE]->(d:Disease) WHERE NOT d.name 'control' RETURN bs,r,d"
get_control_query = "MATCH (bs:Biological_sample)-[r:HAS_DISEASE]-> (d:Disease {name: 'control'}) RETURN bs,r,d"

# parse results from graph to csv
get_results_query = "MATCH (bs:Biological_sample)-[r:HAS_DISEASE]->(d:Disease) RETURN bs.subjectid,d.name"
results = conn.run_query(get_results_query)

subject_id = []
disease = []

for record in results:
    subject_id.append(record["bs.subjectid"])
    if record["d.name"] == "control":
        disease.append(0)
    else:
        disease.append(1)

results_df = pd.DataFrame({"subject_id": subject_id, "disease":disease})

results_df.to_csv("./data/training_data.csv", index=False)

conn.close()
