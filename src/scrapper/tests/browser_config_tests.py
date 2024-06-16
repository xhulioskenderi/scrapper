import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
import os
import json
from selenium import webdriver
from browser_setup_code import RotateUserAgents, ProfileGenerator, ProfilePool, Mozilla, Chrome  # adjust 'your_module' to the name of your actual module
from ua_parse import parse_ua

class TestRotateUserAgents(unittest.TestCase):
    def setUp(self):
        self.rotate_user_agents = RotateUserAgents()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.parent_dir = os.path.dirname(self.script_dir)
        self.target_dir = os.path.join(self.parent_dir, 'text_files')

    def test_get_useragents(self):
        self.rotate_user_agents.get_useragents()

        self.assertTrue(os.path.exists(os.path.join(self.target_dir, 'chrome_ua.json')))
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, 'firefox_ua.json')))

        with open(os.path.join(self.target_dir, 'chrome_ua.json'), 'r') as f:
            data = json.load(f)
            for key, value in data.items():
                ua = parse_ua(key)
                self.assertEqual(ua['browser']['name'], 'Chrome')
                self.assertIsInstance(value, float)

        with open(os.path.join(self.target_dir, 'firefox_ua.json'), 'r') as f:
            data = json.load(f)
            for key, value in data.items():
                ua = parse_ua(key)
                self.assertEqual(ua['browser']['name'], 'Firefox')
                self.assertIsInstance(value, float)

    def test_choose_chrome(self):
        self.rotate_user_agents.get_useragents()
        chosen_key = self.rotate_user_agents.choose_chrome()

        with open(os.path.join(self.target_dir, 'chrome_ua.json'), 'r') as f:
            data = json.load(f)
            self.assertTrue(chosen_key in data.keys())

    def test_choose_mozilla(self):
        self.rotate_user_agents.get_useragents()
        chosen_key = self.rotate_user_agents.choose_mozilla()

        with open(os.path.join(self.target_dir, 'firefox_ua.json'), 'r') as f:
            data = json.load(f)
            self.assertTrue(chosen_key in data.keys())

if __name__ == '__main__':
    unittest.main()
