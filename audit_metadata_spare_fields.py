import csv
import glob

import pandas as pd

''' Note: this script can fail when run on a slow network drive.
    Copy all csv's and this script to a local folder in this case. '''


filenames = glob.glob('**.csv')

myfiles = []
for f in filenames:
    df = pd.read_csv(f)
    if 'SPARE_1' in df.columns:
        mydict = {'filename': f}
        df.replace('', float('NaN'), inplace=True)
        df.dropna(how='all', axis=1, inplace=True)
        for n, row in enumerate(df['SPARE_1']):
            spare2value = df['SPARE_2'][n]
            if 'SET!' in row and not 'SET!:' in row:
                mydict['set'] = True
            elif 'SET!' in spare2value and not 'SET!:' in spare2value:
                mydict['set'] = True
            else:
                mydict['set'] = False
            if 'SS!' in row and not 'SS!:' in row:
                mydict['subset'] = True
            elif 'SS!' in spare2value and not 'SS!:' in spare2values:
                mydict['subset'] = True
            else:
                mydict['subset'] = False
        mydict['lastCol'] = df.columns[-1]
        myfiles.append(mydict)
    
