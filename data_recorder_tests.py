import unittest
import filecmp
import os
import json
import data_recorder

TEST_DB_PATH = "test_cases/test_db_2.json"
TEST_DB_PATH_2 = "test_cases/test_db.json"

class TestDataRecorder(unittest.TestCase):
    def test_create_db(self):
        # clean slate, create a fresh db
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
        data_recorder.DB_PATH = TEST_DB_PATH
        data_recorder.create_db()
        test_db_default_input = {"data_records": []}
        db_default_input = {}
        with open(TEST_DB_PATH) as filehandler:
            db_default_input = json.load(filehandler)
        self.assertEqual(os.path.exists(TEST_DB_PATH), True)
        self.assertEqual(test_db_default_input, db_default_input)
        
    def test_push_to_db(self):
        data_entries = [{"id": "43", "name": "John Smith", "address": "123 Highgate Grove Singapore   323244", "phone": "34323434"},
                        {"id": "23", "name": "Bugs Bunny", "address": "Rabbit Hole London   232323", "phone": "87263162363"}]
        # clean slate, create a fresh db
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
        data_recorder.DB_PATH = TEST_DB_PATH
        data_recorder.push_to_db(data_entries)
        self.assertEqual(filecmp.cmp("test_cases/test_db.json", "test_cases/test_db_2.json"), True)

    def test_pull_from_db(self):
        test_data_entries = [{"id": "43", "name": "John Smith", "address": "123 Highgate Grove Singapore   323244", "phone": "34323434"},
                             {"id": "23", "name": "Bugs Bunny", "address": "Rabbit Hole London   232323", "phone": "87263162363"}]
        data_recorder.DB_PATH = TEST_DB_PATH_2
        existing_data_entries = data_recorder.pull_from_db().get("data_records")
        self.assertEqual(test_data_entries, existing_data_entries)
    
    def test_search_entries(self):
        data_entries = [{"id": "43", "name": "John Smith", "address": "123 Highgate Grove Singapore   323244", "phone": "34323434"},
                        {"id": "23", "name": "Bugs Bunny", "address": "Rabbit Hole London   232323", "phone": "87263162363"}]
        matched_entries = data_recorder.search_entries(data_entries, "jo", "name")
        test_match = [{"id": "43", "name": "John Smith", "address": "123 Highgate Grove Singapore   323244", "phone": "34323434"}]
        self.assertEqual(matched_entries, test_match)

unittest.main(verbosity=2)