import unittest
from modules.behavior_engine import BehaviorEngine

class TestBehaviorEngine(unittest.TestCase):
    def setUp(self):
        self.be = BehaviorEngine()

    def test_load_baseline(self):
        result = self.be.load_baseline()
        self.assertIsInstance(result, dict)

    def test_analyze_event(self):
        event = {"type": "network", "value": "8.8.8.8"}
        result = self.be.analyze_event(event)
        self.assertIn("score", result)

if __name__ == "__main__":
    unittest.main()
