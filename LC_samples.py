__author__ = "Nessa Carson"
__copyright__ = "Copyright 2020"
__version__ = "1.0"
__email__ = "nessa.carson@syngenta.com"
__status__ = "Prototype"

'''Script to find relevant .raw subfolders quickly'''

import glob
import os
import time

def viewfolders(lod):
    for f in lod:
        folderloc = (os.sep).join((f['folder'], f['subfolder']))
        created = time.localtime(os.path.getctime(folderloc))
        print(f'{f["subfolder"]}\t\t{time.strftime("%a %d %b %Y %H:%M:%S", created)}\t{f["location"]}')
    print('\n')

def run():
    lod = []
    
    while True:
        kw = input('Keyword: ')
        for loc in locations:
            os.chdir(loc['path'])
            folderlist = glob.glob(f'**{kw}**.raw')
            newlist = [{'location': loc['name'], 'folder': loc['path'], 'subfolder': f} for f in folderlist]
            lod += newlist

        if not lod:
            print('No data found. \n')
        elif len(lod) > 200:
            viewinput = input(f'Length of folderlist is {len(lod)}. \
                  Do you want to view {len(lod)} folder names? (Y/N) ')
            print('\n')
            if viewinput.lower() in 'yestrue1':
                viewfolders(lod)
        else:
            viewfolders(lod)
        lod = []

RussHClass = r'\\GBJHXNS11AB6\chem.PRO\Data'
RLHClass = r'\\gbjhxnsmasx1026\masslynx\ChemRobot.PRO\Data'
NCfolder = r'\\gbjhxnsmasx1026\masslynx\ChemRobot.PRO\Data\NC'

locations = [{'name': 'Russell HClass', 'path': RussHClass},
              {'name': 'RLHClass', 'path': RLHClass},
              {'name': f'RLHClass{os.sep}NC', 'path': NCfolder}]

run()
