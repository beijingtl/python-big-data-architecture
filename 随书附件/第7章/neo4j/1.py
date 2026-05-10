# pip3 install neo4j-driver
# python3 example.py

from neo4j import GraphDatabase, basic_auth

driver = GraphDatabase.driver(
  "bolt://34.201.57.241:7687",
  auth=basic_auth("neo4j", "reproduction-credit-speeds"))

cypher_query = '''
MATCH (movie:Movie {title:$favorite})<-[:ACTED_IN]-(actor)-[:ACTED_IN]->(rec:Movie)
 RETURN distinct rec.title as title LIMIT 20
'''

with driver.session(database="neo4j") as session:
  results = session.read_transaction(
    lambda tx: tx.run(cypher_query,
                      favorite="The Matrix").data())
  for record in results:
    print(record['title'])

driver.close()
