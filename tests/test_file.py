import unittest
from modules.file_monitor import FileMonitor

class TestFileMonitor(unittest.TestCase):
    def setUp(self):
        self.fm = FileMonitor(paths=["/tmp/"])

    def test_scan_paths(self):
        result = self.fm.scan_paths()
        self.assertIsInstance(result, dict)

    def test_detect_changes(self):
        before = {"file1.txt": "hash1"}
        after = {"file1.txt": "hash2"}
        result = self.fm.detect_changes(before, after)
        self.assertIn("modified", result)

if __name__ == "__main__":
    unittest.main()
