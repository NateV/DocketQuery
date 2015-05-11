import docket_query as dq
import os


print("Setting up...")
directory_path = "/Users/nathanvogel/Documents/Python/YSRP/DocketParse/testDocs/test_two/complete/*"
records_destination = "./test/test_two/query_records.csv"
if os.path.exists(records_destination):
  os.remove(records_destination)
errors_destination = "./test/test_two/query_errors.csv"
if os.path.exists(errors_destination):
  os.remove(errors_destination)

print("The main event ...")
records_written, errors = dq.query_directory(directory_path, records_destination, errors_destination)
print("Complete.")