# [2022] This is a library for Data Recorder.
# Developer: Su Sengupta
# Test: data_recorder_test.py

#!/usr/bin/env python

import json
import csv
import yaml
import lxml
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

import os
import argparse
from collections import OrderedDict

import sqlite3

DB_PATH = "./main.json"
DB_CAPACITY = 100
DEFAULT_FORMAT = "json"
SUPPORTED_FORMATS = ["json", "csv", "yaml", "xml"]

FUNCTIONS = ["add", "upload", "download", "search", "display"]
SUPPORTED_RECORDS = ["id", "name", "address", "phone"]

SUPPORT_EMAIL_ALIAS = "data-recorder-help@gmail.com"

# TMP_PATH = "./tmp.json"

class DataRecord:
    # Class for storing an entry in Data Recorder
    #
    # Attributes:
    # name (str): Name of the employee
    # address (str): Address of the employee
    # phone (str): Phone number of the employee

    def __init__(self, name, address, phone, n_id):
        self._name = name
        self._address = address
        self._phone = phone
        self._id = n_id
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
        self._phone = str(self._phone)
        self._address = str(self._address).replace(",", " ")


### ADDING DATA MANUALLY ###

def add_data():
    # Should there be an upper limit for how many entries can be added in total? I am going to assume our DB can't take more than 100 entries as an example.
    DB_SIZE = get_DB_size()
    total_entries = input("Currently, we have [%s] slots left in our DB. Please type the number of entries you'd like to add today.\n" % (DB_CAPACITY - DB_SIZE))
    
    if total_entries.isnumeric():
        if DB_SIZE + int(total_entries) > 100:
            print ("Sorry, that exceeds our upper limit of %s entries. Please try again." % (DB_CAPACITY))
        else:
            print ("Adding a new batch of [%s] entries:" % total_entries)
            add_data_entries(int(total_entries))
    else:
        print ("Please enter a valid option for number of entries.")
    return

def get_DB_size():
    try:
        db_data = open(DB_PATH)
    except:
        print ("unable to read DB")
    data_records = json.load(db_data)
    db_size = len(data_records.get("data_records"))
    return db_size

def add_data_entries(total_entries):
    num_entry = 1
    data_entries = []

    while (num_entry <= total_entries):
        # Validating data entries? In case of special characters or spam
        name = input("Enter the name: ")
        address = input("Enter the address: ")
        phone = input("Enter phone number: ")
        n_id = input("Enter the id: ")

        data_record = DataRecord(name, address, phone, n_id)
        data_record_dict = data_record.to_dict()
        data_entries.append(data_record_dict)
        num_entry += 1

        # a backup will be done every 5 entries
        # Store into a tmp file

    push_to_db(data_entries)
    # push_to_database(data_entries)


def push_to_db(data_entries):
    with open(DB_PATH) as filehandler:
        existing_data = json.load(filehandler)
        existing_data.get("data_records").extend(data_entries)
    with open(DB_PATH, 'w') as filehandler:
        json.dump(existing_data, filehandler, indent=4)

def pull_from_db():
    # error handling needed here
    with open(DB_PATH) as filehandler:
        existing_data = json.load(filehandler)
    data_records = existing_data.get("data_records")
    return data_records

def connect_to_db():
    # add an exception to catch DB errors
    conn = sqlite3.connect('test_database') 
    cursor = conn.cursor()
    return cursor

# def push_to_database(data_entries):
#     cursor = connect_to_db()
#     for entry in data_entries:
#         db_entry = []
#         for field in SUPPORTED_RECORDS:
#             db_entry.append(entry.get(field))
#         print (tuple(db_entry))
#         c.execute('''
#           INSERT INTO employee_records (n_id, name, address, phone)

#                 VALUES
#                 ?
#           ''')

        

### END OF ADDING DATA MANUALLY ###

### SEARCHING DATA MANUALLY ###

