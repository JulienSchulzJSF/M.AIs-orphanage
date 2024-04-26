from neo4j import *

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

query = "MATCH (n) RETURN n LIMIT 10"
results = conn.run_query(query)


for record in results:
   print(record)


conn.close()
