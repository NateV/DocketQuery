
To use:

`
from DocketQuery.docket_query import AskADocket, dicts2csv
from DocketQuery.saved_functions import docket_number_and_name


#pick some directory with parsed dockets
dir = "tests/texts/"

#Initialize an AskADocket object with the mapping function
#you'd like to use.
scraper = AskADocket(docket_number_and_name)

#Scrape the directory you want to scrape with the
#function you've chosen, and retrieve the errors,
#results, and success/total counts.
errors, results, counts = scraper.scrape_directory(dir)

`

