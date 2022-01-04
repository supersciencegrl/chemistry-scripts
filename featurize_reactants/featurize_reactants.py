__author__ = "Syngenta GBJH"
__copyright__ = "Copyright 2022"
__version__ = "1.0.1"
__email__ = "nessa.carson@syngenta.com"
__status__ = "Production"

import os
import time

import pandas as pd
import PySimpleGUI as sg


def import_dataframe(inputfile):
    try:
        df = pd.read_excel(inputfile)
    except ValueError:
        df = pd.read_csv(inputfile)

    return df

def openfile(filename):
    _ = os.system(f'start excel "{filename}"')

def saveParms():
    with open(parmfile, 'wt') as fout:
        fout.write(f'overwrite = {overwrite}\n')
        fout.write(f'output_ext = \'{output_ext}\'\n')
        fout.write(f'inputfile1 = \'{inputfile1}\'\n')
        fout.write(f'inputfile2 = \'{inputfile2}\'\n')

def collapse(layout, key):
    return sg.pin(sg.Column(layout, key=key))

GUI = True
parmfile = 'parms.dat'
sg.theme('Green')
merge = False

# Default filenames
inputfile1 = r"C:\Users\S1024501\GitHub\Syngenta-scripts\featurize_reactants\Examples\1_LDT-000037_Selected_Reactions.xlsx"
inputfile2 = r"C:\Users\S1024501\GitHub\Syngenta-scripts\featurize_reactants\Examples\2__selection_0_LDT-000037_20211014.csv"
outputfile = r"C:\Users\S1024501\GitHub\Syngenta-scripts\featurize_reactants\Examples\test.csv"

# Load previous inputs
if os.path.exists(parmfile):
    with open(parmfile, 'r') as fin:
        for line in fin:
            exec(line)
else:
    overwrite = True
    output_ext = 'csv'

inputfile1_dir = os.path.split(inputfile1)[0] if os.path.split(inputfile1)[0] else os.getcwd()
inputfile2_dir = os.path.split(inputfile2)[0] if os.path.split(inputfile2)[0] else os.getcwd()

if GUI:
    dropdown = [    [sg.Text('Output data type:', key='output_ext_text'),
                     sg.Combo(['csv', 'xlsx'], default_value=output_ext, readonly=True, key='output_ext')]
                    ]
    file_types = (('Excel files', ('.csv', '.xlsx'),),)
    
    layout = [  [sg.Text('Enumerated data file:'),
                     sg.Stretch(), sg.Input(key='df', enable_events = True),
                     sg.FileBrowse(initial_folder=inputfile1_dir, file_types=file_types)],
                [sg.Text('Filtered data file:'),
                     sg.Stretch(), sg.Input(key='filtered', enable_events = True),
                     sg.FileBrowse(initial_folder=inputfile2_dir, file_types=file_types)],
                [sg.Checkbox('Overwrite filtered data file?', default=overwrite, enable_events = True, key='overwrite'),
                     sg.Stretch(),
                     collapse(dropdown, 'output_ext_section')],
                [sg.Button('Merge', bind_return_key=True, disabled=True),
                     sg.Cancel()]
                ]
    window = sg.Window('Data files', layout, keep_on_top=True, return_keyboard_events=True)
    window.Finalize()
    window['df'].update(inputfile1)
    window['filtered'].update(inputfile2)
    if overwrite:
        window['output_ext_section'].update(visible=False)
    if inputfile1 and inputfile2:
        window['Merge'].update(disabled=False)
    time.sleep(0.1)

    while True:
        try:
            event, values = window.Read()
            print(event, values)
            try:
                if values['df'] and values['filtered']:
                    window['Merge'].update(disabled=False)
                else:
                    window['Merge'].update(disabled=True)
            except TypeError: # eg: event is NoneType
                pass                

            if event == 'Merge':
                file_1_exists = os.path.isfile(values['df'])
                file_2_exists = os.path.isfile(values['filtered'])
                if file_1_exists and file_2_exists:
                    merge = True
                    window.close()
                    break
                if not file_1_exists:
                    sg.PopupError(f'File {values["df"]} does not exist.', title='Error')
                if not file_2_exists:
                    sg.PopupError(f'File {values["filtered"]} does not exist', title='Error')
            elif event in [sg.WIN_CLOSED, 'Escape:27', None, 'Cancel']:
                window.close()
                break

            # Toggle visibility of output_ext combobox if overwriting filtered inputfile
            elif event == 'overwrite':
                if values['overwrite']:
                    window['output_ext_section'].update(visible=False)
                else:
                    window['output_ext_section'].update(visible=True)
                
        except KeyboardInterrupt:
            window.close()
            break

overwrite = values['overwrite']
output_ext = values['output_ext']
output_ext_used = output_ext # Allows saving the user-specified output_ext parameter when overwriting a different filetype
inputfile1 = values['df']
inputfile2 = values['filtered']
saveParms()

if merge:
    if overwrite:
        output_ext_used = os.path.splitext(inputfile2)[1][1:]
        outputfile = inputfile2
    else:
        inputfile2_dir = os.path.split(inputfile2)[0] if os.path.split(inputfile2)[0] else os.getcwd()
        outputfile = os.path.join(inputfile2_dir, f'output.{output_ext}')

    df = import_dataframe(inputfile1)
    columns_to_keep = ['Reactant1_SMILES', 'Reactant2_SMILES', 'Product1_SMILES', 'Product2_SMILES']
    df.drop(df.columns.difference(columns_to_keep), axis = 1, inplace = True)

    filtered = import_dataframe(inputfile2)

    output = pd.merge(df, filtered, how='outer', left_on='Product1_SMILES', right_on='SMILES')
    output.reset_index()
    outputwritten = False
    while not outputwritten:
        try:
            if output_ext_used == 'csv':
                output.to_csv(outputfile, index=False)
                outputwritten = True
            else:
                output.to_excel(outputfile, index=False)
                outputwritten = True
        except PermissionError:
            sg.PopupError(f'Please close {outputfile} to continue.', title='error')

    # Final report
    layout = [  [sg.Text('Merge completed successfully!')],
                [sg.Button('Open file', key='openoutput'), sg.Button('Close')]
                ]

    window = sg.Window('Successful!', layout, keep_on_top=True, return_keyboard_events=True)

    while True:
        try:
            event, values = window.Read()
            if event in ['openoutput', chr(13)]:
                openfile(outputfile)
                window.close()
                break
            elif event in ['Close', sg.WIN_CLOSED, 'Escape:27']:
                window.close()
                break
        except KeyboardInterrupt:
            window.close()
            break
