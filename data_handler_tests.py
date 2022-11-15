import unittest
import filecmp
import os
from data_handler import DataRecord, FormatHandler

TEST_DB_PATH = "test_cases/test_db.json"
TEST_UPLOAD_PATH = "test_cases/test_upload.json"

class TestDataRecord(unittest.TestCase):
    def test_normal_data_record(self):
        data_record = DataRecord("1", "Anne Rice", "23 Vampire Ave NY 12512", "66666666")
        self.assertEqual(data_record.get_id(), "1")
        self.assertEqual(data_record.get_name(), "Anne Rice")
        self.assertEqual(data_record.get_address(), "23 Vampire Ave NY 12512")
        self.assertEqual(data_record.get_phone(), "66666666")

    def test_special_data_record(self):
        data_record = DataRecord("1hdsg", "Anne-^ Rice", "23 Vampire Ave, NY-12512", "dgj66666666dgjf")
        self.assertEqual(data_record.get_id(), "1")
        self.assertEqual(data_record.get_name(), "Anne Rice")
        self.assertEqual(data_record.get_address(), "23 Vampire Ave  NY 12512")
        self.assertEqual(data_record.get_phone(), "66666666")
    
    def test_special_data_record_2(self):
        data_record = DataRecord("1hdsg^&", "Anne2*", "23 Vampire Ave, NY-12512, 238768", "dgj66666666dgjf")
        self.assertEqual(data_record.get_id(), "1")
        self.assertEqual(data_record.get_name(), "Anne2")
        self.assertEqual(data_record.get_address(), "23 Vampire Ave  NY 12512  238768")
        self.assertEqual(data_record.get_phone(), "66666666")

