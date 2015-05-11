from lxml import etree
import datetime
from fractions import Fraction
import csv
import os
import glob
import re
import logging

import pytest # For debugging.

"""
docket_query is a tool for retrieving information from a criminal docket that
has been parsed into xml with docket_parse.

docket_query has a Class, Docket.
Outline:
1) A Docket is instantiated with a path to an
   xml docket.
2) The user calls methods on Docket to retrieve useful information from the
   Docket.  For example, docket.get_defendant_name() returns the name of the
   defendant to which the docket relates.

TODO: A user can't customize queries without editing this module. Maybe
      fix that?  Or call it a feature?
"""

def query_directory(path, records_destination, errors_destination):
  """
  In: A path to a directory containing xml files representing dockets and
      a path to a file where the results will be saved. Should be a .csv
      file.
  Output: A list of dicts written and a list of errors that occurred.
  """
  records = []
  errors = []
  files_iterator = glob.iglob(path) #TODO: should make the glob more
                                    #      restrictive.
  for file in files_iterator:
    docket = Docket(file)
    new_records_list, new_errors = docket.get_guilty_sequence_records()
    records = records + new_records_list
    errors = errors + new_errors

  write_guilty_sequence_records(records, records_destination, errors, errors_destination, mode="a")
  return records, errors

def load_from_path(path):
  """
  In: A path pointing to a docket
  Out: The text of the docket, utf-8 encoded.
  N.B. I'm not sure if I'll need this, actually.
  """
  with open(path) as f:
    docket_text = f.read()
  f.close()
  return docket_text

def load_tree_from_path(path):
  """
  In: A path pointing to a docket.
  Out: An etree of the docket.
  """
  return etree.parse(path)

def convert_time(period, unit):
  """
  In: A period of time as a number and the unit of that number, as in:
      ("7 1/2", "years")
  Out: A timedelta object of the input time period.
  """
  year_pattern = re.compile("year", flags=re.I)
  month_pattern = re.compile("month", flags=re.I)
  if re.search(year_pattern, unit) != None:
    day_count = sum([float(Fraction(quantity)) * 365 for quantity in period.split()])
  elif re.search(month_pattern, unit) != None:
    day_count = sum([float(Fraction(quantity)) * 30.42 for quantity in period.split()])
                # 30.41666 is the average length of a month in non
                # leap-year.
  else:
    day_count=0
  return datetime.timedelta(days=day_count)

def scrape_sentence_info(sentence):
  """
  Input: an etree.Element looking like:
  <sentence_info>
              <program>IPP</program>
              <length_of_sentence>
                <min_length>
                  <time>12.00</time>
                  <unit>Months</unit>
                </min_length>
                <max_length>
                  <time>12.00</time>
                  <unit>Months</unit>
                </max_length>
              </length_of_sentence>
              <date>03/02/2011</date>
              <extra_sentence_details>12 months... HOUSE ARREST FOR FIRST 3 MONTHS. SHERIFF TO T RANSPORT... Complete 20 hours community service...</extra_sentence_details>
            </sentence_info>
  Output: A dict looking like:
        {"sentence_program": "IPP",
         "min_length": <timedelta days=365>,
         "max_length": <timedelta days=365>}
  """
  program = xpath_or_log(sentence, "program/text()", "program")
  min_length_time = xpath_or_log(sentence, "length_of_sentence/min_length/time/text()", "min_length_time")
  min_length_unit = xpath_or_log(sentence, "length_of_sentence/min_length/unit/text()", "min_length_unit")
  max_length_time = xpath_or_log(sentence, "length_of_sentence/max_length/time/text()", "max_length_time")
  max_length_unit = xpath_or_log(sentence, "length_of_sentence/max_length/unit/text()", "max_length_unit")
  return {"sentence_program": program,
          "min_length": convert_time(min_length_time, min_length_unit),
          "max_length": convert_time(max_length_time, max_length_unit)}

def scrape_action(action):
  """
  Input: a etree.Element looking like:
         <judge_action>
           <judge_name> Hill, Glynnis </judge_name>
           <date> 09/09/2011 </date>
           <sentence_info>
             <program> Confinement </program>
             <length_of_sentence>
               <min_length>
                 <time> 7 1/2  </time>
                 <unit> years  </unit>
               </min_length>
                 <max_length>
                   <time> 15  </time>
                   <unit> years </unit>
                 </max_length>
             </length_of_sentence>
             <date> 09/09/2011 </date>
           <extra_sentence_details>
             DEFENDANT FOUND NOT TO BE SEXUAL PREDITOR,
             LIFE TIME REGISTRATION WITH STATE...
             POLICE; RESIDENCE, EMPLOYMENT, SCHOOL, PAY COURT COST
             &amp; FINES, SENTENCE TO RUN...
             CONSECUTIVE WITH ANY OTHER SENTENCE PRESENTLY
             SERVING...
           </extra_sentence_details>
           </sentence_info>
         </judge_action>
  Output: A list containing dicts looking like:
    {
     "judge": "Hill, Glynnis",
     "action_date": "09/09/2011",
     "sentence_program": "Confinement",
     "min_length": <timedelta object>,
     "max_length": <timedelta object>
    }
  """
  actions = []
  judge = xpath_or_log(action, "judge_name/text()", "judge")
  date = xpath_or_log(action, "date/text()", "action_date")
  base_action = {"judge":judge,
                 "action_date":date}
  for sentence in action.xpath("sentence_info"):
    new_action = scrape_sentence_info(sentence)
    new_action.update(base_action)
    actions.append(new_action)
  return actions

