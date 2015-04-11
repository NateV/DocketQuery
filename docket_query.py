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
"""

def load_from_path(path):
  """
  In: A path pointing to a docket
  Out: The text of the docket, utf-8 encoded.
  """
  pass





class Docket():

  def __init__(self, path):
    self.text = load_from_path(path)

  def get_defendant_name(self):
    pass

  def get_defendant_birthdate():
    pass

