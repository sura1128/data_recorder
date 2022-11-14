# [2022] This is a library for Data Recorder.
# Developer: Su Sengupta
# Test: data_recorder_test.py

import json
import csv
import yaml
import lxml
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

import os
import argparse
import re
from collections import OrderedDict

class DataRecord:
    # Class for storing an entry in Data Recorder
    #
    # name (str): Name of the employee
    # address (str): Address of the employee
    # phone (str): Phone number of the employee
    # n_id (str): ID of the employee

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
    
    def set_id(self, id):
        self._id = id
    
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
        self._id = str(self._id)
        self._phone = re.sub("\D", "", str(self._phone))
        self._address = re.sub('[^a-zA-Z0-9 \n\.]', '', self._address)


class FormatHandler:
    # class to read and write file data of different formats
    def __init__(self, file_format, file_path):
        self._file_format = file_format
        self._file_path = file_path
        self._db_path = "./main.json"
        self._supported_records = ["id", "name", "address", "phone"]
    
    def upload(self):
        func_name = "self.upload_%s_data()" % (self._file_format)
        exec(func_name)
    
    def push_to_db(self, data_entries):
        existing_data = []
        with open(self._db_path) as filehandler:
            existing_data = json.load(filehandler)
            # data_entries = self.remove_duplicates(existing_data, data_entries)
            existing_data.get("data_records").extend(data_entries)
        with open(self._db_path, 'w') as filehandler:
            json.dump(existing_data, filehandler, indent=4)
    
    def remove_duplicates(self, existing_data, data_entries):
        # kinda brute force right now, is there a way to  optimize this?
        data_records = existing_data.get("data_records")

    def upload_json_data(self):
        with open(self._file_path) as filehandler:
            upload_data = json.load(filehandler)
            try:
                upload_entries = upload_data.get("data_records")
            except:
                print ("Please follow the right format for data upload. Refer to: example.%s" % self._file_format)
            # Some way to validate the entries? check for duplicates?
            self.push_to_db(upload_entries)

    def upload_csv_data(self):
        rows = []
        upload_entries = []
        with open(self._file_path, 'r') as filehandler:
            csvreader = csv.reader(filehandler)
            header = next(csvreader)
            for row in csvreader:
                rows.append(row)
        if not self.validate_header(header):
            print ("Please follow the right format for data upload. Refer to: example.%s" % self._file_format)
        else:
            for entry in rows:
                data_entry = {}
                for index in range(0, len(self._supported_records)):
                    data_entry[self._supported_records[index]] = entry[index].replace('"', '').strip()
                upload_entries.append(data_entry)
            self.push_to_db(upload_entries)


    def validate_header(self, header):
        formatted_headers = [h.lower().replace('"', '').strip() for h in header]
        if formatted_headers != self._supported_records:
            return False
        return True

    def upload_yaml_data(self):
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
        return DataRecord(n_id, name, address, phone)
    
    def download(self):
        func_name = "self.download_%s_data()" % (self._file_format)
        exec(func_name)
        print ("Downloaded data to: %s" % self._file_path)
    
    def pull_from_db(self):
        # error handling needed here
        with open(self._db_path) as filehandler:
            existing_data = json.load(filehandler)
        return existing_data
    
    def download_json_data(self):
        # error handling needed
        data_records = self.pull_from_db()
        # print ("TEST %s" % self._file_path)
        # print (data_records)
        with open(self._file_path, 'w', encoding='utf-8') as f:
            json.dump(data_records, f, ensure_ascii=False, indent=4)
    
    def download_csv_data(self):
        header = self._supported_records
        data_records = self.pull_from_db().get("data_records")
        csv_data_records = []
        for record in data_records:
            csv_data_records.append(list(record.values()))
        # exception handling
        with open(self._file_path, 'w', encoding='UTF8', newline='') as filehandler:
            writer = csv.writer(filehandler)
            writer.writerow(header)
            writer.writerows(csv_data_records)
    
    def download_yaml_data(self):
        data_records = self.pull_from_db().get("data_records")
        yaml_data_records = []
        for record in data_records:
            yaml_entry = {}
            for field in self._supported_records[1:]:
                yaml_entry[field]  = record.get(field)
            yaml_data_records.append({record.get("id"): yaml_entry})
        # print (yaml_data_records)
        yaml_final_data = [{"data_records": yaml_data_records}]
        # remove the dash somehow?
        with open(self._file_path, 'w') as filehandler:
            documents = yaml.dump(yaml_final_data, filehandler)
    
    def download_xml_data(self):
        data_records = self.pull_from_db().get("data_records")
        # create the file structure
        data = ET.Element('data_records')
        for record in data_records:
            item = ET.SubElement(data, 'employee', attrib=record)
        xml_data = ET.tostring(data)
        # exception handling
        filehandler = open(self._file_path, "wb")
        filehandler.write(xml_data)