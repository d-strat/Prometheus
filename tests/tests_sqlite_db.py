import unittest
import sqlite3
import os
from database.sqlite_db import SQLiteDB  # Assuming the class is in sqlite_db.py
import time


class TestSQLiteDB(unittest.TestCase):
    TEST_DB = "test_database.db"

    @classmethod
    def setUpClass(cls):
        cls.db = SQLiteDB(cls.TEST_DB)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        os.remove(cls.TEST_DB)

    def setUp(self):
        """Clear tables before each test."""
        self.db._SQLiteDB__execute_query("DELETE FROM NodeActivity")
        self.db._SQLiteDB__execute_query("DELETE FROM Nodes")

    def test_add_and_get_node_activity(self):
        """Test adding and retrieving node activity."""
        self.db._SQLiteDB__save("Nodes", {"id": 1, "ip_version": "IPv4", "ip_address": "192.168.1.1", "udp_tcp": "TCP",
                                          "port": 8080, "protocol": "HTTP", "public_key": "test_key"})
        self.db.add_node_activity(1)
        result = self.db.get_node_activity(1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 1)  # node_id should be 1

    def test_remove_old_nodes(self):
        """Test removing nodes with outdated activity."""
        self.db._SQLiteDB__save("Nodes", {"id": 2, "ip_version": "IPv4", "ip_address": "192.168.1.2", "udp_tcp": "UDP",
                                          "port": 9090, "protocol": "HTTPS", "public_key": "test_key2"})
        self.db.add_node_activity(2)
        time.sleep(2)  # Wait to create a time difference
        self.db.remove_old_nodes(1)  # Remove nodes with activity older than 1 second
        result = self.db.dump_nodes()
        self.assertEqual(len(result), 0)  # The node should be removed
        self.assertEqual(self.db.get_node_activity(2), [])

    def test_dump_nodes(self):
        """Test retrieving all nodes."""
        self.db._SQLiteDB__save("Nodes",
                                {"id": 3, "ip_version": "IPv4", "ip_address": "10.0.0.1", "udp_tcp": "TCP", "port": 443,
                                 "protocol": "HTTPS", "public_key": "test_key3"})
        nodes = self.db.dump_nodes()
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0][0], 3)  # ID should match


if __name__ == "__main__":
    unittest.main()