# tests/test_monitor.py

import unittest
from src.monitor.monitor import Monitor

class TestMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = Monitor(keywords=["urgent", "help"])

    def test_monitor_message(self):
        self.monitor.monitor_message("This is an urgent request")
        self.monitor.monitor_message("Just a normal message")
