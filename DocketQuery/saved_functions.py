def docket_number_and_name(docket_tree):
  #Input: a docket as an ElementTree
  #Output: a list of 1 hash, which contains the name and docket number
  #        of the given docket.
  name = docket_tree.xpath("/docket/header/caption/defendant/text()")[0].strip()
  number = docket_tree.xpath("/docket/header/docket_number/text()")[0].strip()
  return {"defendant_name": name,
          "docket_number": number}