def write_guilty_sequence_records(records, records_destination, errors, errors_destination, mode="w+"):
  """
  Input: 1) Records from dockets,
         2) the name of a .csv file for saving the output
         3) File writing mode. Default is to create a new file/overwrite
            existing file.  "ab+" will probably be the other mode to use, for
            when processing many dockets and writing a .csv with lots of
            observations.
  Output: The list of dicts with the observations recorded.
  """
  with open(records_destination, mode, newline='') as csvfile:
    fieldnames =  ["docket_number", "defendant_name", "birth_date", "judge", "action_date",
                   "charge", "disposition", "sentence_program", "min_length",
                   "max_length"]
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
    writer.writeheader()
    for record in records:
      writer.writerow(record)
  csvfile.close()

  with open(errors_destination, mode, newline='') as errors_file:
    fieldnames =["file", "error_field"]
    writer = csv.DictWriter(errors_file, fieldnames = fieldnames)
    writer.writeheader()
    for error in errors:
      writer.writerow(error)
  errors_file.close()

  return records, errors

def get_actions_with_sentences(sequence):
  """
  Input: An lxml Element representing a docket disposition sequence.
  Output: A list of Elements such that each Element is:
          1) a child of the disposition sequence,
          2) a judge_action,
          3) has a sentence_info child.
  """
  return sequence.xpath("judge_action[sentence_info]")

def xpath_or_log(element, query_string, variable_sought):
  """
  This method is for retrieving a text value from an xml element.
  It is only to be used when there is only one of the desired value in
  the xml element.

  Input: 1) An etree element.
         2) The xpath query for the variable being sought
         3) The name of the variable sought, to include in the
            returned "[variable] unknown" if the query doesn't work.
  Output: 1) The text of the variable sought, if possible, or
          2) a string "[variable] unknown" if the query does not find
             text.
          3) Writes to a log if the variable's not found.
  """
  query_results = element.xpath(query_string)
  if len(query_results) > 0:
    return query_results[0].strip()
  else:
    #TODO: Log something?
    return "%s unknown" % variable_sought


class Docket():

  def __init__(self, path):
    self.path = path
    self.tree = load_tree_from_path(path)

  def get_docket_number(self):
    return xpath_or_log(self.tree, "/docket/header/docket_number/text()", "docket_number")

  def get_defendant_name(self):
    return xpath_or_log(self.tree, "/docket/header/caption/defendant/text()", "defendant_name")

  def get_defendant_birthdate(self):
    return xpath_or_log(self.tree, "/docket/section[@name='Defendant_Information']/defendant_information/birth_date/text()", "defendant_birthdate")

  def get_guilty_sequence_records(self):
    """
    THIS IS A VERY IMPORTANT METHOD. It returns the 'observations' from a
    docket that analysis will be based on.

    Method returns a list of dictionaries with data describing the sentencing for
    offenses with guilty dispositions (pleas or not).  The dictionary has
    the following form:
    {"docket_number": "",
     "defendant_name": "",
     "birth_date": "",
     "judge": "",
     "action_date": "",
     "charge": "",
     "disposition": "",
     "sentence_program": "",
     "min_length": "",
     "max_length": ""
    }
    With these observations, I will be able to correlate sentence lengths,
    judges, and charges.
    """
    records = [] #Initialize empty list of records.

    # Getting a few values that will be in every observation taken from this
    # docket.
    base_record = {"docket_number": self.get_docket_number(),
                   "defendant_name": self.get_defendant_name(),
                   "birth_date" : self.get_defendant_birthdate()}

    guilty_sequences = self.tree.xpath("//sequence[contains(./offense_disposition, 'Guilty') and (judge_action/sentence_info/length_of_sentence)]")
    for sequence in guilty_sequences:
       charge = xpath_or_log(sequence, "sequence_description/text()", "charge")
       disposition = xpath_or_log(sequence, "offense_disposition/text()", "offense_disposition")
       actions_with_sentences = get_actions_with_sentences(sequence)
       for action in actions_with_sentences:
         action_list = scrape_action(action)
         for action_dict in action_list:
           action_dict.update(base_record)
           action_dict.update({"charge":charge, "disposition":disposition})
           records.append(action_dict)

    errors = []
    for record in records:
      for key, value in record.items():
        if "length" not in key:
          if "unknown" in value:
            errors.append({"file": self.path,
                           "error_field": key})
        if key == "length":
          if value==datetime.timedelta(days==0):
            errors.append({"file": self.path,
                           "error_field":key})

    return records, errors


















