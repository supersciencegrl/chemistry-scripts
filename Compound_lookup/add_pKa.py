'''
This is heavily derived from Dr Khoi Van (Baylor University)'s script pka_lookup
(https://github.com/khoivan88/pka_lookup) and adapted for Pfizer Sandwich HTE reagent library database
'''
import json
from pathlib import Path
from typing import Optional
import urllib
import xml.etree.ElementTree as ET

import pubchempy as pcp
import requests

def get_proxies(proxy_file):
    if proxy_file.is_file():
        with open(proxy_file, 'rt') as fin:
            proxies = json.load(fin)
        proxy_support = urllib.request.ProxyHandler(proxies)
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)
        return proxies

    else:
        return {}

def auto_pka(cas: str, proxies={}, print_output: bool=True) -> Optional[float]:
    '''
    Returns the pKa for a substance given its CAS number or chemical name.

    Args:
        cas (str): The CAS number (or chemical name) of the substance.
        proxies (dict): Dictionary of http and/or https proxies to pass to the requests module. 
        print_output (bool): Flag indicating whether to print the pKa result. Defaults to True.

    Returns:
        Optional[str]: The pKa value as a string, or None if not found in the database.
    '''

    if not proxies:
        proxies = get_proxies(proxy_file)

    cids = pcp.get_cids(cas, 'name')
    try:
        cid = cids[0]
    except (IndexError, TypeError):
        if print_output:
            print(f'Compound {cas} not found')
        return None

    pka_lookup_xml = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/XML?heading=Dissociation+Constants'

    try:
        r = requests.get(pka_lookup_xml, headers=headers, timeout=10, proxies=proxies)
    except requests.exceptions.RequestException as error:
        if print_output:
            print(f'Error retrieving pKa: {str(error)}')
        return None

    if r.status_code == 200:
        tree = ET.fromstring(r.text)
        for node in tree.iter('{http://pubchem.ncbi.nlm.nih.gov/pug_view}String'):
            pKa_result = node.text
        if print_output:
            print(pKa_result)
        return pKa_result

    else:
        if print_output:
            print('pKa not found in database.')
        return None

headers = {
    'user-agent': 'Mozilla/5.0 (X11; CentOS; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
    'Connection': 'close'}
proxy_file = Path('proxies.dat')
proxies_none = {'http': '', 'https': ''} # To force use of no proxy
