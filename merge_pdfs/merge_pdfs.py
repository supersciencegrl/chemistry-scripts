__author__ = "Nessa Carson"
__copyright__ = "Copyright 2020, 2023"
__version__ = "1.0"
__status__ = "Prototype"

import datetime
import glob
import os
import re
from pathlib import Path
import shutil

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
def mergepdfs(outputFile: Path, inputFileList: list):
    """
    Merge a set of PDF files into a single PDF file.

    Args:
    - outputFile (Path): The path to the output file.
    - inputFileList (list): A list of file paths of the input PDF files.

    Returns:
    - None

    Raises:
    - TypeError: If any of the input arguments is of incorrect type.
    - ValueError: If any of the input arguments is of incorrect value.
    - IOError: If the output file cannot be opened for writing.

    Example:
    mergepdfs('merged.pdf', ['file1.pdf', 'file2.pdf', 'file3.pdf'])
    """

    merger = PdfFileMerger()

    for path in inputFileList:
        merger.append(path)

    with open(outputFile, 'wb') as fout:
        merger.write(fout)

def openOutput():
    """
    If the 'library' flag is True, the output folder is opened in Windows Explorer.
    If the 'library' flag is False, the output file is opened if it exists. Otherwise, an error message is printed.

    """

    if library:
        # Opens the folder containing a list of files
        os.system(f'start "" "{outputFolder}"')
    else:
        # Opens the merged pdf file
        filepath = Path(os.path.join(outputFolder, outputFile))
        if os.path.isfile(filepath):
            os.system(f'start "" "{filepath}"')
        else:
            print(f'{outputFile} not found.')

def openResults(library: bool, outputFolder: Path, outputFile: Path):
    """
    Opens the output folder.
    Optimization mode only: asks the user whether to open the merged output pdf in the default viewer.

    Args:
        library (bool): A flag indicating whether the input files were created as part of a library.
        outputFolder (Path): The path of the folder containing the pdf files.
        outputFile (Path): The name of the merged output pdf file.

    Returns:
        None

    Side Effects:
        - Prompts the user to open the merged output PDF file in the default viewer, if `library` is False.
        - Opens a new file explorer window showing `outputFolder`, regardless of `library` flag.

    Raises:
        N/A
    """

    if not library:
        # Optimization mode: asks the user whether to open the merged output pdf in the default viewer
        openfiles = input(f'Open {outputFile}? (Y/N) ')
        if openfiles.lower() in 'yestrue1':
            openOutput()

    # Both library and optimization mode: opens the output folder in Windows Explorer
    os.system(f'start "" "{outputFolder}"') # First argument interpreted as window title

