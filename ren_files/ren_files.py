__author__ = "Syngenta GBJH"
__copyright__ = "Copyright 2020, 2022"
__version__ = "1.1"
__email__ = "nessa.carson@syngenta.com"
__status__ = "Prototype"

import glob
import os
import re

import PySimpleGUI as sg

sg.theme('Green')

# Log in
user = os.getlogin().lower()
if user == 's1020478':
    username = 'aledgard'
elif user == 's1077007':
    username = 'smutton'
elif user == 's1024501':
    username = 'ncarson'
else:
    sg.popup_get_text(f'What is your NMR username? eg: \'ncarson\'\nEmail {__email__} to have your user account added for faster login.')

# Debug parameters 
#username = 'aledgard'

LCMSfiles = glob.glob('**.raw/')
NMRfiles = glob.glob(f'{username}**/')

errors = []
newnames = []
notmoved = []
for f in NMRfiles:
    #newname = f.replace('_', '-')
    #newname = newname.partition(f'{username}-')[2]
    newname = f
    newnames.append(newname)

newnames.sort()
LCMSfiles.sort()

regexlist = ['\d{6}-\d{3}-\d{1,4}', '\d{6}-\d{3}', '\d{6}-\d{1,3}']
fullregexlist = [prefix + rgx for rgx in regexlist for prefix in ['LIB-', '']]

LCMSnewnames = []
NMRsrenamed = 0
for n, oldLCMSname in enumerate(LCMSfiles):
    for rgx in fullregexlist:
        y = re.search(rgx, oldLCMSname)
        if y:
            break
    if y:
        try:
            if y[0].replace('-', '_') in newnames[n]:
                oldNMRname = NMRfiles[n]
                newNMRname = newnames[n]
                print(f'ren {oldNMRname} {newNMRname}')
                try:
                    if not os.path.isfile(newname):
                        os.rename(oldNMRname, newNMRname)
                        NMRsrenamed += 1
                    else:
                        notmoved.append([oldNMRname, newNMRname])
                except PermissionError:
                    errors.append([oldNMRname, newNMRname])

                newLCMSname = f'{newnames[n][:-1]}.raw'
                print(f'ren {oldLCMSname} {newLCMSname}\n')
                try:
                    if not os.path.isfile(newLCMSname):
                        os.rename(oldLCMSname, newLCMSname)
                    else:
                        notmoved.append([oldLCMSname, newLCMSname])
                except PermissionError:
                    errors.append([oldLCMSname, newLCMSname])
                LCMSnewnames.append(newLCMSname)
        except IndexError:
            if not newnames:
                sg.Popup('No NMR files found. ')
                break

for [f, newname] in errors:
    time.sleep(1)
    try:
        os.rename(f, newname)
    except PermissionError:
        sg.Popup(f'Cannot rename {f} to {newname}: folder is currently in use.', title = 'Permission error')

notmovedstring = ('; ').join([n[0] for n in notmoved])
message = f'{NMRsrenamed} NMR folders and {len(LCMSnewnames)} LC-MS folders renamed. '
if notmovedstring:
    message += f'\n{notmovedstring}'
if newnames and LCMSnewnames:
    title = 'Successful!'
else:
    title = 'Files not moved'
sg.Popup(message, title = title)
