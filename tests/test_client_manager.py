# tests/test_client_manager.py

import unittest
from src.client_manager.client_manager import ClientManager

class TestClientManager(unittest.TestCase):
    def setUp(self):
        self.manager = ClientManager()

    def test_add_client(self):
        self.manager.add_client("client1")
        self.assertEqual(len(self.manager.clients), 1)

    def test_remove_client(self):
        self.manager.add_client("client1")
        self.manager.remove_client("client1")
        self.assertEqual(len(self.manager.clients), 0)
