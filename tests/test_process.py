import unittest
from modules.process_monitor import ProcessMonitor

class TestProcessMonitor(unittest.TestCase):
    def setUp(self):
        self.pm = ProcessMonitor()

    def test_list_processes(self):
        result = self.pm.list_processes()
        self.assertIsInstance(result, list)

    def test_detect_suspicious(self):
        dummy = [{"name": "testapp", "pid": 123}]
        result = self.pm.detect_suspicious(dummy)
        self.assertIsInstance(result, list)

if __name__ == "__main__":
    unittest.main()
