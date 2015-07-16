import pytest
import re
from fractions import Fraction
import datetime

#  This file contains functions used to scrape data from dockets.
#  Each function receives a docket as an lxml ElementTree and the name of the
#  file where that element tree comes from.  The file name is for error
#  logging purposes, so it could be some other identifier of the docket.
#  Each function must return two objects:
#    1) A list of dicts that represent errors.  Each dict has two fields,
#       "error_file" and "error_field".
#    2) A list of dicts that are observations pulled from dockets.


def docket_number_and_name(docket_tree, file_name):
  #Input: a docket as an ElementTree
  #Output: 1) A list of errors. Each error is a hash identifying the file
  #           and the field where the error arose.
  #        2) a list of 1 hash, which contains the name and docket number
  #           of the given docket.
  errors = []
  try:
    name = docket_tree.xpath("/docket/header/caption/defendant/text()")[0].strip()
  except Exception as e:
    errors.append({"error_file":file_name, "error_field": "defendant_name"})
    name = "unknown"
  try:
    number = docket_tree.xpath("/docket/header/docket_number/text()")[0].strip()
  except Exception as e:
    errors.append({"error_file":file_name, "error_field": "docket number"})
    number = "unknown"
  return errors, [{"defendant_name": name,
                   "docket_number": number}]


def docket_num_name_age(docket_tree, file_name):
  # Input: a docket as an ElementTree and the name of the file being
  #        scraped.
  # Output: List of errors and list of hashes containing the docket number,
  #         name, and age of the person in the docket.
  errors = []
  try:
    name = docket_tree.xpath("/docket/header/caption/defendant/text()")[0].strip()
  except Exception as e:
    errors.append({"error_file":file_name, "error_field": "defendant_name",
                   "message":e})
    name = "unknown"
  try:
    number = docket_tree.xpath("/docket/header/docket_number/text()")[0].strip()
  except Exception as e:
    errors.append({"error_file":file_name, "error_field": "docket number",
                   "message":e})
    number = "unknown"
  try:
    birth_date = docket_tree.xpath("/docket/section[@name='Defendant_Information']/defendant_information/birth_date/text()")[0].strip()
  except Exception as e:
    errors.append({"error_file":file_name, "error_field": "birth_date",
                   "message":e})
    birth_date = "unknown"
  try:
    docket_initiated = docket_tree.xpath("/docket/section[@name='Case_Information']/case_info/date_initiated/text()")[0].strip()
  except Exception as e:
    errors.append({"error_file":file_name, "error_field": "date_initiated",
                   "message":e})
    docket_initiated = "unknown"
  try:
    docket_filed = docket_tree.xpath("/docket/section[@name='Case_Information']/case_info/date_filed/text()")[0].strip()
  except Exception as e:
    errors.append({"error_file":file_name, "error_field": "date_filed",
                   "message":e})
    docket_filed = "unknown"
  return errors, [{"defendant_name": name,
                   "docket_number": number,
                   "birth_date": birth_date,
                   "date_initiated": docket_initiated,
                   "date_filed": docket_filed}]

