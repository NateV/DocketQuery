from DocketQuery.saved_functions import docket_number_and_name, \
                                        docket_num_name_age, \
                                        conviction_information, \
                                        get_actions_with_sentences
from lxml import etree
import re
from io import StringIO
import pytest

def test_docket_number_and_name():
  # docket_number_and_name is a very simple example function that can
  # be passed to an AskADocket object.
  file_name = "tests/texts/CP-51-CR-0000001-2011_stitched_complete.xml"
  errors, results = docket_number_and_name(etree.parse(file_name), file_name)
  assert len(errors) == 0
  assert results[0]["docket_number"] == "CP-51-CR-0000001-2011"
  assert results[0]["defendant_name"] == "Samuel Mccray"


def test_docket_num_and_age():
  file_name = "tests/texts/CP-51-CR-0000001-2011_stitched_complete.xml"
  errors, results = docket_num_name_age(etree.parse(file_name), file_name)
  assert results[0]["birth_date"] == "07/24/1964"
  assert results[0]["date_filed"] == "01/03/2011"


def test_conviction_information():
  file_name = "tests/texts/CP-51-CR-0000001-2011_stitched_complete.xml"
  errors, results = conviction_information(etree.parse(file_name), file_name)
  assert re.match(re.compile('Rape', flags=re.I), results[0]["charge_desc"])
  assert re.match(re.compile('.*3121.*'), results[0]["charge_section"])
  assert results[0]['max_time'] == 5475




#Testing helpers
def test_get_actions_with_sentences():
  sequence = etree.parse(StringIO("""<sequence>
            <sequence_num>1</sequence_num>
            <sequence_description>Rape Forcible Compulsion</sequence_description>
            <offense_disposition>Guilty Plea - Negotiated</offense_disposition>
            <grade>F1</grade>
            <code_section>18 § 3121 §§ A1</code_section>
            <judge_action>
              <judge_name>Hill, Glynnis</judge_name>
              <date>05/17/2011</date>
            </judge_action>
            <judge_action>
              <judge_name>Hill, Glynnis</judge_name>
              <date>09/09/2011</date>
              <sentence_info>
                <program>Confinement</program>
                <length_of_sentence>
                  <min_length>
                    <time>7 1/2</time>
                    <unit>years</unit>
                  </min_length>
                  <max_length>
                    <time>15</time>
                    <unit>years</unit>
                  </max_length>
                </length_of_sentence>
                <date>09/09/2011</date>
                <extra_sentence_details>DEFENDANT FOUND NOT TO BE SEXUAL PREDITOR, LIFE TIME REGISTRATION WITH STATE... POLICE; RESIDENCE, EMPLOYMENT, SCHOOL, PAY COURT COST &amp; FINES, SENTENCE TO RUN... CONSECUTIVE WITH ANY OTHER SENTENCE PRESENTLY SERVING...</extra_sentence_details>
              </sentence_info>
            </judge_action>
          </sequence>"""))
  actions = get_actions_with_sentences(sequence)
  assert len(actions) == 1
  assert actions[0].xpath("date/text()")[0].strip() == "09/09/2011"
