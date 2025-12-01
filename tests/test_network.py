import unittest
from modules.network_monitor import NetworkMonitor

class TestNetworkMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = NetworkMonitor()

    def test_capture_connections(self):
        result = self.monitor.capture_connections()
        self.assertIsInstance(result, list)

    def test_analyze_packet(self):
        packet = {"src": "1.1.1.1", "dst": "8.8.8.8", "size": 120}
        result = self.monitor.analyze_packet(packet)
        self.assertIn("risk", result)

if __name__ == "__main__":
    unittest.main()
