__author__ = "Nessa Carson"
__copyright__ = "Copyright 2020"
__version__ = "1.2" # Now opens lists of integers; nextsp() and help() functions added
__email__ = "nessa.carson@syngenta.com"
__status__ = "Prototype"

import glob
import os
import time

print(f'NMR Sample List v.{__version__}')
# Created by Nessa Carson 2020
# Updated 2020-Jul-07 10:44

''' Order functions '''
def findspectra(*kw):
    spectralist = []
    for n, d in enumerate(lod):
        spectralist.append(('\t').join([str(n), d['filename'], d['nuc1'], d['solvent'], time.strftime('%a %d %b %Y %H:%M:%S', d['created'])]))
    if kw:
        spectralist = [i for i in spectralist if all(str(keyword).replace('-', '_') in i for keyword in kw)]
    return spectralist

def silentchron(*kw):
    spectralist = findspectra()
    spectralist.sort(key = lambda x: starttime - time.mktime(time.strptime(x.split('\t')[-1], '%a %d %b %Y %H:%M:%S')))
    if kw:
        spectralist = [i for i in spectralist if all(str(keyword).replace('-', '_') in i for keyword in kw)]
    return spectralist

''' User functions '''
def listspectra(*kw):
    if len(kw) >= 2:
        if kw[1] == 'chron':
            spectralist = silentchron(*kw)
        else:
            spectralist = findspectra(*kw)
    else:
        spectralist = findspectra(*kw)
    for sp in spectralist:
        print(sp)

def listchron(*kw):
    spectralist = silentchron(*kw)
    for sp in spectralist:
        print(sp)

def reload():
    global lod, starttime
    print('For a list of commands, type "help()"')
    starttime = time.time()
    drive400 = '//GBJHNMR03/data/opacc/'
    drive500 = '//GBJHNMR09/data/opacc/'

    if os.path.isdir(f'{drive400}/'):
        my400folders = [i.replace('/', '\\') for i in glob.glob(f'{drive400}/{username}**/**/')]
    else:
        print(f'WARNING: cannot connect to 400 MHz NMR drive {drive400}/')
        my400folders = []

    if os.path.isdir(f'{drive500}/'):
        my500folders = [i.replace('/', '\\') for i in glob.glob(f'{drive500}/{username}**/**/')]
    else:
        print(f'WARNING: cannot connect to 500 MHz NMR drive {drive500}/')
        my500folders = []

    lod = []
    addfrominstrument('400', my400folders)
    addfrominstrument('500', my500folders)

    endtime = time.time()
    prtime = endtime - starttime
    print(f'\nLoading time: {round(prtime, 4)} s')

def expandlist(stra):
    outputlist = []

    if isinstance(stra, str):
        tempargument = stra.replace(':', '-').replace(' ', '').replace(';', ',')
        if ',' in tempargument:
            tempargument = tempargument.split(',')
        else:
            tempargument = [tempargument]
        for n, arg in enumerate(tempargument):
            if '\t' in stra:
                outputlist.append(stra.split('\t')[1])
            elif '-' in arg:
                first, sep, third = arg.partition('-')
                for x in range(int(first), int(third) + 1):
                    outputlist.append(x)
            else:
                outputlist.append(int(arg))
    elif isinstance(stra, int) or isinstance(stra, dict):
        outputlist = [stra]
    else:
        outputlist = list(stra)

    templist = [s for s in outputlist if isinstance(s, str)] # Avoid TypeError
    for item in templist:
        if '-' in item.replace(':', '-'):
            newlist = expandlist(item)
            index = outputlist.index(item)
            outputlist = outputlist[:index] + newlist + outputlist[index+1:]
            if item in outputlist:
                outputlist.remove(item)

    return outputlist

def opensp(spectrum):
    global argument

    tempargument = expandlist(spectrum)
    while any([isinstance(subarg, list) for subarg in tempargument]):
        newlist = []
        for subarg in tempargument:
            newlist += expandlist(subarg)
        tempargument = newlist
    argument = []

    for arg in tempargument:
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

