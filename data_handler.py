# [2022] This is a library for Data Recorder.
# Developer: Su Sengupta
# Test: data_recorder_test.py

import json
import csv
import yaml
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

import os
import argparse
import re
from collections import OrderedDict

class DataRecord:
    """
    Class for storing an entry in Data Recorder.
    Used to initialize, validate and return data records.

    Attributes
    ----------
        n_id (str): ID of the employee
        name (str): Name of the employee
        address (str): Address of the employee
        phone (str): Phone number of the employee
    """

    def __init__(self, n_id, name, address, phone):
        self._id = n_id
        self._name = name
        self._address = address
        self._phone = phone
        self.validate_entry()

    def set_name(self, name):
        self._name = name

    def set_address(self, address):
        self._address = address

    def set_phone(self, phone):
        self._phone = phone
    
    def set_id(self, n_id):
        self._id = n_id
    
    def get_name(self):
        return self._name
    
    def get_address(self):
        return self._address
    
    def get_phone(self):
        return self._phone
    
    def get_id(self):
        return self._id
    
    def to_dict(self):
        return self.format_dict(self.__dict__)
    
    def format_dict(self, data_record):
        formatted_data_record = {}
        for key, value in data_record.items():
            key = key.replace("_", "").strip().lower()
            value = value.strip()
            formatted_data_record[key] = value
        return formatted_data_record
    
    def validate_entry(self):
        #  check for spam characters
        self._id = re.sub("\D", "", str(self._id))
        self._phone = re.sub("\D", "", str(self._phone))
        self._name = re.sub('[^a-zA-Z0-9 \n\.]', ' ', self._name)
        self._name = ' '.join(self._name.split())
        self._address = re.sub('[^a-zA-Z0-9 \n\.]', ' ', self._address)


