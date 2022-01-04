__author__ = "Nessa Carson"
__copyright__ = "Copyright 2020"
__version__ = "1.0"
__email__ = "nessa.carson@syngenta.com"
__status__ = "Prototype"

import glob
import os
import subprocess
import time

import PySimpleGUI as sg
import pywinauto
import winsound

# Class of custom errors
class CustomError(Exception):
    '''Base class for custom errors'''
    pass
class ClientError(CustomError):
    '''Client Spectrus or MestReNova not found'''
    pass

''' Order functions '''
def findspectra(*kw):
    spectralist = []
    for n, d in enumerate(lod):
        spectralist.append(('\t').join([str(n), d['filename'], d['nuc1'], d['solvent'], time.strftime('%a %d %b %Y %H:%M:%S', d['created'])]))
    if kw:
        spectralist = [i for i in spectralist if all(keyword.replace('-', '_') in i for keyword in kw)]
    return spectralist

def silentchron(*kw):
    spectralist = findspectra()
    spectralist.sort(key = lambda x: starttime - time.mktime(time.strptime(x.split('\t')[-1], '%a %d %b %Y %H:%M:%S')))
    if kw:
        spectralist = [i for i in spectralist if all(keyword.replace('-', '_') in i for keyword in kw)]
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
    starttime = time.time()
    my400folders = [i.replace('/', '\\') for i in glob.glob(f'E:/{username}**/**/')]
    my500folders = [i.replace('/', '\\') for i in glob.glob(f'F:/{username}**/**/')]

    lod = []
    addfrominstrument('400', my400folders)
    addfrominstrument('500', my500folders)

    endtime = time.time()
    prtime = endtime - starttime
    print('For a list of commands, type "help()"')
    print(f'\nLoading time: {round(prtime, 5)} s')

def opensp(spectrum):
    global argument
    argument = spectrum
    if isinstance(spectrum, int):
        try:
            spectrum = lod[spectrum]
        except IndexError:
            print(f'Spectrum {spectrum} does not exist. ')
    if isinstance(spectrum, list):
        for sp in spectrum:
            if isinstance(sp, int):
                sp = lod[sp]
            if isinstance(sp, dict):
                spfilename = sp['filename']
                load = os.system(f'""{client}" "{spfilename}"')
            elif '\t' in sp:
                spfilename = sp.partition('\t')[2].partition('\t')[0]
                load = os.system(f'""{client}" "{spfilename}"')
            else:
                load = os.system(f'""{client}" "{sp}"')
    elif isinstance(spectrum, dict):
        spectrumfilename = spectrum['filename']
        load = os.system(f'""{client}" "{spectrumfilename}"')
    elif '\t' in spectrum:
        spectrumfilename = spectrum.partition('\t')[2].partition('\t')[0]
        load = os.system(f'""{client}" "{spectrumfilename}"')
    else:
        load = os.system(f'""{client}" "{spectrum}"')

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

    windowtitle = None
    clientopen = False
    if spectrus:
        windowtitle = 'ACD/Spectrus: Processor Window'
        class_name = 'TSpectrusWindow'
    elif mestrenova:
        windowtitle = 'MestReNova'
        class_name = 'Qt5QWindowIcon'

    if windowtitle:
        while not clientopen: # Check that client is open before sending commands
            try:
                pwa = pywinauto.application.Application()
                w_handle = pywinauto.findwindows.find_windows(title = windowtitle, class_name = class_name)[0]
                clientopen = True
                print('Client window is open. ')
            except IndexError:
                pass

    robotlablist = RobotLabLCMS(*kw)
    Russlablist = RussLabLCMS(*kw)
    spectralist = robotlablist + Russlablist
    spectralist.sort(key = lambda x: x.split('\\')[-1])

    print(f'Opening {len(spectralist)} chromatograms. ')
    passed = 0
    failed = 0
    windowcrashed = 0
    errorhandled = True
    for i, sp in enumerate(spectralist):
        dialogclosed = False
        if mestrenova:
            while not dialogclosed:
                time.sleep(0.2)
                windowhandles = pywinauto.findwindows.find_windows(title = windowtitle, class_name = class_name)
                errorhandles = pywinauto.findwindows.find_windows(title = 'Information', class_name = class_name)
                #print(class_name, windowhandles)
                if windowcrashed == 10:
                    exit()
                elif errorhandles: # If error window is open, wait till it's closed
                    windowcrashed = 0
                    time.sleep(0.2)
                    errorhandled = False
                elif not errorhandled: # If there's an error, try and reload the last one again
                    windowcrashed = 0
                    time.sleep(0.2)
                    windowhandles = pywinauto.findwindows.find_windows(title = windowtitle, class_name = class_name)
                    errorhandles = pywinauto.findwindows.find_windows(title = 'Information', class_name = class_name)
                    if errorhandles:
                        pass
                    if len(windowhandles) == 1: # Check nothing's opened since last check
                        errorhandled = True
                        print(f'Passed error check: {splast}')
                    else:
                        print('Failed error check. ')
                    if errorhandled and splast:
                        load = subprocess.Popen([client, splast])
                elif not windowhandles: # Main window does not appear in list immediately after opening each spectrum
                    windowcrashed += 1
                elif not errorhandles and len(windowhandles) == 1: # Check dialog is closed
                    windowcrashed = 0
                    time.sleep(0.2)
                    windowhandles = pywinauto.findwindows.find_windows(title = windowtitle, class_name = class_name)
                    #print('Check: ', class_name, windowhandles)
                    if len(windowhandles) == 1: # Check nothing's opened since last check
                        dialogclosed = True
                        passed += 1
                    else:
                        failed += 1
        load = subprocess.Popen([client, sp])
        splast = sp

