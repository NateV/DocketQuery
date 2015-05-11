import docket_query
import sys
import getopt
import logging
import yaml

# For example:
# python -m query_script -s /Volumes/DOCKETS/CP_51_CR_all_2011_parsed/complete/*.xml -d /Volumes/DOCKETS/CP_51_CR_all_2011_parsed/query_results.csv -e /Volumes/DOCKETS/CP_51_CR_all_2011_parsed/query_errors.csv -l /Volumes/DOCKETS/CP_51_CR_all_2011_parsed/query_log.md

def get_parameters():
  """
  Returns the parameters needed for run():
  1) Path of the source directory
  2) Path of the destination directory
  3) Path for the logging file for the results
  4) Path for a separate csv for just errors
  """
  usage_string = "user$ query_script.py -p <parameters_file.yaml>"
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hp:")
  except:
    print("Options error.")
    print(usage_string)
    sys.exit(2)
  for opt, arg in opts:
    if opt=="-h":
      print("""
      Usage:
      {}

      Options:
      -h: This message.
      -p: Path to a yaml file with the following structure:
          parsed_xml: <a path to directory of parsed xml files>
          destination_csv: <a path of new csv file to create with query results>
          logfile: <a path for the log to go>
          errorfile: <a path for the errorfile to go>
      """.format(usage_string))
      sys.exit(2)
    if opt=="-p":
      parameters_file = arg
  sliced_opts = {opt[0] for opt in opts}
  if "-p" not in sliced_opts:
    print("Must provide parameters file.")
    sys.exit(2)

  params = yaml.load(open(parameters_file))
  print("Params: {}, {}, {}, {}".format(params["parsed_xml"], params["destination_csv"], params["logfile"], params["errorfile"]))

  return params["parsed_xml"], params["destination_csv"], params["logfile"], params["errorfile"]

def run(parsed_xml_dir, destination_csv, logfile, errorfile):
  print("Starting...")
  logging.basicConfig(filename=logfile, level=logging.DEBUG)
  docket_query.query_directory(parsed_xml_dir, destination_csv, errorfile)


if __name__ == "__main__":
  parsed_xml_dir, destination_csv, logfile, errorfile = get_parameters()
  run(parsed_xml_dir, destination_csv, logfile, errorfile)