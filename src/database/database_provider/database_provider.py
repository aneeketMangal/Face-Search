from abc import ABC, abstractclassmethod
class DatabaseProvider(ABC):
    """
        Abstract class for database.
        It provides three operations as of now
        1. insert
        2. fetchAll -> fetch all matching records
        3. fetchOne -> fetch a single record
        4. createTable
    """
    @abstractclassmethod
    def __init__(self, databaseCredentials):
        pass

    @abstractclassmethod
    def insert(self, query, params = None):
        pass

    @abstractclassmethod
    def fetchAll(self, query, params=None):
        pass

    @abstractclassmethod
    def fetchOne(self, query, params=None):
        pass

    @abstractclassmethod
    def createTable(self, query, params=None):
        pass

