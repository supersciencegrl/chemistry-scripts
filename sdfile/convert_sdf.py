__author__ = "Syngenta GBJH"
__copyright__ = "Copyright 2022"
__version__ = "1.0"
__email__ = "nessa.carson@syngenta.com"
__status__ = "Production"

import os
import re
import time

import PySimpleGUI as sg

# Class of custom errors
class CustomError(Exception):
    ''' Base class for custom errors '''
    pass
class SDFError(CustomError):
    ''' Raised when inputfile type is not .sdf '''
    pass
class ThisFileNotFoundError(CustomError):
    ''' Raised when inputfile is not found '''
    pass

def requestRAParms(default_library, default_username):
    layout = [  [sg.Text('Library:'),
                 sg.Stretch(),
                 sg.Input(default_text=default_library, disabled=True)],
                [sg.Text('Username:'),
                 sg.Stretch(),
                 sg.Input(default_text=default_username, key='username')],
                [sg.Text('Remote Analyzer starting index:',
                         tooltip='Must be a six-digit number, eg: \'398999\''),
                 sg.Stretch(),
                 sg.Input(key='RA_index')],
                [sg.Button('OK', bind_return_key=True), sg.Button('Cancel')]
                ]
    
    window = sg.Window('Parameters', layout, keep_on_top=True, return_keyboard_events=True, use_default_focus=False)
    window.Finalize()
    window.TKroot.focus_force()
    window['RA_index'].SetFocus()
    time.sleep(0.1)

    while True:
        try:
            event, values = window.Read()
            if event in ['OK']:
                if not values['username']:
                    window['username'].SetFocus()
                    sg.PopupError('Username cannot be blank.', title='Error', keep_on_top=True)
                elif not re.match('\d{6}$', values['RA_index']):
                    window['RA_index'].SetFocus()
                    message = 'Remote Analyzer starting index must be a six-digit number eg: \'398999\'.'
                    _ = sg.PopupError(message, title='Error', keep_on_top=True)
                else:
                    window.close()
                    break
            elif event in ['Cancel', sg.WIN_CLOSED]:
                window.close()
                return None, None, event
                    
        except KeyboardInterrupt:
            window.close()
            return None, None, event

    username = values['username']
    RA_index = values['RA_index']

    return username, RA_index, event

def parseMolecule(molfile, RA_index):
    molfile_list = molfile.split('\n')

    try:
        structure_index = molfile_list.index('M  END')
    except ValueError: # end of sdf; empty molecule
        return None, None
    structure = molfile_list[: structure_index+1]
    
    library_index = molfile_list.index('> <Notebook>')
    label = molfile_list[library_index+1]
    label_RA = label.replace('-', '_')
    filename = f'{username}_{label_RA}__{RA_index}'

    new_structure = [filename] + structure[1:]
    new_structure_string = ('\n').join(new_structure)

    return new_structure_string, filename

def saveParms():
    with open(parmfile, 'wt') as fout:
        fout.write(f'initial_folder = r"{mydir}"\n')
        fout.write('\n')
        fout.write(f'userdb = {userdb}')

sg.theme('Green')
parmfile = 'parms.dat'

# Load previous inputs
if os.path.exists(parmfile):
    with open(parmfile, 'r') as fin:
        for line in fin:
            exec(line)
else:
    initial_folder = os.getcwd()

##inputfile = r"C:\Users\S1024501\GitHub\Syngenta-scripts\ren_files\sdfile\LIB-000370-1.sdf" # Default
##RA_index = 398990

inputfile = None
default_path = ''
while not inputfile:
    inputfile = sg.popup_get_file('SDFile:',
                                  title = 'Input file',
                                  file_types = (('SDFiles', ('.sdf'),),),
                                  initial_folder = initial_folder,
                                  keep_on_top = True,
                                  history_setting_filename = True,
                                  default_path = default_path)
    try:
        if not os.path.splitext(inputfile)[1] == '.sdf':
            sg.PopupError('Please input a valid SDFile.', title='Error', keep_on_top=True)
            raise SDFError
        elif not os.path.isfile(inputfile):
            sg.PopupError(f'File {inputfile} does not exist.', title='Error', keep_on_top=True)
            raise ThisFileNotFoundError
        
    except (SDFError, ThisFileNotFoundError):
        thisdir = os.path.dirname(inputfile)
        initial_folder = thisdir if os.path.isdir(thisdir) else ''
        default_path = inputfile
        inputfile = None
    except TypeError: # NoneType
        inputfile = None
        break

if inputfile:
    inputfile = inputfile.replace('"', '')
    mydir, inputfile_name = os.path.split(inputfile)

    with open(inputfile) as fin:
        sdf = fin.read()

    molfiles = sdf.split('$$$$\n')
    default_library = inputfile_name[:10] if inputfile_name.startswith('LIB') else ''
    
    user = molfiles[0].partition('<Experimentalist>\n')[2].partition('\n\n')[0]
    if user in userdb: # From parmfile
        username = userdb[user]
    else:
        username = ''
        sg.Popup(f'Email {__email__} to have this experimentalist\'s user account added for faster login.')
    default_username = username
        
    username, RA_index, event = requestRAParms(default_library, default_username)
    if username and RA_index:
        RA_index_iter = int(RA_index)

        output = []
        for molfile in molfiles:
            structure, filename = parseMolecule(molfile, RA_index_iter)
            if structure:
                output.append([structure, filename])
            RA_index_iter += 1

        saveParms()
        outputfile_name = os.path.splitext(inputfile_name)[0] + '-edited_for_ASV.sdf'
        outputfile = os.path.join(mydir, outputfile_name)
        with open(outputfile, 'wt') as fout:
            for molecule in output:
                structure, filename = molecule
                fout.write(structure + '\n')
                fout.write('> <File>\n')
                fout.write(filename + '\n\n')
                fout.write('$$$$\n')
        completed = True

    else:
        sg.Popup('Operation cancelled.')
        completed = False

    if completed:
        if event in [chr(13), '\r']:
            time.sleep(0.3)
        # Final report
        layout = [  [sg.Text('Completed successfully!')],
                    [sg.Button('Open containing folder', key='openfolder'), sg.Button('Close')]
                    ]

        window = sg.Window('Success!', layout, keep_on_top=True, return_keyboard_events=True)

        while True:
            try:
                event, values = window.Read()
                if event in ['openfolder', chr(13)]:
                    os.startfile(mydir)
                    window.close()
                    break
                elif event in ['Close', sg.WIN_CLOSED, 'Escape:27']:
                    window.close()
                    break
            except KeyboardInterrupt:
                window.close()
                break
