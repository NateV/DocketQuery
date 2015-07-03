from DocketQuery.docket_query import AskADocket
from DocketQuery.saved_functions import docket_number_and_name

from lxml import etree
import pytest

def test_docket_number_and_name():
  # docket_number_and_name is a very simple example function that can
  # be passed to an AskADocket object.
  file_name = "tests/texts/CP-51-CR-0000001-2011_stitched_complete.xml"
  results = docket_number_and_name(etree.parse(file_name))
  assert results["docket_number"] == "CP-51-CR-0000001-2011"
  assert results["defendant_name"] == "Samuel Mccray"

class TestAskADocket:

  def setup_method(self, method):
    self.file_name = "tests/texts/CP-51-CR-0000001-2011_stitched_complete.xml"

  def test_scrape_docket(self):
    scraper = AskADocket(docket_number_and_name)
    results = scraper.scrape_docket(self.file_name)
    assert results["docket_number"] == "CP-51-CR-0000001-2011"
    assert results["defendant_name"] == "Samuel Mccray"

  def test_scrape_directory(self):
    dir = "tests/texts/"
    scraper = AskADocket(docket_number_and_name)
    results, counts = scraper.scrape_directory(dir)
    assert counts["successes"] == counts["total"]
    assert counts["total"] != 0
    for result in results:
      if result["docket_number"] == "CP-51-CR-0000001-2011":
        assert result["defendant_name"] == "Samuel Mccray"
      elif result["docket_number"] == "CP-51-CR-0000012-2011":
        assert result["defendant_name"] == "Sergio V V. Moore"