"""
This module parses the sample-enroll.843 file. The file name is hard coded into the script. The module parses
the 843 file one line at a time and builds a record dictionary. Once the record dictionary is complete, it is
persisted to a MongoDB collection.
"""

import const
import datetime
import os
from pymongo import MongoClient

#The record currently being processed
record = dict()

#The coverage currently being processed
current_processing_coverage = ''

#All of the communication qualifiers
communication_number_qualifier = {'AP': 'alternate_telephone',
                                  'BN': 'beeper_number',
                                  'CP': 'cellular_phone',
                                  'EM': 'electronic_mail',
                                  'EX': 'telephone_extension',
                                  'FX': 'facsimile',
                                  'HP': 'home_phone',
                                  'TE': 'telephone',
                                  'WP': 'work_phone'}
#End of line notation
const.line_ending = '~\n'

"""
Parses a line from the 843 file.

@param str_line - The line to be parsed
"""
def parse_line(str_line):
    line_collection = str_line.split('*')

    if line_collection[0] == 'INS':
        record['response_code'] = line_collection[1].upper()
        record['relationship_code'] = line_collection[2].upper()
        record['maintenance_code'] = line_collection[3].upper()
        record['maintenance_reason_code'] = line_collection[4].upper()
        record['benefit_status_code'] = line_collection[5].upper()
        record['medicare_status_code'] = line_collection[6].upper()
        record['eligibility_reason_code'] = line_collection[7].upper()
        record['employment_status_code'] = line_collection[8].upper().replace(const.line_ending, '')
    elif line_collection[0] == 'REF' and line_collection[1] == '0F':
        record['subscriber_number'] = line_collection[2].replace(const.line_ending, '')
    elif line_collection[0] == 'REF' and line_collection[1] == '1L':
        record['group_policy_number'] = line_collection[2].replace(const.line_ending, '')
    elif line_collection[0] == 'DTP' and line_collection[1] == '356':
        if line_collection[2] == 'D8':
            record['eligibility_begin_date'] = datetime.datetime.strptime(line_collection[3].replace(const.line_ending, ''),'%Y%m%d')
    elif line_collection[0] == 'NM1':
        record['last_name'] = line_collection[3].upper()
        record['first_name'] = line_collection[4].upper()
        record['middle_name'] = line_collection[5].upper()
        record['name_prefix'] = line_collection[6].upper()
        record['name_suffix'] = line_collection[7].upper()

        if line_collection[8] == '34':
            record['social_security_number'] = line_collection[9].replace(const.line_ending, '')
        elif line_collection[8] == 'ZZ':
            record['mutually_defined_number'] = line_collection[9].replace(const.line_ending, '')
    elif line_collection[0] == 'PER':
        if line_collection[3] in communication_number_qualifier:
            record[communication_number_qualifier[line_collection[3]]] = line_collection[4]

        if line_collection[5] in communication_number_qualifier:
            record[communication_number_qualifier[line_collection[5]]] = line_collection[6]

        if line_collection[7] in communication_number_qualifier:
            record[communication_number_qualifier[line_collection[7]]] = line_collection[8].replace(const.line_ending, '')
    elif line_collection[0] == 'N3':
        record['address1'] = line_collection[1].upper()
        record['address2'] = line_collection[2].upper()
    elif line_collection[0] == 'N4':
        record['city'] = line_collection[1].upper()
        record['state'] = line_collection[2].upper()
        record['postal_code'] = line_collection[3]
        record['country_code'] = line_collection[4]
        record['location_qualifier'] = line_collection[5]
        record['location_identifier'] = line_collection[6]
        record['country_subdivision_code'] = line_collection[7].replace(const.line_ending, '')
    elif line_collection[0] == 'DMG':
        if line_collection[1] == 'D8':
            record['birth_date'] = datetime.datetime.strptime(line_collection[2].replace(const.line_ending, ''),'%Y%m%d')

        record['gender_code'] = line_collection[3].upper().replace(const.line_ending, '')
    elif line_collection[0] == 'HD':
        coverage = dict()
        coverage['maintenance_type_code'] = line_collection[1]
        coverage['maintenance_reason_code'] = line_collection[2]
        coverage['insurance_line_code'] = line_collection[3].replace(const.line_ending, '')
        global current_processing_coverage
        current_processing_coverage = coverage['insurance_line_code'] + '_coverage'
        record[current_processing_coverage] = coverage
    elif line_collection[0] == 'DTP' and line_collection[1] == '348':
        coverage = record[current_processing_coverage]

        if line_collection[2] == 'D8':
            coverage['coverage_begin_date'] = datetime.datetime.strptime(line_collection[3].replace(const.line_ending, ''),'%Y%m%d')

"""
Reads the sample-enroll.843 and processes the file line-by-line
"""
def read_file():
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    with open(os.path.join(__location__, '..\\resources\\sample-enroll.834')) as data:
        for each_line in data:
            if (each_line.startswith('INS') or each_line.startswith('SE')) and record.items() != 0:
                record_id = records_collection.insert(record)
                print(record_id)
                record.clear()

            parse_line(each_line)


###############################################################################
# Start of main application
###############################################################################
client = MongoClient()
subscriber_db = client.subscriber_db
records_collection = subscriber_db.records_collections

read_file()
query1 = records_collection.find( { 'HLT_coverage.insurance_line_code': 'HLT' }, fields = {'last_name': 1, 'first_name': 1, 'social_security_number': 1 } )
records = dict((entry['_id'], entry) for entry in query1)
print(records)

query2 = records_collection.find( { 'HLT_coverage.coverage_begin_date': {'$gte': datetime.datetime.strptime('20130809', '%Y%m%d')} }, {'last_name': 1, 'first_name': 1, 'social_security_number': 1 } )
records = dict((entry['_id'], entry) for entry in query2)
print(records)