class TestFormatHandler(unittest.TestCase):
    def test_push_to_db(self):
        data_entries = [{"id": 1, "name": "Anne Rice", "address": "23 Vampire Ave NY 12512", "phone": "66666666"},
                        {"id": 56, "name": "Becky", "address": "Block 25 LA 1728126", "phone": "36553232"},
                        {"id": 43, "name": "Toto Ro", "address": "The Banana Leaf Tokyo 238723", "phone": "34563424"}]
        format_handler = FormatHandler()
        format_handler.set_db_path("test_cases/test_case_1.json")
        format_handler.push_to_db(data_entries)
        self.assertEqual(filecmp.cmp("test_cases/test_case_1_result.json", "test_cases/test_case_1.json"), True)
    
    def test_pull_from_db(self):
        data_entries = [{"id": 1, "name": "Anne Rice", "address": "23 Vampire Ave NY 12512", "phone": "66666666"},
                        {"id": 56, "name": "Becky", "address": "Block 25 LA 1728126", "phone": "36553232"},
                        {"id": 43, "name": "Toto Ro", "address": "The Banana Leaf Tokyo 238723", "phone": "34563424"}]
        format_handler = FormatHandler()
        format_handler.set_db_path("test_cases/test_case_1.json")
        existing_data = format_handler.pull_from_db().get("data_records")
        self.assertEqual(data_entries, existing_data)
    
    def test_remove_duplicates(self):
        existing_data = {"data_records":[
                        {"id": 1, "name": "Anne Rice", "address": "23 Vampire Ave NY 12512", "phone": "66666666"},
                        {"id": 56, "name": "Becky", "address": "Block 25 LA 1728126", "phone": "36553232"},
                        {"id": 43, "name": "Toto Ro", "address": "The Banana Leaf Tokyo 238723", "phone": "34563424"}
                        ]}
        data_entries = [{"id": 33, "name": "Mary Kate", "address": "22 Twins Ave NY 222222", "phone": "2222222229"},
                        {"id": 56, "name": "Becky Sue", "address": "Block 25 LA 1728126", "phone": "265325232"},
                        {"id": 4, "name": "Toto Ro", "address": "The Banana Leaf Tokyo 238723", "phone": "34563424"}]
        unique_entries = [{"id": 33, "name": "Mary Kate", "address": "22 Twins Ave NY 222222", "phone": "2222222229"},
                          {"id": 4, "name": "Toto Ro", "address": "The Banana Leaf Tokyo 238723", "phone": "34563424"}]
        format_handler = FormatHandler()
        test_result_entries = format_handler.remove_duplicates(existing_data, data_entries)
        self.assertEqual(unique_entries, test_result_entries)
    
    def test_json_upload(self):
        test_file_path = "test_cases/test_data.json"
        test_name, test_ext = os.path.splitext(test_file_path)
        test_ext = test_ext.split(".")[-1] # remove '.' from extension

        # clear any old db data to test
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

        format_handler = FormatHandler(test_ext, test_file_path)
        format_handler.set_db_path(TEST_DB_PATH)
        format_handler.upload_json_data()
        self.assertEqual(filecmp.cmp(TEST_DB_PATH, TEST_UPLOAD_PATH), True)
    
    def test_csv_upload(self):
        test_file_path = "test_cases/test_data.csv"
        test_name, test_ext = os.path.splitext(test_file_path)
        test_ext = test_ext.split(".")[-1] # remove '.' from extension

        # clear any old db data to test
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

        format_handler = FormatHandler(test_ext, test_file_path)
        format_handler.set_db_path(TEST_DB_PATH)
        format_handler.upload_csv_data()
        self.assertEqual(filecmp.cmp(TEST_DB_PATH, TEST_UPLOAD_PATH), True)
    
    def test_yaml_upload(self):
        test_file_path = "test_cases/test_data.yaml"
        test_name, test_ext = os.path.splitext(test_file_path)
        test_ext = test_ext.split(".")[-1] # remove '.' from extension

        # clear any old db data to test
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

        format_handler = FormatHandler(test_ext, test_file_path)
        format_handler.set_db_path(TEST_DB_PATH)
        format_handler.upload_yaml_data()
        self.assertEqual(filecmp.cmp(TEST_DB_PATH, TEST_UPLOAD_PATH), True)
    
    def test_xml_upload(self):
        test_file_path = "test_cases/test_data.xml"
        test_name, test_ext = os.path.splitext(test_file_path)
        test_ext = test_ext.split(".")[-1] # remove '.' from extension

        # clear any old db data to test
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

        format_handler = FormatHandler(test_ext, test_file_path)
        format_handler.set_db_path(TEST_DB_PATH)
        format_handler.upload_xml_data()
        self.assertEqual(filecmp.cmp(TEST_DB_PATH, TEST_UPLOAD_PATH), True)
    
    def test_json_download(self):
        format_handler = FormatHandler("json", "test_cases/test_download.json")
        format_handler.set_db_path(TEST_DB_PATH)
        format_handler.download_json_data()
        self.assertEqual(filecmp.cmp(TEST_DB_PATH, "test_cases/test_download_result.json"), True)
    
    def test_csv_download(self):
        format_handler = FormatHandler("csv", "test_cases/test_download.csv")
        format_handler.set_db_path(TEST_DB_PATH)
        format_handler.download_json_data()
        self.assertEqual(filecmp.cmp(TEST_DB_PATH, "test_cases/test_download.json"), True)
    
    def test_xml_download(self):
        format_handler = FormatHandler("csv", "test_cases/test_download.xml")
        format_handler.set_db_path(TEST_DB_PATH)
        format_handler.download_json_data()
        self.assertEqual(filecmp.cmp(TEST_DB_PATH, "test_cases/test_download.json"), True)

    def test_yaml_download(self):
        format_handler = FormatHandler("csv", "test_cases/test_download.xml")
        format_handler.set_db_path(TEST_DB_PATH)
        format_handler.download_json_data()
        self.assertEqual(filecmp.cmp(TEST_DB_PATH, "test_cases/test_download.json"), True)



unittest.main(verbosity=2)