from DocketQuery import docket_query
from DocketQuery.saved_functions import conviction_information
import os

src = "/Volumes/DOCKETS/CP_51_CR_all_2011_parsed/complete/"
dest = "/Volumes/DOCKETS/CP_51_CR_all_2011_parsed/query_results/"
# src = "tests/texts/"
# dest = "tests/output/query_results/"

scraper = docket_query.AskADocket(conviction_information)
errors, results, counts = scraper.scrape_directory(src)
if not os.path.exists(dest):
  os.mkdir(dest)
docket_query.dicts2csv(errors, results,
                       open(dest + "errors.csv", 'w'),
                       open(dest + "results.csv", 'w'),
                       counts = counts,
                       counts_file = open(dest + "counts.csv", 'w'))
