from lxml import etree
import datetime
from fractions import Fraction
import csv

import pytest

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
      fix that?
"""

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
  if unit=="years":
    day_count = sum([float(Fraction(quantity)) * 365 for quantity in period.split()])
  elif unit=="months":
    day_count = sum([float(Fraction(quantty)) * 30.42]) # 30.41666 is the average
                                                   # length of a month in non
                                                   # leap-year.
  else:
    day_count = 0
  return datetime.timedelta(days=day_count)

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
  Output: A dict looking like:
    {
     "judge": "Hill, Glynnis",
     "date": "09/09/2011",
     "sentence_program": "Confinement",
     "min_length": <timedelta object>,
     "max_length": <timedelta object>
    }
  """
  judge = action.xpath("judge_name/text()")[0].strip()
  date = action.xpath("date/text()")[0].strip()
  program = action.xpath("sentence_info/program/text()")[0].strip()

  min_length_period = action.xpath("sentence_info/length_of_sentence/min_length/time/text()")[0].strip()
  min_length_unit = action.xpath("sentence_info/length_of_sentence/min_length/unit/text()")[0].strip()
  min_length = convert_time(min_length_period, min_length_unit)

  max_length_period = action.xpath("sentence_info/length_of_sentence/max_length/time/text()")[0].strip()
  max_length_unit = action.xpath("sentence_info/length_of_sentence/max_length/unit/text()")[0].strip()
  max_length = convert_time(max_length_period, max_length_unit)

  return     {"judge": judge,
              "date": date,
              "sentence_program": program,
              "min_length": min_length,
              "max_length": max_length}

def write_guilty_sequence_records(docket, destination, mode="w+"):
  """
  Input: 1) A Docket object,
         2) the name of a .csv file for saving the output
         3) File writing mode. Default is to create a new file/overwrite
            existing file.  "ab+" will probably be the other mode to use, for
            when processing many dockets and writing a .csv with lots of
            observations.
  Output: "Success" on success, and the method saves a .csv file
  """
  with open(destination, mode) as csvfile:
    fieldnames =  ["docket_number", "defendant_name", "birth_date", "judge", "date",
                   "charge", "disposition", "sentence_program", "min_length",
                   "max_length"]
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
    writer.writeheader()
    for record in docket.get_guilty_sequence_records():
      writer.writerow(record)
  csvfile.close()
  return "Success"

def get_actions_with_sentences(sequence):
  """
  Input: An lxml Element representing a docket disposition sequence.
  Output: A list of Elements such that each Element is:
          1) a child of the disposition sequence,
          2) a judge_action,
          3) has a sentence_info child.
  """
  return sequence.xpath("judge_action[sentence_info]")

class Docket():

  def __init__(self, path):
    self.tree = load_tree_from_path(path)

  def get_docket_number(self):
    return self.tree.xpath("/docket/header/docket_number/text()")[0].strip()

  def get_defendant_name(self):
    return self.tree.xpath("/docket/header/caption/defendant/text()")[0].strip()

  def get_defendant_birthdate(self):
    return self.tree.xpath("/docket/section[@name='Defendant_Information']/defendant_information/birth_date/text()")[0].strip()

  def get_guilty_sequence_records(self):
    """
    THIS IS A VERY IMPORTANT METHOD. It returns the 'observations' that
    analysis will be based on.

    Method returns a list of dictionaries with data describing the sentencing for
    offenses with guilty dispositions (pleas or not).  The dictionary has
    the following form:
    {"docket_number": "",
     "defendant_name": "",
     "birth_date": "",
     "judge": "",
     "date": "",
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
       charge = sequence.xpath("sequence_description/text()")[0].strip()
       disposition = sequence.xpath("offense_disposition/text()")[0].strip()
       actions_with_sentences = get_actions_with_sentences(sequence)
       for action in actions_with_sentences:
         action_dict = scrape_action(action)
         action_dict.update(base_record)
         action_dict.update({"charge":charge, "disposition":disposition})
         records.append(action_dict)
    return records