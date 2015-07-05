
# A user provides docket_query a directory or a single completely parsed
# criminal records docket, `docket`
# and a function `f`, such `f(docket)` returns a set of csv rows with
# data scraped from the docket.

from lxml import etree
import glob
import pytest
import io
from io import StringIO
import csv

class AskADocket:

  def __init__(self, fun):
    #Input: A function
    self.scrape_function = fun

  def scrape_docket(self, docket):
    # Input: Path to a parsed docket file.  Could be a file object or StringIO object
    # Output: A list of errors, each of which is a dict,
    #         A list of results, each of which is a dict that is the result
    #         of applying the function
    #         A dict with the total count of dockets scraped.
    return self.scrape_function(etree.parse(docket), docket)

  def scrape_directory(self, directory_path):
    successes = 0
    total = 0
    results = []
    errors = []
    for file in glob.iglob(directory_path + "*.xml"):
      total += 1
      try:
        file_errors, file_results = self.scrape_docket(file)
        results += file_results
        errors += file_errors
        successes += 1
      except Exception as e:
        print("Error while parsing {}.".format(file))
        print(e)
    return errors, results, {"total_dockets_scraped": total, "successes": successes}


def dicts2csv(errors, results, error_file, results_file, counts = {}, counts_file = None):
  # Input: a list of hashes which will become the rows of a csv table
  # Output: Writes errors and results to two csv files (or file-like objects)

  # Writing errors:
  error_fields = errors[0].keys() if errors else ["No errors reported"]
  writer = csv.DictWriter(error_file, delimiter=',',quotechar='|',
                          fieldnames=error_fields)
  writer.writeheader()
  for error in errors: writer.writerow(error)

  # Writing results
  results_fields = results[0].keys() if results else ["No results reported"]
  writer = csv.DictWriter(results_file, delimiter=',', quotechar='|',
                          fieldnames=results_fields)
  writer.writeheader()
  for result in results: writer.writerow(result)

  # Writing counts
  if counts:
    counts_fields = counts.keys()
    writer = csv.DictWriter(counts_file, delimiter=',', quotechar='|',
                           fieldnames=counts_fields)
    writer.writeheader()
    writer.writerow(counts)
    return error_file, results_file, counts_file
  return error_file, results_file




# Example functions
def docket_number_and_name(docket_tree, file_name):
  #Input: a docket as an ElementTree
  #Output: a list of 1 hash, which contains the name and docket number
  #        of the given docket.
  errors = []
  try:
    name = docket_tree.xpath("/docket/header/caption/defendant/text()")[0].strip()
  except:
    errors.append({"error_file":file_name, "error_field": "defendant_name"})
  try:
    number = docket_tree.xpath("/docket/header/docket_number/text()")[0].strip()
  except:
    errors.append({"error_file":file_name, "error_field": "docket number"})
  return errors, [{"defendant_name": name,
                   "docket_number": number}]
