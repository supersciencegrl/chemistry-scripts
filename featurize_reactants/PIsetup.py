import PyInstaller.__main__
import os

scriptname = f'featurize_reactants'

PyInstaller.__main__.run([
    '--clean',
    '--debug=all',
    '--noconfirm',
    '--name=%s' % scriptname,
    #'--onedir',
    '--onefile',
    '--windowed',
    #'--add-data=parms.dat;.',
    #'--add-binary=%s' % os.path.join('resource', 'path', '*.png'),
    #'--icon=%s' % 'syngenta_logo.ico',
    #'--version-file=version.txt',
    'featurize_reactants.py'
])
