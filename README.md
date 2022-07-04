# chemistry-scripts
A disparate collection of scripts I have used for chemistry labwork and data analysis

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

## Library_metadata

A GUI-based program to prepopulate an LC-MS sample list with compound metadata for fast analysis. 

## ren_files

A GUI-based program to to rename NMR and LC-MS data files for a specific workflow. 

## sdfile

A GUI-based program to add metadata to an .sdf file (list of molecules) to facilitate structural analysis. 

## Identifiers

API-based interconversion between multiple chemical identifiers. Now obsolete and part of a larger program. 