def search_data():
    data_records = pull_from_db()

    # More features: starting with, ends with, contains
    search_field = input("Which of the following fields would you like to use for searching: %s\n" % SUPPORTED_RECORDS)
    if search_field.lower() not in SUPPORTED_RECORDS:
        print ("The field [%s] does not exist in our records. Please contact [%s] if you'd like to add a new field or try again." % (search_field, SUPPORT_EMAIL_ALIAS))
        return
    search_value = input("What %s would you like to search for: " % search_field)

    found_entries = []
    print ("Searching for %s amongst %s in entries..." % (search_value, search_field))
    for record in data_records:
        if search_value.lower() in record.get(search_field).lower():
            found_entries.append(record)
    
    # simple shell output - possibility of displaying in table form?
    print ("Here are the matching entries with [%s] in [%s]:" % (search_value, search_field))
    print (found_entries)

    # display in HTML?

### END OF SEARCHING DATA MANUALLY ###

### DISPLAY DATA MANUALLY ###
def display_data():
    existing_data = pull_from_db()
    
    # simple shell output - possibility of displaying in table form?
    print (existing_data)

    # display in HTML?

### END OF DISPLAY DATA MANUALLY ###


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
        with open(self._db_path) as filehandler:
            existing_data = json.load(filehandler)
            existing_data.get("data_records").extend(data_entries)
        with open(self._db_path, 'w') as filehandler:
            json.dump(existing_data, filehandler, indent=4)
    
    def upload_json_data(self):
        with open(self._file_path) as filehandler:
            upload_data = json.load(filehandler)
            try:
                upload_entries = upload_data.get("data_records")
            except:
                # Create example file formats to follow
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
                    # Some way to validate the entries? check for duplicates?
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
                entry_dict = self.get_data_record(entry.get('name'), entry.get('address'),
                    entry.get('phone'), n_id).to_dict()
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
                entry_dict = self.get_data_record(entry.get('name'), entry.get('address'),
                    entry.get('phone'), entry.get('id')).to_dict()
                upload_entries.append(entry_dict)
            self.push_to_db(upload_entries)
    
    def get_data_record(self, name, address, phone, n_id):
        return DataRecord(name, address, phone, n_id)
    
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
        


### UPLOADING DATA ###
def upload_data():
    src = input("Please provide the path to the source file for uploading data: ")
    src_name, src_ext = os.path.splitext(src)
    src_ext = src_ext.split(".")[-1] # remove '.' from extension

    # Check if file exists on disk
    if not os.path.exists(src):
        print ("The filepath [%s] does not exist, please try again." % src)
        return

    if src_ext not in SUPPORTED_FORMATS:
        print ("This file format is not supported currently. Please contact [%s] to request for a new format." % SUPPORT_EMAIL_ALIAS)
    else:
        print ("Uploading data from: %s..." % src)
        formathandler = FormatHandler(src_ext, src)
        formathandler.upload()

### END OF UPLOADING DATA ###

### DOWNLOADING DATA ###
def download_data():
    print ("Downloading data...")

    dest = input("Please provide the path to the destination file for downloading data: ")
    dest_name, dest_ext = os.path.splitext(dest)
    dest_ext = dest_ext.split(".")[-1] # remove '.' from extension

    if dest_ext not in SUPPORTED_FORMATS:
        print ("This file format is not supported currently. Please contact [%s] to request for a new format." % SUPPORT_EMAIL_ALIAS)
    else:
        print ("Downloading data to: %s..." % dest)
        formathandler = FormatHandler(dest_ext, dest)
        formathandler.download()


### END OF DOWNLOADING DATA ###


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="commands", dest="command")
    
    add_parser = subparsers.add_parser("add", help="manually add entry/entries to data recorder")
    upload_parser = subparsers.add_parser("upload", help="upload serialized data into data recorder")
    download_parser = subparsers.add_parser("download", help="download entries from data recorder into another format")
    search_parser = subparsers.add_parser("search", help="search for entries in data recorder")
    display_parser = subparsers.add_parser("display", help="display entries in data recorder")

    # print use cases for all the commands

    options = parser.parse_args()
    return options


def main():
    print ("\n***Welcome to Data Recorder!***\n\nThis tool will help you store records for Employees that include: %s" % SUPPORTED_RECORDS)
    print ("Curently, Data Recorder supports the following functions: %s\n" % FUNCTIONS)
    print ("Note: all entries will be stored in a database called 'main' by default unless otherwise specified.\n")
    args = parse_args()
    if args.command == "add":
        add_data()
    elif args.command == "search":
        search_data()
    elif args.command == "display":
        display_data()
    elif args.command == "upload":
        upload_data()
    elif args.command == "download":
        download_data()


if __name__ == '__main__':
    main()