################
Contact pipeline
################

Contacts can be imported after the customer has filled an xls file named
'Importation_contacts_v8.xls'.

Each sheet must be exported as csv file: with ',' separator and '"' as text wrapper.

The 'collective.contact.importexport' product (using transmogrifier) proposes:
    * a pipeline stored in the plone registry and writed on buildout root (as
      'pipeline.cfg') at each registry modification
    * a script named 'execute_pipeline.py' than can be run.

The server.dmsmail Makefile contains a section named 'pipeline' to run this
last script easier.

***
Run
***

* For a manual run, you can place the .csv files in the buildout 'imports' folder.
* Complete the paths in pipeline.cfg 'config' section.
* Check columns configuration (..._fieldnames) between csv and configuration
* If importing UVCW contacts, add organisation name in 'plonegroup_org_title'
* run `make pipeline` thats use 'pipeline.cfg'. If commit=1 in Makefile,
  result is committed. If commit=0, run `make pipeline commit=1` to really commit.

************
pipeline.cfg
************

This config file describes a pipeline using sections (some with parameters).
They are listed and named as hereafter.
Parameters are optional (O) or mandatory (M).

config
------
This section is the main one with common parameters.

Parameters:
    * creating_group = O, label of organisation configured as 'group_encoder'
    * directory_path = O, path of the directory to import in
    * csv_encoding = O, default utf8, csv files encoding
    * plonegroup_org_title = O, used when importing UVCW contacts to get the
      customer entry to use as 'plonegroup-organization'
    * organizations_filename = O, organizations csv file path
    * organizations_fieldnames = O, organizations csv columns names
    * persons_filename =O, persons csv file path
    * persons_fieldnames = O, persons csv columns names
    * held_positions_filename = O, held positions csv file path
    * held_positions_fieldnames = O, held positions csv columns names

initialization
--------------
.. autoclass:: collective.contact.importexport.blueprints.main.Initialization

csv_disk_source
---------------
.. autoclass:: collective.contact.importexport.blueprints.contactcsv.CSVDiskSourceSection

csv_ssh_source
--------------
.. autoclass:: collective.contact.importexport.blueprints.contactcsv.CSVSshSourceSection

csv_reader
----------
.. autoclass:: collective.contact.importexport.blueprints.contactcsv.CSVReaderSection
