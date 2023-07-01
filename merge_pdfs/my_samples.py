__author__ = "Nessa Carson"
__copyright__ = "Copyright 2020, 2023"
__version__ = "1.3"
__status__ = "Prototype"

import glob
import os
import time

print(f'NMR Sample List v.{__version__}')

''' Order functions '''
def findSpectra(*kw):
    """
    Generates a list of spectra based on a list of dictionaries (lod), where each dictionary corresponds to a spectrum.

    Args:
        *kw: A variable-length argument list of keywords to filter the list of spectra. Keywords are matched against 
             a string representation of each spectrum's metadata, including filename, nucleus, solvent, and created date.

    Returns:
        A list of strings representing each spectrum that matches the given keywords. Each string contains the index
        of the spectrum in the original list, its filename, nucleus, solvent, and file creation datetime.

    Example:
        lod = [{'filename': 'spectrum1.pdf', 'nuc1': '1H', 'solvent': 'DMSO', 'created': time.struct_time(tm_year=2022, tm_mon=3, tm_mday=13, tm_hour=16, tm_min=45, tm_sec=2)},               {'filename': 'spectrum2.pdf', 'nuc1': '13C', 'solvent': 'CDCl3', 
                'created': time.struct_time(tm_year=2022, tm_mon=3, tm_mday=14, tm_hour=10, tm_min=20, tm_sec=30)
                }]
        For example, the function `findspectra('spectrum', 'DMSO', '13C')` will return:
                ['0\tspectrum1.pdf\t1H\tDMSO\tSat 12 Mar 2022 16:45:02',
                 '1\tspectrum2.pdf\t13C\tCDCl3\tSun 13 Mar 2022 10:20:30'
                ]
    """

    spectraList = []
    for n, d in enumerate(lod):
        myString = ('\t').join([str(n), 
                                d['filename'],
                                d['nuc1'],
                                d['solvent'],
                                time.strftime('%a %d %b %Y %H:%M:%S',
                                d['created'])
                                ]
                            )
        spectraList.append(myString)
    if kw:
        spectraList = [i for i in spectraList if all(str(keyword).replace('-', '_') in i for keyword in kw)]

    return spectraList

def silentChron(*kw):
    """
    Finds spectra and sorts them by acquisition time, from oldest to newest. Where keyword arguments are provided, 
    only return spectra that contain all of the keywords in their metadata.

    Args:
        *kw: Variable-length list of strings representing keywords to filter the spectra by.

    Returns:
        A list of strings, each string containing the metadata of a spectrum in the library. The metadata are tab-separated 
        and have the following format:
        "<spectrum index>\t<filename>\t<nucleus 1>\t<solvent>\t<creation datetime>". 
        The list is sorted by increasing creation date and time.
    """

    spectraList = findSpectra()
    # Sort the spectra by acquisition time
    spectraList.sort(key = lambda x: starttime - time.mktime(time.strptime(x.split('\t')[-1], '%a %d %b %Y %H:%M:%S')))
    # Return a subset containing the keywords only
    if kw:
        spectraList = [i for i in spectraList if all(str(keyword).replace('-', '_') in i for keyword in kw)]
    return spectraList

''' User functions '''
def listSpectra(*kw):
    """
    Prints a list of spectra in the library that match the specified keywords.

    If two or more positional arguments are passed, and the second one is 'chron', the list is sorted chronologically.
    Otherwise, the list is sorted by the order of spectra in the list.

    Parameters:
    *kw:
        Variable number of string arguments that serve as keywords for filtering the list of spectra.
    
    Returns:
    None
    """

    if len(kw) >= 2:
        if kw[1] == 'chron': # Chronological mode
            spectraList = silentChron(*kw)
        else:
            spectraList = findSpectra(*kw)
    else:
        spectraList = findSpectra(*kw)
    for sp in spectraList:
        print(sp)

def listChron(*kw):
    """
    Prints a list of spectra sorted by acquisition time in chronological order, and filtered by keyword(s) if provided.

    Parameters:
    *kw (tuple): 
        optional. A tuple of keyword(s) to filter the list of spectra. If provided, only the spectra containing all the 
        specified keywords will be displayed.
    
    Output:
        Prints the sorted list of spectra to the console.
    """

    spectraList = silentChron(*kw)
    for sp in spectraList:
        print(sp)