def nextsp():
    global argument
    if isinstance(argument, int):
        argument += 1

        try:
            spdict = lod[argument]
        except IndexError:
            print('Last item reached in list. ')
            pass
        spectrumfilename = spdict['filename']
        load = os.system(f'""{client}" "{spectrumfilename}"')
    elif isinstance(argument, list):
        try:
            argument = sorted(argument)[-1] + 1
            try:
                spdict = lod[argument]
            except IndexError:
                print('Last item reached in list. ')
                pass
            spectrumfilename = spdict['filename']
            load = os.system(f'""{client}" "{spectrumfilename}"')
        except TypeError:
            print('Could not find next for argument {argument}. ')
            pass

def help():
    print('Possible commands: ')
    commandslist = ['', 'reload()', 'listspectra(*kw)', 'listchron(*kw)', 'opensp(kw)', 'nextsp()']
    print(('\n\t').join(commandslist))

'''Build functions'''
def makedict(spect):
    newdict = {}
    for line in spect:
        if line.startswith('##$SOLVENT'): #Line 240; put first to shorten loop
            newdict['solvent'] = line.partition('<')[2].partition('>')[0].title()
            break
        elif line.startswith('##$NUC2'): # Line 149
            newdict['nuc2'] = line.partition('<')[2].partition('>')[0]
            if newdict['nuc2'] == 'off':
                newdict['nuc2'] = ''
        elif line.startswith('##$NUC1'): # Line 148
            newdict['nuc1'] = line.partition('<')[2].partition('>')[0]
        elif line.startswith('##$EXP'): # Line 58
            newdict['expt'] = line.partition('<')[2].partition('>')[0]
    return newdict

def addfrominstrument(instrument, folderlist):
    for f in folderlist:
        mydict = {'nuc1': '', 'nuc2': ''}
        mydict['age'] = starttime - os.path.getctime(f)
        mydict['created'] = time.localtime(os.path.getctime(f))
        mydict['filename'] = f
        mydict['instrument'] = instrument
        with open(os.path.join(f, 'acqu'), 'rt') as fin:
            newdict = makedict(fin)
        if newdict:
            mydict.update(newdict)
        lod.append(mydict)

# LC-MS functions
def RobotLabLCMS(*kw):
    path = '//gbjhxnsmasx1026/masslynx/chemrobot.pro/Data'
    folderlist = [i.replace('/', '\\') for i in glob.glob(f'{path}/**.raw')]
    folderlist2 = [i.replace('/', '\\') for i in glob.glob(f'{path}/NC/*/**.raw')]
    folderslist = folderlist + folderlist2

    if kw:
        spectralist = [i for i in folderlist if all(keyword in i for keyword in kw)]
    else:
        spectralist = folderlist[:]

    return spectralist

def RussLabLCMS(*kw):
    path = '//GBJHXNS11AB6/chem.PRO/Data'
    folderlist = [i.replace('/', '\\') for i in glob.glob(f'{path}/**.raw')]

    if kw:
        spectralist = [i for i in folderlist if all(keyword in i for keyword in kw)]
    else:
        spectralist = folderlist[:]

    return spectralist

def openLCMS(*kw):
    load = subprocess.Popen(client) # Preload client

    robotlablist = RobotLabLCMS(*kw)
    Russlablist = RussLabLCMS(*kw)
    spectralist = robotlablist + Russlablist
    spectralist.sort(key = lambda x: x.split('\\')[-1])

    print(spectralist)
    for i, sp in enumerate(spectralist):
        load = subprocess.Popen([client, sp])

# Search parameters
Debug = False
c = 'chron'

username = 'ncarson'
client = 'C:\\Program Files\\ACD2019LSM\\SPECPROC.exe'
#client = r"C:\Program Files (x86)\Mestrelab Research S.L\MestReNova Lite CDE\MestReNova.exe"

reload()
# time.strftime('%a %d %b %Y %H:%M:%S', time.localtime(os.path.getctime(f)))
