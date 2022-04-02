from src.database.database_provider.postgreSQL_database import PostgreSQLDatabaseProvider
import logging

class Database:
    """
        Helper class to perform database operations on high level.
        They provide utility to fetch Face objects and insert face objects as well.

    """

    def __init__(self, databaseCredentials):
        self.databaseProvider = PostgreSQLDatabaseProvider(databaseCredentials)
        self.tableName = databaseCredentials['tableName']
        # creating table in case its not created
        createTableQuery = f"""
            CREATE TABLE IF NOT EXISTS {self.tableName} (
                id SERIAL PRIMARY KEY,
                person TEXT,
                version TEXT,
                date TEXT, 
                location TEXT,
                image BYTEA
            );  
            """
        self.databaseProvider.createTable(createTableQuery)



    # insert face encodings(pickle format) and also their metaData
    def insertFaceWithMetaData(self, face, metadata):
        insertFaceQuery = f"""
            INSERT INTO {self.tableName} (person, version, date, location, image)
            VALUES (%s, %s, %s, %s, %s);
        """
        self.databaseProvider.insert(insertFaceQuery, (metadata['person'], metadata['version'], metadata['date'], metadata['location'], face.getEncoding()))
        logging.debug("Inserted face")

    # utility function to fetch all faces from the database (id, image, person_name)
    def getFacesWithoutMetaData(self):
        getFacesQuery = f"""
            SELECT id, image, person
            FROM {self.tableName}
        """

        result = self.databaseProvider.fetchAll(getFacesQuery, None)
        
        logging.debug("Fetched faces")
        return result
        

    # utility function to fetch meta data of a face from the database
    def getFaceMetaData(self, id):
        getFaceQuery = f"""
            SELECT id, person, version, date, location
            FROM {self.tableName}
            WHERE id = {id};
        """
        result = self.databaseProvider.fetchOne(getFaceQuery)
        return result
        