def conviction_information(docket_tree, file_name):
  #  This function scrapes conviction information from a docket as well as
  #  basic information like docket name and defendant information.
  results = []
  errors, basic_info = docket_num_name_age(docket_tree, file_name)
  # Get a list of the sequences that have the word "guilty" in them.
  guilty_sequences = docket_tree.xpath("//sequence[contains(./offense_disposition, 'Guilty') and (judge_action/sentence_info/length_of_sentence)]")
  # Loop through sequences with guilty dispositions
  for i, sequence in enumerate(guilty_sequences):
    sequence_info = dict()
    sequence_info.update(basic_info[0]) # Load a copy of the basic info into the sequence_info dict.
    try:
      sequence_info["charge_desc"] = sequence.xpath("sequence_description/text()")[0].strip()
    except Exception as e:
      errors.append({"error_file":file_name,
                     "error_field": "sequence_{}/charge_desc".format(i),
                     "message":e})
      sequence_info["charge_desc"] = "unknown"
    try:
      sequence_info["charge_section"] = sequence.xpath("code_section/text()")[0].strip()
    except Exception as e:
      errors.append({"error_file":file_name,
                     "error_field": "sequence_{}/charge_section".format(i),
                     "message":e})
      sequence_info["charge_section"] = "unknown"
    try:
      sequence_info["grade"] = sequence.xpath("grade/text()")[0].strip()
    except Exception as e:
      errors.append({"error_file":file_name,
                     "error_field":"sequence_{}/grade".format(i),
                     "message":e})
      sequence_info["grade"] = "unknown"
    # Loop through actions within a sequence that have a sentence
    for i2, action in enumerate(get_actions_with_sentences(sequence)):
      action_info = dict()
      action_info.update(sequence_info) # Load a copy of the basic info and
                                        # sequence info into action_info.
      # Judge
      try:
        action_info["judge_name"] = action.xpath("judge_name/text()")[0].strip()
      except Exception as e:
        errors.append({"error_file":file_name,
                       "error_field":"sequence_{}/action_{}/judge_name".format(i,i2),
                       "message":e})
        action_info["judge_name"] = "unknown"
      # Date of action
      try:
        action_info["action_date"] = action.xpath("date/text()")[0].strip()
      except Exception as e:
        errors.append({"error_file":file_name,
                       "error_field":"sequence_{}/action_{}/date".format(i,i2),
                       "message":e})
        action_info["action_date"] = "unknown"
      # Loop through sentences in the action.
      for i3, sentence in enumerate(action.xpath("sentence_info")):
        sentence_info = dict()
        sentence_info.update(action_info)
        #Program
        try:
          sentence_info["program"] = sentence.xpath("program/text()")[0].strip()
        except Exception as e:
          errors.append({"error_file":file_name,
                         "error_field":"sequence_{}/action_{}/sentence_{}/program".format(i,i2, i3),
                         "message":e})
          sentence_info["program"] = "unknown"
        #Min length
        try:
          min_time = sentence.xpath("length_of_sentence/min_length/time/text()")[0].strip()
          min_unit = sentence.xpath("length_of_sentence/min_length/unit/text()")[0].strip()
          sentence_info["min_time"] = convert_time(min_time, min_unit).days
        except Exception as e:
          errors.append({"error_file":file_name,
                         "error_field":"sequence_{}/action_{}/sentence_{}/min_time".format(i,i2, i3),
                         "message":e})
          sentence_info["min_time"] = "unknown"
        #Max length
        try:
          max_time = sentence.xpath("length_of_sentence/max_length/time/text()")[0].strip()
          max_unit = sentence.xpath("length_of_sentence/max_length/unit/text()")[0].strip()
          sentence_info["max_time"] = convert_time(max_time, max_unit).days
        except Exception as e:
          errors.append({"error_file":file_name,
                         "error_field":"sequence_{}/action_{}/sentence_{}/max_time".format(i,i2, i3),
                         "message":e})
          sentence_info["max_time"] = "unknown"
        results.append(sentence_info)
        # End of loop through sentences
      # End of loop through actions
    # End of loop through sequences
  return errors, results

def final_disposition_information(docket_tree, file_name):
  #  Scrape information about all final dispositions.
  #  I think this will be almost exactly the same as conviction_information().
  pass











## HELPERS

def get_actions_with_sentences(sequence):
  """
  Input: An lxml Element representing a docket disposition sequence.
  Output: A list of Elements such that each Element is:
          1) a child of the disposition sequence,
          2) a judge_action,
          3) has a sentence_info child.
  """
  return sequence.xpath("judge_action[sentence_info]")


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

  program = sentence.xpath("program/text()")[0].strip()
  min_length_time = xpath_or_log(sentence, "length_of_sentence/min_length/time/text()", "min_length_time")
  min_length_unit = xpath_or_log(sentence, "length_of_sentence/min_length/unit/text()", "min_length_unit")
  max_length_time = xpath_or_log(sentence, "length_of_sentence/max_length/time/text()", "max_length_time")
  max_length_unit = xpath_or_log(sentence, "length_of_sentence/max_length/unit/text()", "max_length_unit")
  return {"sentence_program": program,
          "min_length": convert_time(min_length_time, min_length_unit),
          "max_length": convert_time(max_length_time, max_length_unit)}


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
    return ' '.join([period, unit, "(cannot parse time)"])
  return datetime.timedelta(days=day_count)
