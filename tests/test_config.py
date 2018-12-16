import unittest
from Configuration import Configuration


class ConfigurationCompletionTest(unittest.TestCase):
    def test_single_value(self):
        data = {}
        skel = {
            "test": "value"
        }
        data: dict = Configuration._complete_with_skel(data, skel)
        self.assertEqual(data, skel)
        data['test'] = "value2"
        self.assertNotEqual(data, skel)

    def test_dict(self):
        data = {}
        skel = {
            "dict": {
                "test1": "value1",
                "test2": "value2"
            }
        }
        data: dict = Configuration._complete_with_skel(data, skel)
        self.assertEqual(data, skel)
        data['dict']['test1'] = "value2"
        self.assertNotEqual(data, skel)

    def test_list(self):
        data = {
            "list1": []
        }
        skel = {
            "list1": [
                "value1",
                "value2"
            ],
            "list2": []
        }
        data: dict = Configuration._complete_with_skel(data, skel)
        self.assertDictEqual(data, skel)
        data['list1'][1] = "value3"
        self.assertNotEqual(data, skel)
