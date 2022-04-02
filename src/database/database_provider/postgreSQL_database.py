# from database.database_provider import DatabaseProvider
from src.database.exceptions.DBException import DBException
import logging
import psycopg2

class PostgreSQLDatabaseProvider():
    """
        concrete implementation of DatabaseProvider, using postgreSQL
    """
    def __init__(self, databaseCredentials):
        self.conn = "None"
        try:
            self.conn = psycopg2.connect(
                database=databaseCredentials['databaseName'],
                user=databaseCredentials['user'],
                password=databaseCredentials['password'],
                host=databaseCredentials['host'],
                port=databaseCredentials['port']
            )
        # if database is unable to connect, then the server is closed.
        except Exception as e:
            raise DBException(e)
            exit(1)
        logging.debug("Connected to the PostgreSQL database")

    def insert(self, query, params =None):
        try:
            cur = self.conn.cursor()
            cur.execute(query, params)
            self.conn.commit()
            cur.close()
        except Exception as e:
            raise DBException(e)

    def fetchAll(self, query, params= None):
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            raise DBException(e)

    def fetchOne(self, query, params=None):
        try:
            cur = self.conn.cursor()
            cur.execute(query, params)
            row = cur.fetchone()
            cur.close()
            return row
            
        except Exception as e:
            raise DBException(e)


    def createTable(self, query):
        try:
            logging.debug(query)
            cur = self.conn.cursor()
            cur.execute(query)
            self.conn.commit()
            cur.close()
        except Exception as e:
            raise DBException(e)