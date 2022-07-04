import re
import requests
import urllib.parse

import pubchempy as pcp
import pyperclip
import PySimpleGUI as sg

def nametoCSN(name):
    ''' Converts name or CAS to CSN '''
    url = 'http://aci.rt.intra:9944/airim/lookup/airp1/csn/synonym/'

    r = requests.get(f'{url}{name}', headers = headers, timeout = 10)
    if r.status_code == 200:
        CSN = r.text
        return CSN
    else:
        print(f'No CSN found: {name}')
        return None

def nametoCAS(name):
    compound = pcp.get_compounds(name, 'name')
    if compound:
        casfound = False
        for s in compound[0].synonyms:
            casfound = iscas(s)
            if casfound:
                return s
        return None # if no casfound in synonyms

    else:
        return None

def CSNtoMany(csn):
    url = 'http://aci.rt.intra:9944/airim/propcalc/airp1/csn/all/'

    r = requests.get(f'{url}{csn}', headers = headers, timeout = 10)
    if r.status_code == 200:
        try:
            string = r.text.partition('{')[2].partition('}')[0]
            resultlist = string.split(',"')
            resultdict = {}
            for result in [r.replace('"', '') for r in resultlist]:
                key, sep, value = result.partition(':')
                resultdict[key] = value
            return resultdict
            
        except IndexError:
            return None
    else:
        print(f'Not found in AIRIM: {csn}')
        return None

def CSNtoImage(csn):
    url = 'http://aci.rt.intra:9944/airim/lookup/airp1/png/csn/'
    # svgurl = 'http://aci.rt.intra:9944/airim/lookup/airp1/svg/csn/'

    r = requests.get(f'{url}{csn}', headers = headers, timeout = 10)
    if r.status_code == 200:
        image = r.text
        return image
    else:
        print(f'No image found: {csn}')
        return None

def SMILEStoMany(smiles): # Also takes chime input
    url = 'http://aci-dev2.rt.intra:9944/airim/propcalc/all/'

    encoded = urllib.parse.quote(smiles)
    r = requests.get(f'{url}{encoded}', headers = headers, timeout = 10)
    if r.status_code == 200:
        try:
            string = r.text.partition('{')[2].partition('}')[0]
            resultlist = string.split(',"')
            resultdict = {}
            for result in [r.replace('"', '') for r in resultlist]:
                key, sep, value = result.partition(':')
                resultdict[key] = value
            return resultdict
            
        except IndexError:
            return None
    else:
        print(f'Not found in AIRIM: {smiles}')
        return None

def iscas(name): #Function to determine whether a string is a CAS number
    x = re.match('\d{2,7}-\d\d-\d', name)
    try:
        z = x[0] # Throws TypeError if no regex match
        digitsbackwards = z.replace('-', '')[::-1]
        checksum = 0
        for i, digit in enumerate(digitsbackwards):
            checksum += (i * int(digit))
        if checksum%10 == int(z[-1]):
            return True
        else:
            print('Invalid CAS: {name}')
            return False

    except TypeError:
        return False

headers = {
        'user-agent': 'Mozilla/5.0 (X11; CentOS; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
        'Connection': 'close'}

testCSN = 'CSAA185474'
testCAS = '6192-52-5'
