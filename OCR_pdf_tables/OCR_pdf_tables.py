import csv
import os
from pathlib import Path

import tabula

# Import filepaths and create filepath dictionary
filepaths = {}
with open('filepaths.csv', 'r', encoding='utf-8-sig') as fin:
    reader = csv.reader(fin)
    for line in reader:
        k,v = line
        filepaths[k] = v

inputfile = Path(filepaths['inputfile'])
# Store outputs in the my_cwd folder
os.chdir(Path(filepaths["my_cwd"]))

dfs = tabula.read_pdf(inputfile, pages='all', multiple_tables=True)

df = dfs[5] # First dataframe
## df.to_csv('table5.csv')
