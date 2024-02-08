# chemistry-scripts
A disparate collection of scripts I have used for chemistry labwork and data analysis

## Compound lookup
- <em>add_pKa.py</em> &ndash; A small script to return pKa from a CAS number or chemical name input. This is very amenable to diversifying to other compound parameters. May be called by other apps. 
- <em>add_Hphrases.py</em> &ndash; A script to look up H-phrases and P-phrases from a CAS number or chemical name input. 

### Batch chemical parameters
A bespoke script created for [@Imekulo](https://twitter.com/Imekulo) on Twitter, to input a list of chemical names or CAS numbers, and receive a table of molecular weights, molecular formulae, empirical formulae, and CAS numbers in return. 

Please contact me or comment with improvements. Feel free to reuse with credit so others can find the original link with any updates. It's relatively easy to add new columns: I normally use modifications of <em>add_pKa.py</em> to do so. 

## Accessible data

- <em>SampleFinder.py</em> &ndash; A personal, GUI-based script to find my LC-MS sample data or open the pdf output quickly. Now obsolete: eventually became part of a much bigger data access app, used across multiple departments
- <em>my_samples.py</em> &ndash; Older version of SampleFinder, without the GUI
- <em>LC_samples.py</em> &ndash; Quickly returns all LC-MS raw data with filenames containing a user-chosen substring. Now obsolete and part of SampleFinder

## Analytical data scripts

- <em>19F_shifts.txt</em> &ndash; A list of literature <super>19</super>F NMR chemical shift data
- <em>audit_metadata_spare_fields.py</em> &ndash; Quick check to audit the use of metadata in samples collected in an instrument folder
- <em>merge_pdfs.py</em> &ndash; Finds relevant pdf analytical data for an experiment and merges to a single pdf for easy viewing and uploading
- <em>mine_params.py</em> &ndash; Returns acquisition and processing parameters for a folder of Bruker NMR data to analyse spectrometer use

## Featurize_reactants

A GUI-based program to merge .csv or .xlsx data for a specific workflow involving matching SMILES strings of products and starting materials for external lookup of the starting materials. 

## is_it_chiral
Checks - with point chirality only - whether a given molecule is chiral or not. 

## Library_metadata

A GUI-based program to prepopulate an LC-MS sample list with compound metadata for fast analysis. 

## Merge_pdfs

A bespoke Python CLI program to make NMR and LC-MS data easily human-searchable, and merge pdf files, in either "Library" or "Optimization" mode. 

## OCR_pdf_tables

A quick script to OCR tables from pdf files and save them to pandas dataframes, using the tabula-py library. 

## Random alarm

Rings an alarm randomly with in the next user-defined time period in minutes. I use this to deal with my email inbox while doing non-focus tasks... 

## ren_files

A GUI-based program to to rename NMR and LC-MS data files for a specific workflow. 

## sdfile

A GUI-based program to add metadata to an .sdf file (list of molecules) to facilitate structural analysis. 
