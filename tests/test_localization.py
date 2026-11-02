import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from check_localization import unique_object, validate


class LocalizationTests(unittest.TestCase):
    source = 'pub const REQUIRED_KEYS: [&str; 1] = ["demo.test"];'
    inventory = {'demo_keys': ['demo.test']}

    def test_portuguese_accents_and_newline_are_accepted(self):
        self.assertEqual(validate({'demo.test': 'Ação\nunião!'}, self.inventory, self.source), [])

    def test_missing_key_is_reported(self):
        self.assertTrue(validate({}, self.inventory, self.source))

    def test_extra_key_is_reported(self):
        self.assertTrue(validate({'demo.test': 'Olá', 'other': 'extra'}, self.inventory, self.source))

    def test_empty_and_unsupported_text_are_reported(self):
        for value in ['', '   ', '🐉', '\t', None]:
            with self.subTest(value=value):
                self.assertTrue(validate({'demo.test': value}, self.inventory, self.source))

    def test_rust_key_drift_is_reported(self):
        self.assertTrue(validate({'demo.test': 'Olá'}, self.inventory,
                                 self.source.replace('demo.test', 'demo.other')))

    def test_duplicate_json_key_is_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"key":"first","key":"second"}', object_pairs_hook=unique_object)

    def test_duplicate_inventory_is_reported(self):
        self.assertTrue(validate({'demo.test': 'Olá'},
                                 {'demo_keys': ['demo.test', 'demo.test']}, self.source))