def reload():
    """
    Reloads the NMR data and updates the `lod` global variable.

    This function looks for network drives containing NMR data for the user (`drive400` and `drive500`)
    and adds any data found to the `lod` list by calling the `addfrominstrument()` function. The time it
    takes to load the data is printed at the end. If either the `drive400` or `drive500` drives cannot be found,
    a warning message is displayed. 

    Global variables:
        lod (list): a list of NMR spectra dictionaries
        starttime (float): the start time of the data reload process

    Example usage:
        >>> reload()
        For a list of commands, type "help()"
        
        Loading time: 10.2374 s
    """

    global lod, starttime
    print('For a list of commands, type "help()"')
    starttime = time.time()
    drive400 = Path(r'//GBJHNMR03/data/opacc/')
    drive500 = Path(r'//GBJHNMR09/data/opacc/')

    # Reloads data from 400-MHz NMR
    if os.path.isdir(f'{drive400}/'):
        my400folders = [i.replace('/', '\\') for i in glob.glob(f'{drive400}/{username}**/**/')]
    else:
        print(f'WARNING: cannot connect to 400-MHz NMR drive {drive400}/')
        my400folders = []

    # Reloads data from 500-MHz NMR
    if os.path.isdir(f'{drive500}/'):
        my500folders = [i.replace('/', '\\') for i in glob.glob(f'{drive500}/{username}**/**/')]
    else:
        print(f'WARNING: cannot connect to 500-MHz NMR drive {drive500}/')
        my500folders = []

    # Creates a new list of dictionaries from both NMR instruments
    lod = []
    addfrominstrument('400', my400folders)
    addfrominstrument('500', my500folders)

    endtime = time.time()
    prtime = endtime - starttime
    print(f'\nLoading time: {round(prtime, 4)} s')

def expandList(thisInput):
    """
    Fully expands a list of arguments that can contain integers and delimiter-separated ranges.

    Args:
        thisInput: A string or iterable to be expanded.

    Returns:
        A list of integers obtained by expanding the input string or iterable.

    Examples:
        >>> expandList('1; 2-5; 7')
        [1, 2, 3, 4, 5, 7]
        >>> expandList('3:6')
        [3, 4, 5, 6]
        >>> expandList([1, 2, '3-5'])
        [1, 2, 3, 4, 5]
    """

    # Initialize output variable
    outputList = []

    if isinstance(thisInput, str):
        # Standardize string input
        tempArgument = thisInput.replace(':', '-').replace(' ', '').replace(';', ',')
        if ',' in tempArgument:
            tempArgument = tempArgument.split(',')
        else:
            tempArgument = [tempArgument]
        for n, arg in enumerate(tempArgument):
            if '\t' in thisInput:
                outputList.append(thisInput.split('\t')[1])
            elif '-' in arg:
                first, sep, third = arg.partition('-')
                for x in range(int(first), int(third) + 1):
                    outputList.append(x)
            else:
                outputList.append(int(arg))

    elif isinstance(thisInput, int) or isinstance(thisInput, dict):
        outputList = [thisInput]
    else:
        outputList = list(thisInput)

    # Create a temporary list of strings to iterate recursively over until function is complete
    tempList = [s for s in outputList if isinstance(s, str)]
    for item in tempList:
        if '-' in item.replace(':', '-'):
            newlist = expandList(item)
            index = outputList.index(item)
            outputList = outputList[:index] + newlist + outputList[index+1:]
            if item in outputList:
                outputList.remove(item)

    return outputList

