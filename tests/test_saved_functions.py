from DocketQuery.saved_functions import docket_number_and_name
from lxml import etree

def test_docket_number_and_name():
  # docket_number_and_name is a very simple example function that can
  # be passed to an AskADocket object.
  file_name = "tests/texts/CP-51-CR-0000001-2011_stitched_complete.xml"
  results = docket_number_and_name(etree.parse(file_name))
  assert results["docket_number"] == "CP-51-CR-0000001-2011"
  assert results["defendant_name"] == "Samuel Mccray"