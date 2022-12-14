# data_recorder

<h2> Data Recorder </h2>

<p>
Data Recorder is a commandline tool that is used to add data entries for employees.
It stores the following records: employee ID, name, address and phone number and aims
to automate data handling in the simplest way possible.

The tool currently supports the following different functionalities:
- adding a new entry manually
- uploading serialized data (json, csv, yaml, xml)
- downloading serialized data (json, csv, yaml, xml)
- searching data based on fields (id, name, address, phone)
- converting file formats (json, csv, yaml, xml)
- displaying data records (text/html)
</p>

<br>
<h3> Installation and Usage </h3>
Clone the repository using the link -> 
 git clone https://github.com/sura1128/data_recorder.git <br><br>

To run the tool ->
 ```python data_recorder.py -h```

To learn more info about the tool ->
 ```python data_recorder.py info```

To add data manually ->
 ```python data_recorder.py add```
<br>When prompted, enter the number of entries and following details.
<br> Please note that entries with duplicate IDs will not be added as the ID needs to be unique for each employee.

To display all data -> 
 ```python data_recorder.py display -h```
<br>This will show you the formats available to display.

If you want to see text output on shell -> 
 ```python data_recorder.py display text```

If you want to see html output on web browser -> 
 ```python data_recorder.py display html```
 
If you want to search for a field ->
 ```python data_recorder.py search```
 <br> When prompted, enter the field you would like to search. For eg. name
 <br> And then enter the word you are searching for. For eg. "John"
 
 If you want to upload a file containing data entries ->
  ```python data_recorder.py upload```
 <br> When prompted, enter the full path of the source file. For eg. "./my_entries.csv".
 <br> Please note that each of the supported formats need to use a standard template. Please refer to the examples/ folder for more templates.
 
If you want to download a file containing all the data entries ->
  ```python data_recorder.py download```
<br> When prompted, enter the full path of the destination file. For eg. "./my_downloads.csv".

If you want to convert a file (for eg. my_data.csv) to another supported format (for eg. my_data.yaml) ->
 ```python data_recorder.py convert```
<br> When prompted, enter the full paths of the source and destination files.


<h3> Adding a new storage format </h3>
Let's say you want to add a storage format for '.txt'. Here are steps you can take to achieve this:<br>

1. The new format needs to be added to list of supported formats in <b>data_recorder.py</b> :<br>
   ``` SUPPORTED_FORMATS = ["json", "csv", "yaml", "xml", "txt"] ``` <br>
 
2. Once that is done, you will need to extend the class <b>FormatHandler</b> in <b>data_handler.py</b>: <br>
This is the format that needs to be followed for the naming of the function. <br>

``` 
def upload_txt_data(self):
    <add your logic here>
        
    return
 ```
 
The same format can be followed for the download function.

<br>
<h3> Constraints and Improvements </h3>
Data Recorder is not using a database at the moment. Instead, it stores all information
into a .json file called main.json which is located in the same folder as the tool itself.

In the future, we can try moving to an sqlite3 database to store and index the records.

Right now, adding is the only function possible. However, the following features can be explored:
- updating an existing record
- deleting an existing record
- an API to add new fields
- an API to add new formats

<br>
<h3> Running Unit Cases </h3>
To run the unit cases for <b>data_recorder.py</b> -> 
   ```python data_recorder_tests.py```
<br>To run the unit cases for <b>data_handler.py</b> -> 
   ```python data_handler_tests.py```