def openSpectrum(spectrum):
    """
    Opens the specified NMR spectrum. Accepts a spectrum ID as a filepath a string, or an integer. If an integer is given, the ID
    will be used to find the corresponding spectrum in the current directory listing. A filepath will be the 
    full path to the spectrum file. A string can contain multiple spectra, and will be expanded to refer to them all 
    according to the `expandList` function. Once the file(s) have been located, they will be loaded into the NMR client software 
    using the command specified in the `client` global variable.

    Args:
    - spectrum: Path, str or int. 
        The ID of the spectrum to open, the full path to the file, or a string which may contain 
        multiple spectral identifiers.

    Returns: None
    """

    global argument

    tempArgument = expandList(spectrum)
    while any([isinstance(subarg, list) for subarg in tempArgument]):
        newList = []
        for subarg in tempArgument:
            newList += expandList(subarg)
        tempArgument = newList
    argument = []

    for arg in tempArgument:
        # Resolve spectral identifiers
        if not isinstance(arg, dict):
            try:
                arg = int(arg) # Make it an integer if possible
            except (ValueError, TypeError):
                print(f'Argument {arg} not an integer')
                pass

        if isinstance(arg, int): # Deal with integers
            try:
                arg = lod[arg]
            except IndexError:
                print(f'Spectrum {spectrum} does not exist. ')

        # Open spectra
        if isinstance(arg, dict):
            spectrumfilename = arg['filename']
            argument.append(spectrumfilename)
            if Debug:
                print(f'""{client}" "{spectrumfilename}"')
            else:
                load = os.system(f'""{client}" "{spectrumfilename}"')
        elif f':{os.sep}' in arg:
            argument.append(arg)
            if Debug:
                print(f'""{client}" "{arg}"')
            else:
                load = os.system(f'""{client}" "{arg}"')
        else:
            argument.append(arg)
            if Debug:
                print(f'""{client}" "{arg}"')
            else:
                load = os.system(f'""{client}" "{arg}"')

def nextSpectrum():
    """
    Opens the next spectrum in the list. If the current argument is an integer, it increments it by 1 and loads the 
    corresponding spectrum. If the current argument is a list, it finds the next integer in the list, increments it by 1, 
    and loads the corresponding spectrum. If no next spectrum is found, it prints an appropriate message.
    """

    global argument
    if isinstance(argument, int):
        argument += 1

        try:
            spdict = lod[argument]
        except IndexError:
            print('Last item reached in list. ')
            pass
        spectrumFilename = spdict['filename']
        # I have no idea why this function has to miss the last '"' in the argument. But if you don't, it doesn't work in one of the clients
        load = os.system(f'""{client}" "{spectrumFilename}"')
        
    elif isinstance(argument, list):
        try:
            argument = sorted(argument)[-1] + 1
            try:
                spdict = lod[argument]
            except IndexError:
                print('Last item reached in list. ')
                pass
            spectrumFilename = spdict['filename']
            # I have no idea why this function has to miss the last '"' in the argument. But if you don't, it doesn't work in one of the clients
            load = os.system(f'""{client}" "{spectrumFilename}"')
        except TypeError:
            print('Could not find next for argument {argument}. ')
            pass

def help():
    """
    Prints a list of possible user commands. 
    """

    print('Possible commands: ')
    commandslist = ['', 'reload()', 'listSpectra(*kw)', 'listChron(*kw)', 'openSpectrum(kw)', 'nextSpectrum()']
    print(('\n\t').join(commandslist))

'''Build functions'''
def findParameter(line: str):
    """
    Takes in a string and returns a substring between the first occurrences of < and > characters in the line, representing 
    the parameter therein.

    Parameters:
        line (str) : A string containing the parameter to be extracted.
    
    Returns:
        str: A substring representing the parameter value in the input string.
    """
    result = line.partition('<')[2].partition('>')[0]

    return result

def makedict(spect: list):
    """
    Creates a dictionary from a list of strings (spect), with keys corresponding to specific
    metadata from the input list.

    Args:
        spect: A list of strings.

    Returns:
        A dictionary with the following keys:
            'solvent': The solvent used in the NMR experiment, as a string.
            'nuc2': The name of the secondary nucleus (for 2D experiments), as a string.
            'nuc1': The name of the primary nucleus, as a string.
            'expt': The type of NMR experiment, as a string.
    """

    newdict = {}
    for line in spect:
        if line.startswith('##$SOLVENT'): #Line 240; put expected last line first to shorten the loop
            newdict['solvent'] = findParameter(line).title()
            break
        elif line.startswith('##$NUC2'): # Line 149
            newdict['nuc2'] = findParameter(line)
            if newdict['nuc2'] == 'off':
                newdict['nuc2'] = ''
        elif line.startswith('##$NUC1'): # Line 148
            newdict['nuc1'] = findParameter(line)
        elif line.startswith('##$EXP'): # Line 58
            newdict['expt'] = findParameter(line)
    return newdict

