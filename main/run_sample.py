#!/usr/bin/python3

from main import get_config
from main.sample import sample
from main.sample_methods import *

# # #  Creates sample instance calls workflow methods successively until completion  # # #

def run(sample_id, project_dict, config): ### Sample instance and method calls, returns ending file list ###
    sample_obj = sample(sample_id, project_dict, config)
    if project_dict['repo'][0] == '/':
        copy_reads(sample_obj)
    elif project_dict['repo'] == 'NCBI-SRA':
        fastq_dump(sample_obj)
    trim(sample_obj)
    #mem_se(sample)
    mem_pe(sample_obj)
    bam(sample_obj)
    fstat(sample_obj)
    n_sort(sample_obj)
    fxmate(sample_obj)
    p_sort(sample_obj)
    mrkdup(sample_obj)
    index(sample_obj)
    stats(sample_obj)
    # gencov(sample_obj)
    # depth(sample)
    mpileup(sample_obj)
    #snpeff(sample)
    file_list = sample_obj.exit() # ending file list passed back by sample #
    return file_list

def main(sample_id, project_dict): ### Calls and waits for run(), then prints ending file list ###
    # print(project_dict)
    config = get_config.all()
    print(config)
    print(project_dict)
    file_list = run(sample_id, project_dict, config)
    print('Ending file list:')
    for file in file_list:
        print(file)
	
if __name__ == '__main__': ### Only call main when launched in it's own process ###
    while 1: # TODO: accept sample id and project_dict path as command-line args #
        sample = input('Enter sample ID: ') # Accepts terminal input of sample number when run stand-alone #
        if 'SRR' in sample: # Requires 'SRR...' type sample id #
            main(sample)
            break
        elif sample == '': print('Please enter a sample ID')
        else: print('Wrong sample id format!')