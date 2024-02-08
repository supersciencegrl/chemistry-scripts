'''
This is heavily derived from Dr Khoi Van (Baylor University)'s script pka_lookup
(https://github.com/khoivan88/pka_lookup) and adapted for H phrases and Syngenta hazard ratings
'''

import re
import requests
import xml.etree.ElementTree as ET

import pubchempy as pcp

def get_cid(cas):
    """
    Retrieve the first PubChem Compound Identifier (cid) for a given chemical.

    Parameters:
    cas (str): The CAS registry number or chemical name.

    Returns:
    int or None: The first CID associated with the CAS registry number or chemical name if available, 
                 otherwise None if no cid can be found, or if the input is None or empty.
    """
    if cas:
        cids = pcp.get_cids(cas, 'name')
        if cids:
            return cids[0]
        
    return None

def get_safety_phrases(cid):
    """
    Fetches the hazard (H-phrases) and precautionary (P-phrases) statements for a substance using its PubChem cid.

    Parameters:
    cid (int): The PubChem Compound Identifier (cid) of the substance.

    Returns:
    tuple: A tuple containing two elements:
        H_phrases (str or None): A string of hazard statements separated by spaces if available, otherwise None.
        P_phrases (str or None): A string of precautionary statements separated by spaces if available, otherwise None.

    Notes:
    The function makes an HTTP GET request to the PubChem PUG-View API, retrieving the GHS Classification section.
    If the request is successful and there is no redirect history, it will parse the XML response to extract
    the H- and P-phrases using the parse_phrases function. If the request fails or the CID is invalid,
    it will return None for both phrases.
    """
    Hphrases_lookup_xml = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{}/XML?heading=GHS+Classification'.format(cid)

    r = requests.get(Hphrases_lookup_xml, headers=headers, timeout=10)
    if r.status_code == 200 and not r.history:
        tree = ET.fromstring(r.text)
        H_phrases, P_phrases = parse_phrases(tree)
        return H_phrases, P_phrases
    else:
        return None, None

def parse_phrases(tree):
    """
    Extracts and formats hazard (H-phrases) and precautionary (P-phrases) statements from an XML tree.

    Parameters:
    tree (xml.etree.ElementTree.Element): The XML tree to parse, typically obtained from a PubChem PUG-View response.

    Returns:
    tuple: A tuple containing two strings:
        H_phrases (str): A space-separated string of unique H-phrases sorted alphabetically.
        P_phrases (str): A space-separated string of unique P-phrases sorted alphabetically.

    Notes:
    The function iterates over each element in the XML tree that contains a phrase, identified by the tag 'String'.
    It uses regular expressions to check if the text content of the node matches the patterns for H-phrases, EUH-phrases,
    and P-phrases, and appends the matches to respective lists. It then removes duplicates by converting the lists to sets,
    sorts them, and joins them into strings.
    """
    H_phrases_list = []
    P_phrases_list = []
    
    for node in tree.iter('{http://pubchem.ncbi.nlm.nih.gov/pug_view}String'):
        phrases_result = node.text or '' # Empty string if no text

        if re.match('^H\d{3}', phrases_result):
            H_phrases_list.append(phrases_result[:4])
        elif re.match('^EUH\d{3}', phrases_result):
            H_phases_list.append(phrases_result[:6])
        elif re.match('^P\d{3}', phrases_result):
            P_phrases_list.append(phrases_result[:4])

    # Tidy up the lists
    H_phrases_list = sorted(set(H_phrases_list))
    P_phrases_list = sorted(set(P_phrases_list))

    H_phrases = (' ').join(H_phrases_list)
    P_phrases = (' ').join(P_phrases_list)

    return H_phrases, P_phrases

def lookup_cpd(cas):
    """
    Looks up and returns hazard (H-) and precautionary (P-) phrases for a substance using its CAS number or
    chemical name.

    Parameters:
    cas (str): The CAS registry number or chemical name of the substance.

    Returns:
    tuple: A tuple containing two elements:
        H_phrases (str or None): The combined hazard phrases for the substance if available; otherwise None.
        P_phrases (str or None): The combined precautionary phrases for the substance if available; otherwise None.

    Notes:
    The function first retrieves the PubChem Compound Identifier (cid) for the given CAS number or chemical name.
    If a cid is found, it then calls another function to retrieve the H- and P-phrases associated with that cid.
    If no cid is found or if the CAS number or chemical name is not found in PubChem, it returns (None, None).
    """
    
    cid = get_cid(cas)
    if cid:
        H_phrases, P_phrases = get_safety_phrases(cid)
        return H_phrases, P_phrases
    else:
        #print(f'Compound {cas} not found')
        return None, None

headers = {
    'user-agent': 'Mozilla/5.0 (X11; CentOS; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
    'Connection': 'close'}

# Ratings and codes not currently used
H = 'High'
M = 'Medium'
L = 'Low'

hazard_code_list = [(200, H),
                  (201, H),
                  (202, H),
                  (203, H),
                  (204, M),
                  (205, M),
                  (206, H),
                  (207, H),
                  (208, H),
                  (220, H),
                  (221, M),
                  (222, H),
                  (223, M),
                  (224, M),
                  (225, M),
                  (226, L),
                  (227, L),
                  (228, L),
                  (229, M),
                  (230, H),
                  (232, H),
                  (240, H),
                  (241, H),
                  (242, M),
                  (250, H),
                  (251, L),
                  (252, L),
                  (260, M),
                  (261, L),
                  (270, M),
                  (271, H),
                  (272, L),
                  (280, M),
                  (281, M),
                  (290, L),
                  (300, H),
                  (301, M),
                  (302, L),
                  (303, L),
                  (304, M),
                  (305, L),
                  (310, H),
                  (311, M),
                  (312, L),
                  (313, L),
                  (314, M),
                  (315, L),
                  (316, L),
                  (317, M),
                  (318, M),
                  (319, L),
                  (320, L),
                  (330, H),
                  (331, M),
                  (332, L),
                  (333, L),
                  (334, H),
                  (335, M),
                  (336, L),
                  (340, H),
                  (341, H),
                  (350, H),
                  (351, H),
                  (360, M),
                  (361, H),
                  (362, H),
                  (370, M),
                  (371, L),
                  (372, H),
                  (373, M),
                  (400, M),
                  (401, L),
                  (402, L),
                  (410, H),
                  (411, M),
                  (412, L),
                  (413, L),
                  (420, L)
                  ]

EUH_code_list = [(1, H),
               (6, H),
               (14, M),
               (19, M),
               (29, M),
               (31, M),
               (32, M),
               (44, H),
               (59, L),
               (66, L),
               (70, M),
               (71, L)
               ]
