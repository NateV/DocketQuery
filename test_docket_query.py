from docket_query import Docket, load_from_path, load_tree_from_path, \
                         convert_time, scrape_action, \
                         write_guilty_sequence_records, \
                         get_actions_with_sentences
import datetime
from io import StringIO
from lxml import etree
import pytest

def test_load_from_path():
  path = "./test/texts/CP-51-CR-0000001-2011_stitched_complete.xml"
  docket = load_from_path(path)
  assert "Glynnis" in docket

def test_load_tree_from_path():
  path = "./test/texts/CP-51-CR-0000001-2011_stitched_complete.xml"
  docket = load_tree_from_path(path)
  assert docket.getroot().tag == "docket"

def test_convert_time():
  assert convert_time("7 1/2","years") == datetime.timedelta(days=2737.5)

def test_scrape_action():
  action = etree.parse(StringIO("""<judge_action>
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
                       </judge_action>"""))
  action = scrape_action(action)
  assert action["date"] == "09/09/2011"
  assert action["min_length"] == datetime.timedelta(days=2737.5)
  assert action["judge"] == "Hill, Glynnis"

def test_write_guilty_sequence_records():
  docket = Docket("./test/texts/CP-51-CR-0000001-2011_stitched_complete.xml")
  assert write_guilty_sequence_records(docket, "./test/output/records.csv") == "Success"

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


class TestDocket:
    #TODO - need to test what get returns if docket is broken.

  def test_get_defendant_name(self):
    docket = Docket("./test/texts/CP-51-CR-0000001-2011_stitched_complete.xml")
    assert docket.get_defendant_name() == "Samuel Mccray"
    docket = Docket("./test/texts/CP-51-CR-0000012-2011_stitched_complete.xml")
    assert docket.get_defendant_name() == "Sergio V V. Moore"

  def test_get_defendant_birthdate(self):
    docket = Docket("./test/texts/CP-51-CR-0000001-2011_stitched_complete.xml")
    assert docket.get_defendant_birthdate() == "07/24/1964"
    docket = Docket("./test/texts/CP-51-CR-0000012-2011_stitched_complete.xml")
    assert docket.get_defendant_birthdate() == "02/24/1983"

  def test_get_docket_number(self):
    docket = Docket("./test/texts/CP-51-CR-0000001-2011_stitched_complete.xml")
    assert docket.get_docket_number() == "CP-51-CR-0000001-2011"
    docket = Docket("./test/texts/CP-51-CR-0000012-2011_stitched_complete.xml")
    assert docket.get_docket_number() == "CP-51-CR-0000012-2011"

  def test_get_guilty_sequence_records(self):
    docket = Docket("./test/texts/CP-51-CR-0000001-2011_stitched_complete.xml")
    records = docket.get_guilty_sequence_records()
    assert records[0]["judge"] == "Hill, Glynnis"
    assert records[0]["date"] == "09/09/2011"
    assert records[0]["charge"] == "Rape Forcible Compulsion"


    docket = Docket("./test/texts/CP-51-CR-0000012-2011_stitched_complete.xml")
    assert len(docket.get_guilty_sequence_records()) == 0
