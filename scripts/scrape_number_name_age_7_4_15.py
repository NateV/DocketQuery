from DocketQuery import docket_query
from DocketQuery.saved_functions import docket_num_name_age
import os

src = "/Volumes/DOCKETS/CP_51_CR_all_2011_parsed/complete/"
dest = "/Users/nathanvogel/Documents/Python/YSRP/statistics/num_name_age_query/"


scraper = docket_query.AskADocket(docket_num_name_age)
errors, results, counts = scraper.scrape_directory(src)
if not os.path.exists(dest):
  os.mkdir(dest)
docket_query.dicts2csv(errors, results,
                       open(dest + "errors.csv", 'w'),
                       open(dest + "results.csv", 'w'),
                       counts = counts,
                       counts_file = open(dest + "counts.csv", 'w'))
with open(dest + "readme.md", "w") as f:
  f.write("""
  This script applies the docket_num_name_age function to all the
  parsed dockets to recover only each docket's number, name, birth date, and
  initiated date.
""")
f.close()