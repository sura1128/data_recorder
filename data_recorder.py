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
import sys
import argparse
from collections import OrderedDict
from tabulate import tabulate

import sqlite3

from data_handler import FormatHandler, DataRecord

DB_PATH = "./main.json"
DB_CAPACITY = 100
DEFAULT_FORMAT = "json"
SUPPORTED_FORMATS = ["json", "csv", "yaml", "xml"]

FUNCTIONS = ["add", "upload", "download", "search", "display"]
SUPPORTED_RECORDS = ["id", "name", "address", "phone"]

SUPPORT_EMAIL_ALIAS = "data-recorder-help@gmail.com"

def add_data():
    # Should there be an upper limit? going to assume our DB can't take more than 100 entries as an example.
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
        while True:
            n_id = input("Enter the id: ")
            if is_duplicate(n_id):
                print ("This ID already exists in our data records. ID is unique for each entry so please re-enter this.")
                continue
            else:
                break
        name = input("Enter the name: ")
        address = input("Enter the address: ")
        phone = input("Enter phone number: ")

        data_record = DataRecord(n_id, name, address, phone)
        data_record_dict = data_record.to_dict()
        data_entries.append(data_record_dict)
        num_entry += 1

    push_to_db(data_entries)
    # push_to_database(data_entries)

def is_duplicate(n_id):
    existing_data = pull_from_db()
    if not existing_data:
        print ("There are no data records in the DB to display. Exiting.")
        return
    data_records = existing_data.get("data_records")
    for record in data_records:
        if str(n_id) == record.get("id"):
            return True
    return False


def push_to_db(data_entries):
    existing_data = []
    try:
        with open(DB_PATH) as filehandler:
            existing_data = json.load(filehandler)
            existing_data.get("data_records").extend(data_entries)
        with open(DB_PATH, 'w') as filehandler:
            json.dump(existing_data, filehandler, indent=4)
    except OSError as e:
        print ("Error: Unable to upload data to DB. Please contact [%s]." % SUPPORT_EMAIL_ALIAS)


def pull_from_db():
    if not os.path.exists(DB_PATH):
        print ("%s appears to be offline. Cannot display any data." % DB_PATH)
        return
    try:
        with open(DB_PATH) as filehandler:
            existing_data = json.load(filehandler)
    except OSError as e:
        print ("Error: Unable to download data from DB. Please contact [%s]." % SUPPORT_EMAIL_ALIAS)
    return existing_data

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


def search_data():
    existing_data = pull_from_db()
    if not existing_data:
        print ("There are no data records in the DB to display. Exiting.")
        return
    data_records = existing_data.get("data_records")

    # More features: starting with, ends with, contains
    search_field = input("Which of the following fields would you like to use for searching: %s\n" % SUPPORTED_RECORDS)
    if search_field.lower() not in SUPPORTED_RECORDS:
        print ("The field [%s] does not exist in our records. Please contact [%s] if you'd like to add a new field or try again." % (search_field, SUPPORT_EMAIL_ALIAS))
        return
    search_value = input("What %s would you like to search for: " % search_field)

    found_entries = []
    print ("Searching for %s amongst %s in entries...\n" % (search_value, search_field))
    for record in data_records:
        if search_value.lower() in record.get(search_field).lower():
            found_entries.append(record)
    
    if not found_entries:
        print ("There are no matching entries with '%s' in [%s]." % (search_value, search_field))
        return

    print ("Here are the matching entries with '%s' in [%s]:" % (search_value, search_field))
    tabular_list = []
    for entry in found_entries:
        tabular_list.append(entry.values())
    print(tabulate(tabular_list,  headers=SUPPORTED_RECORDS, tablefmt='orgtbl'))
    print("\n")


def display_data():
    existing_data = pull_from_db()
    if not existing_data:
        print ("There are no data records in the DB to display. Exiting.")
        return
    data_records = existing_data.get("data_records")
    tabular_list = []
    for entry in data_records:
        tabular_list.append(entry.values())
    print(tabulate(tabular_list,  headers=SUPPORTED_RECORDS, tablefmt='orgtbl'))
    print("\n")


def upload_data():
    src = input("Please provide the full path to the source file for uploading data (eg. my_dir/path_to_file.csv): ")
    src_name, src_ext = os.path.splitext(src)
    src_ext = src_ext.split(".")[-1] # remove '.' from extension

    if not os.path.exists(src):
        print ("The filepath [%s] does not exist, please try again." % src)
        return

    if src_ext not in SUPPORTED_FORMATS:
        print ("This file format is not supported currently. Please contact [%s] to request for a new format." % SUPPORT_EMAIL_ALIAS)
    else:
        print ("Uploading data from: %s..." % src)
        formathandler = FormatHandler(src_ext, src)
        formathandler.upload()


def download_data():
    print ("Downloading data...")

    dest = input("Please provide the full path to the destination file for downloading data (eg. my_dir/path_to_file.csv): ")
    dest_name, dest_ext = os.path.splitext(dest)
    dest_ext = dest_ext.split(".")[-1] # remove '.' from extension

    if dest_ext not in SUPPORTED_FORMATS:
        print ("This file format is not supported currently. Please contact [%s] to request for a new format." % SUPPORT_EMAIL_ALIAS)
    else:
        print ("Downloading data to: %s..." % dest)
        formathandler = FormatHandler(dest_ext, dest)
        formathandler.download()


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="commands", dest="command")
    
    add_parser = subparsers.add_parser("add", help="manually add entry/entries to data recorder")
    upload_parser = subparsers.add_parser("upload", help="upload serialized data into data recorder")
    download_parser = subparsers.add_parser("download", help="download entries from data recorder into another format")
    search_parser = subparsers.add_parser("search", help="search for entries in data recorder")
    display_parser = subparsers.add_parser("display", help="display entries in data recorder")

    options = parser.parse_args()
    return options


def create_db():
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, 'w') as filehandler:
            json.dump({"data_records": []}, filehandler, indent=4)
    try:
        with open(DB_PATH) as filehandler:
            json.load(filehandler)
    except json.decoder.JSONDecodeError:
        with open(DB_PATH, 'w') as filehandler:
            json.dump({"data_records": []}, filehandler, indent=4)


def main():
    print ("\n***Welcome to Data Recorder!***\n\nThis tool will help you store records for Employees that include: %s" % SUPPORTED_RECORDS)
    print ("Curently, Data Recorder supports the following functions: %s\n" % FUNCTIONS)
    print ("Note: all entries will be stored in a database called 'main' by default unless otherwise specified.\n")
    args = parse_args()

    create_db()

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