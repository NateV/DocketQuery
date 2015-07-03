
# A user provides docket_query a directory or a single completely parsed
# criminal records docket, `docket`
# and a function `f`, such `f(docket)` returns a set of csv rows with
# data scraped from the docket.

from lxml import etree
import glob

class AskADocket:

  def __init__(self, fun):
    #Input: A function
    self.scrape_function = fun

  def scrape_docket(self, docket):
    # Input: Path to a parsed docket file.  Could be a file object or StringIO object
    # Output: A list of hashes that is the result of applying the function
    return self.scrape_function(etree.parse(docket))

  def scrape_directory(self, directory_path):
    successes = 0
    total = 0
    results = []
    for file in glob.iglob(directory_path + "*.xml"):
      total += 1
      try:
        results.append(self.scrape_docket(file))
        successes += 1
      except Exception as e:
        print("Error while parsing {}.".format(file))
        print(e)
    return results, {"total": total, "successes": successes}






# Example functions
def docket_number_and_name(docket_tree):
  #Input: a docket as an ElementTree
  #Output: a list of 1 hash, which contains the name and docket number
  #        of the given docket.
  name = docket_tree.xpath("/docket/header/caption/defendant/text()")[0].strip()
  number = docket_tree.xpath("/docket/header/docket_number/text()")[0].strip()
  return {"defendant_name": name,
          "docket_number": number}
