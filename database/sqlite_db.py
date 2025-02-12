"""
Programmers notes:

Python has None, SQLite has NULL, conversion is automatic in both ways.
"""
import sqlite3
from typing import List, Any, Optional
import threading
import logging


class SQLiteDB:
    _instance = None
    _lock = threading.RLock()
    name = "Prometheus - SQLiteDB"

    def __new__(cls, db_path: str):
        """
        Singleton constructor
        :param db_path: path to database file, if the file does not exist, it will be created.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SQLiteDB, cls).__new__(cls)
                cls._instance._init_db(db_path)
        return cls._instance

    def _init_db(self, db_path: str) -> None:
        """
        Initializes the SQLiteDB instance, sets up logging, and connects to the database.
        """
        self.db_path = db_path
        with open(self.db_path, "a") as f:
            f.close()
        sqlite3.connect(self.db_path).close()
        self.connection: Optional[sqlite3.Connection] = None
        self.__connect()
        self.__create_tables()

    def __connect(self) -> None:
        """
        Establishes a connection to the SQLite database.
        """
        logging.info(f"Connecting to SQLite database at {self.db_path}")
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)

        if self.connection is None:
            logging.error("Failed to connect to the SQLite database!")
            raise ConnectionError("SQLite connection failed")

    def dump_nodes(self) -> List[Any]:
        """
        Retrieves all data from the Nodes table.
        """
        return self.query("SELECT * FROM Nodes")

    def query(self, query: str, params: Optional[List[Any]] = None) -> List[Any]:
        """
        Queries the database and returns results.
        """
        return self.__execute_query(query, params)

    def __execute_query(
        self, query: str, params: Optional[List[Any]] = None
    ) -> List[Any]:
        """
        Executes a given SQL query and returns the results.

        :param query: The SQL query to execute.
        :param params: Optional list of parameters for parameterized queries.
        :return: List of results returned from the executed query.
        """
        with SQLiteDB._lock:
            logging.info(f"Executing query: {query}")
            cursor = self.connection.cursor()

            # Split the query string by semicolons to handle multiple queries
            # queries = [q.strip() + ";" for q in query.split(";") if q.strip()]
            # results = []

            cursor = self.connection.cursor()
            # start_idx = 0
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                self.connection.commit()
                return cursor.fetchall()
            except Exception as e:
                logging.error(f"Error executing query: {e}")
                raise
            finally:
                cursor.close()  # Ensure the cursor is always closed

    def __save(self, table: str, data: dict) -> None:
        """
        Inserts or replaces data into a given table.

        :param table: The table in which to save the data.
        :param data: A dictionary where the keys are column names, and values are the values to be saved.
        :return: None
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        query = f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})"
        logging.info(f"Saving data: {data} into table: {table}")
        self.__execute_query(query, list(data.values()))

    def __delete(
        self, table: str, condition: str, params: Optional[List[Any]] = None
    ) -> None:
        """
        Deletes rows from a table that match the condition.

        :param table: The table from which to delete the data.
        :param condition: A SQL condition for deleting rows (e.g., "id = ?").
        :param params: Optional list of parameters for parameterized queries.
        :return: None
        """
        query = f"DELETE FROM {table} WHERE {condition}"
        logging.info(f"Deleting from table: {table} where {condition}")
        self.__execute_query(query, params)

    def close(self) -> None:
        """
        Closes the SQLite database connection.
        """
        if self.connection:
            logging.info("Closing database connection")
            self.connection.close()

    def __create_tables(self) -> None:
        """
        Creates the necessary tables in the SQLite database.
        """
        table_creation_queries = [
            """
            CREATE TABLE Nodes (
                id SERIAL PRIMARY KEY,
                ip_version ENUM('IPv4', 'IPv6') NOT NULL,
                ip_address VARCHAR(45) NOT NULL,
                udp_tcp ENUM('UDP', 'TCP') NOT NULL,
                port INT CHECK (port BETWEEN 1 AND 65535) NOT NULL,
                protocol VARCHAR(20) NOT NULL
                public_key VARCHAR(128) NOT NULL,
            );

            """,
            """
            CREATE TABLE NodeActivity (
                activity_id SERIAL PRIMARY KEY,
                node_id INT NOT NULL,
                activity_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (node_id) REFERENCES Nodes(id) ON DELETE CASCADE
            );
            """,
        ]

        # CREATE TABLE Nodes (
        #     id SERIAL PRIMARY KEY,
        #     ip_version ENUM('IPv4', 'IPv6') NOT NULL,
        #     ip_address VARCHAR(45) NOT NULL,
        #     udp_tcp ENUM('UDP', 'TCP') NOT NULL,
        #     port INT CHECK (port BETWEEN 1 AND 65535) NOT NULL,
        #     protocol VARCHAR(20) NOT NULL
        #     public_key VARCHAR(100) NOT NULL,
        #     activity_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        # );


        for query in table_creation_queries:
            logging.info(f"Creating tables with query: {query}")
            self.__execute_query(query)
