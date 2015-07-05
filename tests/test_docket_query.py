from DocketQuery.docket_query import AskADocket, dicts2csv
from DocketQuery.saved_functions import docket_number_and_name

from lxml import etree
import pytest
from io import StringIO
import csv

def test_docket_number_and_name():
  # docket_number_and_name is a very simple example function that can
  # be passed to an AskADocket object.
  file_name = "tests/texts/CP-51-CR-0000001-2011_stitched_complete.xml"
  errors, results = docket_number_and_name(etree.parse(file_name), file_name)
  assert results[0]["docket_number"] == "CP-51-CR-0000001-2011"
  assert results[0]["defendant_name"] == "Samuel Mccray"

def test_dicts2csv():
  result = [{'action_date': '09/09/2011', 'defendant_name': 'Samuel Mccray',
            'grade': 'F1', 'max_time': '15 years', 'birth_date': '07/24/1964',
            'judge_name': 'Hill, Glynnis', 'program': 'Confinement',
            'min_time': '7 1/2 years', 'charge_section': '18 § 3121 §§ A1',
            'date_initiated': '01/03/2011',
            'charge_desc': 'Rape Forcible Compulsion',
            'date_filed': '01/03/2011',
            'docket_number': 'CP-51-CR-0000001-2011'},
           {'action_date': '05/17/2011', 'defendant_name': 'Samuel Mccray',
            'grade': 'M1', 'max_time': '5 years', 'birth_date': '07/24/1964',
            'judge_name': 'Hill, Glynnis', 'program': 'Probation',
            'min_time': '5 years', 'charge_section': '18 § 907 §§ A',
            'date_initiated': '01/03/2011',
            'charge_desc': 'Poss Instrument Of Crime W/Int',
            'date_filed': '01/03/2011',
            'docket_number': 'CP-51-CR-0000001-2011'},
           {'action_date': '09/09/2011', 'defendant_name': 'Samuel Mccray',
            'grade': 'M1', 'max_time': '5 years',
            'birth_date': '07/24/1964', 'judge_name': 'Hill, Glynnis',
            'program': 'Probation', 'min_time': '5 years',
            'charge_section': '18 § 907 §§ A',
            'date_initiated': '01/03/2011',
            'charge_desc': 'Poss Instrument Of Crime W/Int',
            'date_filed': '01/03/2011',
            'docket_number': 'CP-51-CR-0000001-2011'}]
  errors = [{"error_file": "test.test","error_field":"test_field"},
            {"error_file": "file2.test","error_field":"test_other"}]
  counts = {"successes": 10, "total":10}
  errors_file, results_file, counts_file = dicts2csv(errors, result,
                                           open('tests/output/errors.csv','w'),
                                           open('tests/output/results.csv','w'),
                                           counts = counts,
                                           counts_file = open('tests/output/counts.csv','w'))
  errors_file.close()
  results_file.close()
  counts_file.close()
  with open('tests/output/results.csv')  as f:
    reader = csv.DictReader(f)
    assert "charge_section" in reader.fieldnames
  f.close()


class TestAskADocket:

  def setup_method(self, method):
    self.file_name = "tests/texts/CP-51-CR-0000001-2011_stitched_complete.xml"

  def test_scrape_docket(self):
    scraper = AskADocket(docket_number_and_name)
    errors, results = scraper.scrape_docket(self.file_name)
    assert results[0]["docket_number"] == "CP-51-CR-0000001-2011"
    assert results[0]["defendant_name"] == "Samuel Mccray"

  def test_scrape_directory(self):
    dir = "tests/texts/"
    scraper = AskADocket(docket_number_and_name)
    errors, results, counts = scraper.scrape_directory(dir)
    assert counts["successes"] == counts["total_dockets_scraped"]
    assert counts["total_dockets_scraped"] != 0
    for result in results:
      if result["docket_number"] == "CP-51-CR-0000001-2011":
        assert result["defendant_name"] == "Samuel Mccray"
      elif result["docket_number"] == "CP-51-CR-0000012-2011":
        assert result["defendant_name"] == "Sergio V V. Moore"