def addfrominstrument(instrument, folderList: list):
    """
    Takes an instrument name and a list of folders as input. Adds the NMR spectra metadata to a list of dictionaries. 

    Args:
        instrument: a string representing the name of the instrument
        folderList: a list of strings representing the paths to folders containing NMR spectra files
    
    Returns:
        None
    
    Outputs:
        Iterates over each folder in the folderlist. For each folder, it creates a new dictionary with the following keys:
            'nuc1': primary nucleus
            'nuc2': secondary nucleus (2D experiments only)
            'age': the difference between the current time and the time the folder was created
            'created': the time the folder was created
            'filename': path to the folder
            'instrument': the name of the instrument

        Then, it reads the acqu file in the folder, and uses the makedict function to extract additional metadata from the 
        file. If any metadata are found, they are added to the dictionary.
        Finally, the dictionary is appended to the lod list.
    """

    for folder in folderList:
        mydict = {'nuc1': '', 
                  'nuc2': ''
                 }
        mydict['age'] = starttime - os.path.getctime(folder)
        mydict['created'] = time.localtime(os.path.getctime(folder))
        mydict['filename'] = Path(folder)
        mydict['instrument'] = instrument

        with open(os.path.join(folder, 'acqu'), 'rt') as fin:
            newdict = makedict(fin)
        if newdict:
            mydict.update(newdict)
        lod.append(mydict)

# LC-MS functions
def LCMS1(*kw):
    """
    Returns a list of LC-MS chromatogram file paths.

    Args:
        *kw: Variable length arguments. Accepts keywords to filter the LC-MS spectra.
    
    Returns:
        A list of file paths of LC-MS spectra.
    """

    path = Path(r'//gbjhxnsmasx1026/masslynx/chemrobot.pro/Data')
    folderList = [i.replace('/', '\\') for i in glob.glob(f'{path}/**.raw')]
    folderList2 = [i.replace('/', '\\') for i in glob.glob(f'{path}/NC/*/**.raw')]
    allFoldersList = folderList + folderList2

    if kw:
        spectraList = [i for i in allFoldersList if all(keyword in i for keyword in kw)]
    else:
        spectraList = allFoldersList[:]

    return spectraList

def LCMS2(*kw):
    """
    Returns a list of LC-MS chromatogram file paths.

    Args:
        *kw: Variable length arguments. Accepts keywords to filter the LC-MS spectra.
    
    Returns:
        A list of file paths of LC-MS spectra.
    """

    path = Path(r'//GBJHXNS11AB6/chem.PRO/Data')
    folderList = [i.replace('/', '\\') for i in glob.glob(f'{path}/**.raw')]

    if kw:
        spectraList = [i for i in folderList if all(keyword in i for keyword in kw)]
    else:
        spectraList = folderList[:]

    return spectraList

def openLCMS(*kw):
    """
    The function openLCMS() opens LCMS chromatogram files using the Spectrus or MestReNova software. For Spectrus, it first preloads 
    the client program, which is needed for Spectrus to run efficiently. Then it gets a list of LCMS spectra files using the LCMS1 
    and LCMS2 functions with any optional keywords passed as arguments. The LCMS spectra files are sorted by their filenames and 
    opened in the client. 

    Args:
        *kw (optional): Variable-length argument list of keywords to filter LCMS spectra files by.

    Returns:
        None. 
        
    Outputs:
        Opens the LCMS spectra files in the specified client.
    """
    if client == spectrus:
        load = subprocess.Popen(client) # Preload client - needed for Spectrus, which is incredibly slow...

    LCMS1_files = LCMS1(*kw)
    LCMS2_files = LCMS2(*kw)
    spectraList = LCMS1_files + LCMS2_files
    spectraList.sort(key = lambda x: x.split('\\')[-1])

    print(spectraList)
    for i, sp in enumerate(spectraList):
        load = subprocess.Popen([client, sp])

# Search parameters
Debug = False
c = 'chron'
username = 'ncarson'

spectrus = Path(r'C:/Program Files/ACD2019LSM/SPECPROC.exe')
mestrenova = Path(r"C:/Program Files (x86)/Mestrelab Research S.L/MestReNova Lite CDE/MestReNova.exe")
client = mestrenova

reload()