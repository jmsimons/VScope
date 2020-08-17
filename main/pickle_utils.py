#!/usr/bin/python3.5

import pickle

def dump(object, filepath):
    with open(filepath, 'wb') as wb:
        pickle.dump(object, wb)

def load(filepath):
    with open(filepath, 'rb') as rb:
        return pickle.load(rb)

project_dict = {'name':None, # Project Name
                'orgn':None, # Project Organism
                'path':None, # Path to main project directory (default: .../vscope/projects)
                'temp':None, # (Optional) Path to temporary project dir, points to a faster storage medium
                'repo':None, # Reads data repository (Local, fastq-dump, wget, upload)
                'acc':None, # Accession/Samples list contains sample ID's for each sample in project
                'ref':None, # Reference genome file (.fa, .fasta, .fas)
                'ver':None, # Reference genome version # (ie 7.0.1)
                'gff':None, # Reference genome exons file (.gff, .gff3)
                'gtf':None, # Reference genome exons file (.gtf)
                'grp':None, # Group size for final analysis
                'sub':True, # Subtraction boolean (Perform Subtraction?)
                'anno':True, # Post-subtraction SnpEff annotation
                'proc':1, # Number of concurrent samples
                'dlay':0, # Number of minutes to delay between sample launches
                'thds':1, # Number of additional threads to use for assembly and other tasks
                }

# dump(project_dict, '../project_dict.pkl')