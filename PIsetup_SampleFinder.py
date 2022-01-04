import os
import sys

import PyInstaller.__main__

scriptname = f'Sample Finder_PROTOTYPE'

PyInstaller.__main__.run([
    '--clean',
    '--name=%s' % scriptname,
    #'--onedir',
    '--onefile',
    '--windowed',
    #'--add-binary=%s' % os.path.join('resource', 'path', '*.png'),
    #'--icon=%s' % os.path.join('resource', 'path', 'icon.ico'),
    #os.path.join('my_package', '__main__.py'),
    'SampleFinder.py'
])