class FormatHandler:
    """
    Class to handle different serialization formats.
    Used to upload and download data.

    Attributes
    ----------
        file_format (str): extension of the file uploaded/downloaded.
        file_path (str): file path of the file uploaded/downloaded.
        db_path (str): Address of the employee
        phone (str): Phone number of the employee
    """
    def __init__(self, file_format=None, file_path=None, db_path=None, supported_records=None):
        self._file_format = file_format
        self._file_path = file_path
        self._db_path = db_path
        self._supported_records = supported_records
    
    def upload(self):
        '''
        Uploads serialized data to db.
        '''
        func_name = "self.upload_%s_data()" % (self._file_format)
        exec(func_name)
    
    def push_to_db(self, data_entries):
        '''
        Pushes new data entries into db.
        By default, this uploads directly to a JSON file
        that is currently acting as a storage unit for
        the data records.

        Parameters
        ----------
            data_entries(dict): dictionary of new data
        '''
        existing_data = {"data_records": []}
        if not os.path.exists(self._db_path):
            with open(self._db_path, 'w') as filehandler:
                json.dump(existing_data, filehandler, indent=4)
        else:
            try:
                with open(self._db_path) as filehandler:
                    existing_data = json.load(filehandler) or {"data_records": []}
                    data_entries = self.remove_duplicates(existing_data, data_entries)
            except json.decoder.JSONDecodeError:
                print ("DB might be corrupted, please check with support team.")

        if existing_data.get("data_records") or data_entries:
            existing_data.get("data_records").extend(data_entries)
            with open(self._db_path, 'w') as filehandler:
                json.dump(existing_data, filehandler, indent=4)
        else:
            print ("No data available for upload.")
    
    def remove_duplicates(self, existing_data, data_entries):
        '''
        Checks for duplicate IDs in db and removes those
        entries that conflict.

        Parameters
        ----------
            existing_data(dict): data currently stored in db
            data_entries(dict): new data being added into db
        '''
        data_records = existing_data.get("data_records")
        data_record_ids = []
        # get all IDs, future idea - cache these somewhere?
        for record in data_records:
            data_record_ids.append(record.get("id"))
        new_data_entries = []
        for entry in data_entries:
            if entry.get("id") not in data_record_ids:
                new_data_entries.append(entry)
            else:
                print ("Duplicate ID: [%s]. This entry will be skipped." % entry.get("id"))
        return new_data_entries

    def upload_json_data(self):
        '''
        Uploads data from .json file to db.
        '''
        upload_entries = []
        with open(self._file_path) as filehandler:
            upload_data = json.load(filehandler)
            try:
                upload_entries = upload_data.get("data_records")
            except:
                print ("Please follow the right format for data upload. Refer to: example.%s" % self._file_format)
        data_entries = []
        for entry in upload_entries:
            data_entry = self.get_data_record(entry.get("id"), entry.get("name"),
                entry.get("address"), entry.get("phone")).to_dict()
            data_entries.append(data_entry)
        self.push_to_db(data_entries)

    def upload_csv_data(self):
        '''
        Uploads data from .csv file to db.
        '''
        rows = []
        upload_entries = []
        with open(self._file_path, 'r') as filehandler:
            csvreader = csv.reader(filehandler)
            header = next(csvreader)
            for row in csvreader:
                rows.append(row)
        if not self.validate_header(header):
            print ("Please follow the right format for data upload. Refer to: example.%s" % self._file_format)
            return
        else:
            for entry in rows:
                try:
                    data_entry = self.get_data_record(entry[0], entry[1], entry[2], entry[3]).to_dict()
                except IndexError:
                    print ("CSV entry %s is missing a field. Skipping it." % entry)
                    continue
                upload_entries.append(data_entry)
            self.push_to_db(upload_entries)

    def validate_header(self, header):
        '''
        Removes any special characters and formatting
        from csv headers.
        '''
        formatted_headers = [h.lower().replace('"', '').strip() for h in header]
        if formatted_headers != self._supported_records:
            return False
        return True

    def upload_yaml_data(self):
        '''
        Uploads data from .yaml file to db.
        '''
        upload_entries = []
        with open (self._file_path, 'r') as filehandler:
            try:
                data = yaml.safe_load(filehandler)
            except yaml.YAMLError as e:
                print (e)
        if not data.get("data_records"):
            print ("Please follow the right format for data upload. Refer to: example.%s" % self._file_format)
        else:
            data_records = data.get("data_records")
            ordered_data_records = OrderedDict([(key, data_records[key]) for key in data_records])
            for n_id, entry in ordered_data_records.items():
                entry_dict = self.get_data_record(n_id, entry.get('name'),
                    entry.get('address'), entry.get('phone')).to_dict()
                upload_entries.append(entry_dict)
            self.push_to_db(upload_entries)

    def upload_xml_data(self):
        '''
        Uploads data from .xml file to db.
        '''
        upload_entries = []
        with open(self._file_path, 'r') as filehandler:
            data = filehandler.read()
        bs_data = BeautifulSoup(data, "xml")
        data_records = bs_data.find_all("data_records")
        if not data_records:
            print ("Please follow the right format for data upload. Refer to: example.%s" % self._file_format)
        else:
            data_records = bs_data.find_all("employee")
            for entry in data_records:
                entry_dict = self.get_data_record(entry.get('id'), entry.get('name'),
                    entry.get('address'), entry.get('phone')).to_dict()
                upload_entries.append(entry_dict)
            self.push_to_db(upload_entries)
    
    def get_data_record(self, n_id, name, address, phone):
        '''
        Creates a DataRecord object that validates the entry.

        Parameters
        ----------
             n_id (str): ID of the employee
            name (str): Name of the employee
            address (str): Address of the employee
            phone (str): Phone number of the employee
        '''
        return DataRecord(n_id, name, address, phone)
    
    def download(self):
        '''
        Downloads serialized data from db to a specified file path.
        '''
        func_name = "self.download_%s_data()" % (self._file_format)
        exec(func_name)
        print ("Downloaded data to: %s" % self._file_path)
    
    def pull_from_db(self):
        '''
        Pulls data records from db.
        By default, this downloads directly from a JSON file
        that is currently acting as a storage unit for
        the data records.
        '''
        try:
            with open(self._db_path) as filehandler:
                existing_data = json.load(filehandler)
        except json.decoder.JSONDecodeError:
            print ("DB might be corrupted, please check with support team.")
        return existing_data
    
    def download_json_data(self):
        '''
        Downloads data from db to .json file.
        '''
        data_records = self.pull_from_db()
        with open(self._file_path, 'w', encoding='utf-8') as f:
            json.dump(data_records, f, ensure_ascii=False, indent=4)
    
    def download_csv_data(self):
        '''
        Downloads data from db to .csv file.
        '''
        header = self._supported_records
        data_records = self.pull_from_db().get("data_records")
        csv_data_records = []
        for record in data_records:
            csv_data_records.append(list(record.values()))
        with open(self._file_path, 'w', encoding='UTF8', newline='') as filehandler:
            writer = csv.writer(filehandler)
            writer.writerow(header)
            writer.writerows(csv_data_records)
    
    def download_yaml_data(self):
        '''
        Downloads data from db to .yaml file.
        '''
        data_records = self.pull_from_db().get("data_records")
        yaml_data_records = []
        for record in data_records:
            yaml_entry = {}
            for field in self._supported_records[1:]:
                yaml_entry[field]  = record.get(field)
            yaml_data_records.append({record.get("id"): yaml_entry})
        yaml_final_data = [{"data_records": yaml_data_records}]
        with open(self._file_path, 'w') as filehandler:
            yaml.dump(yaml_final_data, filehandler)
    
    def download_xml_data(self):
        '''
        Downloads data from db to .xml file.
        '''
        data_records = self.pull_from_db().get("data_records")
        data = ET.Element('data_records')
        for record in data_records:
            item = ET.SubElement(data, 'employee', attrib=record)
        xml_data = ET.tostring(data)
        filehandler = open(self._file_path, "wb")
        filehandler.write(xml_data)