from rdkit import Chem

def make_enantiomer(mol):
    """
    This function creates the enantiomer of a given molecule, taking only point chirality into account.

    The function takes as input a molecule, 'mol', represented as an RDKit Mol object. 
    It then creates a deep copy of the molecule and inverts all stereogenic centers.

    Parameters:
    mol (rdkit.Chem.rdchem.Mol): RDKit Mol object representing the molecule for which to generate the enantiomer.

    Returns:
    rdkit.Chem.rdchem.Mol: RDKit Mol object representing the enantiomer of the input molecule.
    """
    
    enantiomer = Chem.Mol(mol)
    for atom in enantiomer.GetAtoms():
        atom.InvertChirality()
    
    return enantiomer

def is_chiral(mol):
    """
    Determines whether a given molecule is chiral, taking only point chirality into account. 

    This function first adds Hydrogens to the molecule to fill up the valence of its atoms, 
    then identifies potential stereocenters. If no stereocenters are found, the molecule 
    is not chiral and the function returns False.

    If there are stereocenters, the function creates the enantiomer of the molecule and 
    checks whether the original molecule is equivalent to its enantiomer. If they 
    are not equivalent, the function concludes that the molecule is chiral and returns True.
    If they are, the molecule is not chiral and the function returns False.

    Please note that this function does not handle all cases (for example, it does not consider chirality 
    caused by double bond stereochemistry or atropoisomerism. 

    Parameters:
    mol (rdkit.Chem.rdchem.Mol): RDKit Mol object representing the molecule to check for chirality.

    Returns:
    bool: True if the molecule is chiral, False otherwise.
    """
    
    # Add Hydrogens to fill up the valence of the atoms in the molecule
    mol = Chem.AddHs(mol)

    # Find the potential stereocenters
    Chem.AssignStereochemistry(mol)

    # Get the stereocenters
    chiral_centers = Chem.FindMolChiralCenters(mol, includeUnassigned=True)

    # Check if there are no chiral centers
    if not chiral_centers:
        return False

    # Create the mirror image of the molecule
    enantiomer = make_enantiomer(mol)

    # Check if the original molecule and its mirror image are the same
    return not mol.HasSubstructMatch(enantiomer, useChirality=True)

''' Testing '''
# Initialize the molecule from a SMILES string
mol = Chem.MolFromSmiles('N[C@H]1[C@@H](N)CCCC1')

# Check if the molecule is chiral
print(is_chiral(mol))  # Should print: False