def writetoparms(var_name, var_value):
    if isinstance(var_value, str):
        fout.write(f'{var_name} = \'{var_value}\'\n')
    else:
        fout.write(f'{var_name} = {str(var_value)}\n')

# Debug functions
def switchclient(newclient):
    global spectrus, mestrenova, openpdf, client

    if newclient.lower() == 'spectrus':
        spectrus = True
        mestrenova = False
        openpdf = False
        client = sclient
    elif newclient.lower().endswith('nova'):
        spectrus = False
        mestrenova = True
        openpdf = False
        client = mclient
    elif newclient.endswith('pdf'):
        spectrus = False
        mestrenova = False
        openpdf = True

# Search parameters
c = 'chron'

username = 'ncarson'
parmfile = 'parms.txt'

# Set defaults
expt = '20-'
spectrus = False
mestrenova = True
openpdf = False
sclient = 'C:\\Program Files\\ACD2019LSM\\SPECPROC.exe'
mclient = 'C:\\Program Files\\Mestrelab Research S.L\\MestReNova\\MestReNova.exe'

if os.path.isfile(parmfile):
    with open('parms.txt', 'r') as fin:
        for line in fin:
            exec(line)

# GUI Design
sg.theme('Green')

stdtextcolumn = [   [sg.Text('')],
                    [sg.Text('Experiment(s) to open:', pad = (0,3), tooltip = f'This will open all files containing the above pattern. \neg: entering "20-00001" will open every NMR assigned to that eLN page')]    ]

stdinputcolumn = [  [sg.Text('')],
                    [sg.InputText(focus = True, key = 'expt')]    ]

stdcolumn1 = [  [sg.Column(stdtextcolumn, pad = (0,0)), sg.Column(stdinputcolumn, pad = (0,0))],
                [sg.Text('')],
                ]

stdcolumn2 = [  [sg.Frame(title = 'Client', pad = (0,3), layout = [
                    [sg.Radio('Spectrus', 'client', pad = (0,3), default = spectrus, key = 'spectrus')],
                    [sg.Radio('MestReNova', 'client', pad = (0,3), default = mestrenova, key = 'mestrenova')],
                    [sg.Radio('Open pdf(s)', 'client', pad = (0,3), default = openpdf, key = 'openpdf', disabled = True)]
                    ])]
                ]

stdlayout = [   [sg.In(visible = False)],
                [sg.Column(stdcolumn1), sg.Column(stdcolumn2)]
                ]

advtextcolumn = [   [sg.Text('Spectrus location: ', pad = (0,6))],
                    [sg.Text('MestReNova location: ', pad = (0,6))] ]

advdircolumn = [    [sg.InputText(sclient, key = 'sclient'), sg.FileBrowse(initial_folder = sclient.rsplit('\\', 1)[0], file_types = (('Windows programs', '*.exe'),('All files', '*.*')))],
                    [sg.InputText(mclient, key = 'mclient'), sg.FileBrowse(initial_folder = mclient.rsplit('\\', 1)[0], file_types = (('Windows programs', '*.exe'),('All files', '*.*')))] ]

advlayout = [   [sg.In(visible = False)],
                [sg.Column(advtextcolumn), sg.Column(advdircolumn)]
                ]

layout = [  [sg.TabGroup([[sg.Tab('Standard', stdlayout), sg.Tab('Advanced', advlayout)]])],
            [sg.Button('Submit', bind_return_key = True), sg.Button('Cancel')]
            ]

print(f'Syngenta Sample Finder v.{__version__}')
# Created by Nessa Carson 2020
# Updated 2020-Jul-28 09:23
showGUI = True
cancelled = False
complete = False

# Load GUI
if showGUI:
    window = sg.Window('Import LC-MS data', layout, use_default_focus = False, return_keyboard_events = True)
    window.Finalize()
    window['expt'].update(expt)

    while True:
        event, values = window.read()
        if event in ['\r', 'Submit']:
            if values['spectrus']:
                client = sclient
            elif values['mestrenova']:
                client = mclient
            if values['expt'] not in ['', '20-']:
                break
            else:
                winsound.PlaySound('SystemHand', winsound.SND_ALIAS) # Critical stop sound, don't close window
        if event in (None, 'Cancel', 'Quit'):
            cancelled = True
            values['expt'] = expt # Restore initial
            break

    window.close()

    expt = values['expt'].replace(';', ',').replace(', ', ',')
    spectrus = values['spectrus']
    mestrenova = values['mestrenova']
    openpdf = values['openpdf']
    sclient = values['sclient']
    mclient = values['mclient']

    if spectrus:
        client = sclient
    if mestrenova:
        client = mclient

while not cancelled and not complete:
    exptlist = expt.split(',')

    if not openpdf:
        try:
            if not os.path.isfile(client):
                raise ClientError
        except ClientError:
            sg.Popup('Spectral processing program at {client} not installed. '.format(client = client.replace('\\', '/')), 'Client not found')
            cancelled = True

    #for ex in exptlist:
        # Find the spectra, add to outputspectra
        #if len(outputspectra) > 8:
        #   reallyopenspectra = sg.PopupYesNo(f'Do you really want to open {len(outputspectra)} files?', title = 'Are you sure?')
        #if not reallyopenspectra:
        #   cancelled = True
    complete = True

# Save new parameters
with open(parmfile, 'wt') as fout:
    #writetoparms('expt', expt)
    writetoparms('spectrus', spectrus)
    writetoparms('mestrenova', mestrenova)
    writetoparms('openpdf', openpdf)
    writetoparms('sclient', sclient)
    writetoparms('mclient', mclient)

#reload()
