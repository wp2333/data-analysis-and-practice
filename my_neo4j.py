from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable

class App:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def create_friendship(self, person1_name, person2_name):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_friendship, person1_name, person2_name)
            for row in result:
                print("Created friendship between: {p1}, {p2}".format(p1=row['p1'], p2=row['p2']))

    @staticmethod
    def _create_and_return_friendship(tx, person1_name, person2_name):
        # To learn more about the Cypher syntax, see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords https://neo4j.com/docs/cypher-refcard/current/
        query = (
            "CREATE (p1:Person { name: $person1_name }) "
            "CREATE (p2:Person { name: $person2_name }) "
            "CREATE (p1)-[:KNOWS]->(p2) "
            "RETURN p1, p2"
        )
        result = tx.run(query, person1_name=person1_name, person2_name=person2_name)
        try:
            return [{"p1": row["p1"]["name"], "p2": row["p2"]["name"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def find_person(self, person_name):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_person, person_name)
            for row in result:
                print("Found person: {row}".format(row=row))

    @staticmethod
    def _find_and_return_person(tx, person_name):
        query = (
            "MATCH (p:Person) "
            "WHERE p.name = $person_name "
            "RETURN p.name AS name"
        )
        result = tx.run(query, person_name=person_name)
        return [row["name"] for row in result]

    def create_movie(self, movie_title, movie_No):
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_movie, movie_title, movie_No)
            for row in result:
                print("Created movie: {m}".format(m=row['m']))
    
    @staticmethod
    def _create_movie(tx, movie_title, movie_No):
        query = (
            "CREATE (m:Movie { title: $movie_title, No: $movie_No }) "
            "RETURN m"
        )
        result = tx.run(query, movie_title=movie_title, movie_No=movie_No)
        try:
            return [{"m": row["m"]["title"]}
                    for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def create_movie_recommendation(self, m1_title, m2_title):
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_and_return_recommendation, m1_title, m2_title)
            for row in result:
                print("Created recommendation between: {m1}, {m2}".format(m1=row['m1'], m2=row['m2']))

    @staticmethod
    def _create_and_return_recommendation(tx, m1_No, m2_No):
        query = (
            "MATCH (m1:Movie) "
            "WHERE m1.No = $m1_No "
            "OPTIONAL MATCH (m2:Movie) "
            "WHERE m2.No = $m2_No "
            "CREATE (m1)-[r:Recommended]->(m2) "
            "RETURN m1,m2"
        )
        result = tx.run(query, m1_No=m1_No, m2_No=m2_No)
        try:
            return [{"m1": row["m1"]["title"], "m2": row["m2"]["title"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def delete_all(self):
        with self.driver.session() as session:
            result = session.write_transaction(
                self._delete_all)
            # print(result)
    
    @staticmethod
    def _delete_all(tx):
        query = (
            "match (n) optional match (n)-[r]-() delete n,r"
        )
        result = tx.run(query)
        try:
            return result
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

def neo_login():
    uri = "neo4j+s://dc30ec7d.databases.neo4j.io"
    user = "neo4j"
    password = "jX4k6e9P-b7is1cnuw88egr8mMi9KrJaxVnf1rFWjbE"
    app = App(uri, user, password)
    return app

if __name__ == "__main__":
    app=neo_login()
    app.create_movie("abc", "594")
    app.create_movie("def", "578")
    app.create_movie_recommendation("594", "578")
    app.delete_all()
    app.close()
# jX4k6e9P-b7is1cnuw88egr8mMi9KrJaxVnf1rFWjbE