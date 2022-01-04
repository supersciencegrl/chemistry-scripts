__author__ = "Nessa Carson"
__copyright__ = "Copyright 2020"
__version__ = "1.0"
__email__ = "nessa.carson@syngenta.com"
__status__ = "Prototype"

import glob
import os
import re
from shutil import copy2
import time

from PyPDF2 import PdfFileMerger

import my_samples

# Class of custom errors
class CustomError(Exception):
    '''Base class for custom errors'''
    pass
class InputListStringError(CustomError):
    '''Raised when inputliststring contains incorrect values'''
    pass

# Merge pdfs
def mergepdfs(outputfile, inputfilelist):
    merger = PdfFileMerger()
    #file_handles = []

    for path in inputfilelist:
        merger.append(path)

    with open(outputfile, 'wb') as fout:
        merger.write(fout)

def openoutput():
    if library:
        os.system(f'start "" "{outputfolder}"')
    else:
        filepath = os.path.join(outputfolder, outputfile)
        if os.path.isfile(filepath):
            os.system(f'start "" "{filepath}"')
        else:
            print(f'{outputfile} not found.')

def run():
    global library, outputfile, outputfolder, inputstring
    
    inputstring = None
    substringlist = None
    library = False
    while not inputstring or not substringlist:
        inputstring = input('\nInput substring (case-sensitive): ')
        if inputstring:
            substringlist = my_samples.silentchron(inputstring)
            numberlist = [int(ss.partition('\t')[0]) for ss in substringlist]
            my_samples.listchron(inputstring)
        if inputstring and not substringlist:
            print('No spectra found.\n')

    if substringlist:
        inputlist = []
        while not inputlist:
            inputliststring = input('\nList all spectra numbers to extract pdfs: ').lower().replace(' ', '').replace(';', ',').replace(':', '-')
            initinputlist = inputliststring.split(',')
            for x in initinputlist:
                try:
                    if '-' in x:
                        first, sep, third = x.partition('-')
                        try:
                            first = int(first)
                            third = int(third)
                        except ValueError:
                            print(f'{first}-{third} is not a valid integer range.')
                            raise InputListStringError
                        if third <= first:
                            print(f'{first}-{third} is not a valid range.')
                            raise InputListStringError
                        else:
                            for y in range(first, third + 1):
                                if y in numberlist:
                                    inputlist.append(y)
                                else:
                                    print(f'{y} not in spectra list for {inputstring} substring.')
                                    raise InputListStringError
                    else:
                        if x == 'all':
                            inputlist.append(x)
                        else:
                            try:
                                if int(x) in numberlist:
                                    inputlist.append(int(x))
                                else:
                                    print(f'{x} not in spectra list for {inputstring} substring.')
                                    raise InputListStringError
                            except ValueError:
                                if x:
                                    print(f'{x} is not a valid integer.')
                                raise InputListStringError
                except InputListStringError:
                    inputlist = []

        # Using tidied inputlist
        if 'all' in inputlist:
            folderlist = [x.split('\t')[1] for x in substringlist][::-1]
        else:
            folderlist = []
            for x in inputlist:
                folderlist.append(my_samples.lod[x]['filename'])

    print(folderlist)
    if all(['lib' in f.lower() for f in folderlist]):
        library = True
        print('Entering library mode.')

    print(f'{len(folderlist)} folders selected.')

    if library:
        outputfolder = None
        while not outputfolder:
            outputfolder = input('\nFull path of output folder: ')
            if 'def' in outputfolder:
                outputfolder = 'C:\\Users\\S1024501\\OneDrive - Syngenta\\Documents\\Chemistry'
            if outputfolder and not os.path.isdir(outputfolder):
                print(f'{outputfolder} not found')
                outputfolder = None
    else:
        outputfolder = 'C:\\Users\\S1024501\\OneDrive - Syngenta\\Documents\\Chemistry'

    pdflist = []
    for folder in folderlist:
        pdflist = pdflist + glob.glob(f'{folder}pdata\\**\\*.pdf')

    # Avoid overwriting output
    if re.match('^\d{5}$', inputstring):
        outputstring = f'20-{inputstring}'
    else:
        outputstring = inputstring

    if not os.path.isfile(f'{outputstring}.pdf'):
        outputfile = f'{outputstring}-NMR.pdf'
    else:
        outputfile = None
        iterator = 1
        while not outputfile:
            iterator += 1
            if not os.path.isfile(f'{outputstring}-NMR-{iterator}.pdf'):
                outputfile = f'{outputstring}-NMR-{iterator}.pdf'

    confirmation = None
    if library and pdflist:
        while not confirmation:
            confirmation = input(f'Copy {len(pdflist)} pdfs? (Y/N) ')
        if confirmation.lower() in 'yestrue1':
            for pdf in pdflist:
                copy2(pdf, os.path.join(outputfolder, pdf.split(os.sep)[-1]))
        else:
            confirmation = False
    else:
        if len(pdflist) > 1:
            while not confirmation:
                confirmation = input(f'Merge {len(pdflist)} pdfs? (Y/N) ')
            if confirmation.lower() in 'yestrue1':
                mergepdfs(os.path.join(outputfolder, outputfile), pdflist)
            else:
                confirmation = False
        elif len(pdflist) == 1:
            confirmation = True
            print(f'Copying {pdflist[0]} to {outputfile}.')
            mergepdfs(os.path.join(outputfolder, outputfile), pdflist)
        else:
            print('No pdfs found.')

    if confirmation:
        if not library:
            openfiles = input(f'Open {outputfile}? (Y/N) ')
            if openfiles.lower() in 'yestrue1':
                openoutput()
        os.system(f'start "" "{outputfolder}"') # First argument interpreted as window title

run()