def run():
    """
    Takes input from the user, extracts specific pdf files from the library of spectra, and copies or merges them based on the 
    user's input. Then opens the output file in the default viewer.

    Optimization mode: pdfs are merged to a single file
    Library mode: pdfs are copied to a particular local folder rather than merged to a single file

    Returns:
    - None

    """

    global library, outputFile, outputFolder, inputString
    
    # Initialize variables
    inputString = None
    substringList = None

    library = False
    outputFolder = None
    outputFile = None

    # Prompt user to enter substring
    while not inputString or not substringList:
        inputString = input('\nInput substring (case-sensitive): ')
        if inputString:
            # Open the files and create a list of the files that were opened
            substringList = my_samples.silentChron(inputString)
            numberList = [int(ss.partition('\t')[0]) for ss in substringList]
            my_samples.listChron(inputString)
        if inputString and not substringList:
            # Return an error
            print('No spectra found.\n')

    if substringList:
        # Extract pdfs from library based on input list
        inputList = []
        while not inputList:
            inputListString = input('\nList all spectra numbers to extract pdfs: ')
            inputListString = inputListString.lower().replace(' ', '').replace(';', ',').replace(':', '-')
            initInputList = inputListString.split(',')

            # Find each relevant substring
            for x in initInputList:
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
                                if y in numberList:
                                    inputList.append(y)
                                else:
                                    print(f'{y} not in spectra list for {inputString} substring.')
                                    raise InputListStringError
                    else:
                        if x == 'all':
                            inputList.append(x)
                        else:
                            try:
                                if int(x) in numberList:
                                    inputList.append(int(x))
                                else:
                                    print(f'{x} not in spectra list for {inputString} substring.')
                                    raise InputListStringError
                            except ValueError:
                                if x:
                                    print(f'{x} is not a valid integer.')
                                raise InputListStringError
                except InputListStringError:
                    inputList = []

        # Using tidied inputlist
        if 'all' in inputList:
            # Creates a tidied folder list in reverse order for printing
            folderList = [x.split('\t')[1] for x in substringList][::-1]
        else:
            # Creates a tidied list of filenames for printing
            folderList = []
            for x in inputList:
                folderList.append(my_samples.lod[x]['filename'])

    print(folderList)
    if all(['lib' in f.lower() for f in folderList]):
        # Turn on library mode
        library = True
        print('Entering library mode.')

    print(f'{len(folderList)} folders selected.')

    if library:
        # Use library mode (copies rather than merges pdfs) and asks user to provide output folder location
        while not outputFolder:
            outputFolder = input('\nFull path of output folder: ')
            if 'def' in outputFolder:
                # Push to default folder
                outputFolder = Path(r'C:/Users/Nessa/Documents/Chemistry')
            if outputFolder and not os.path.isdir(outputFolder):
                # Ask for input again if invalid
                print(f'{outputFolder} not found')
                outputFolder = None
    else:
        outputFolder = Path(r'C:/Users/Nessa/Documents/Chemistry') # default

    # Create a list of every NMR pdf within the base folder
    pdfList = []
    for folder in folderList:
        pdfList = pdfList + glob.glob(f'{folder}pdata\\**\\*.pdf')

    # Append an iterator to avoid overwriting output
    if re.match('^\d{5}$', inputString):
        # Make this look like the standard expected experiment IDs, format GYY-XXXXX, where YY is this year
        thisYear = datetime.date.today().strftime('%y')
        outputstring = f'G{thisYear}-{inputString}'
    else:
        outputstring = inputString

    # Determine the output file name
    if not os.path.isfile(f'{outputstring}.pdf'):
        outputFile = f'{outputstring}-NMR.pdf'
    else:
        iterator = 1
        while not outputFile:
            iterator += 1
            if not os.path.isfile(f'{outputstring}-NMR-{iterator}.pdf'):
                outputFile = f'{outputstring}-NMR-{iterator}.pdf'

    confirmation = None
    if library and pdfList:
        # Copies pdfs to the desired output folder, after asking the user whether they're sure
        while not confirmation:
            confirmation = input(f'Copy {len(pdfList)} pdfs? (Y/N) ')
        if confirmation.lower() in 'yestrue1':
            for pdf in pdfList:
                shutil.copy2(pdf, os.path.join(outputFolder, pdf.split(os.sep)[-1]))
        else:
            confirmation = False
    else:
        # Merges pdfs to a single file, after asking the user whether they're sure
        if len(pdfList) > 1:
            while not confirmation:
                confirmation = input(f'Merge {len(pdfList)} pdfs? (Y/N) ')
            if confirmation.lower() in 'yestrue1':
                mergepdfs(Path(os.path.join(outputFolder, outputFile)), pdfList)
            else:
                confirmation = False
        # If only 1 pdf is present, copy this file rather than editing it
        elif len(pdfList) == 1:
            confirmation = True
            print(f'Copying {pdfList[0]} to {outputFile}.')
            mergepdfs(Path(os.path.join(outputFolder, outputFile)), pdfList)
        # If no pdfs in the folder
        else:
            print('No pdfs found.')
        
        # Opens the resulting merged file (optimization mode) or output folder (library mode)
        if confirmation:
            openResults(library, outputFolder, outputFile)

if __name__ == '__main__':
    run()
