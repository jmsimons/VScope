#!/usr/bin/python3

import sys
from time import sleep
import main.load_project as load_project
from main.batch import batch
from main.run_sample import run

def main(project_path): ### Initializes batch instance and makes periodic calls to batch.check_processing ###
    project_dict = load_project.dict(project_path)
    project = batch(project_dict)
    while True:
        try: sleep(1)
        except:
            print('Halt: Batch Interupted')
            sys.exit()
        newly_complete = project.check_processing()
        if newly_complete:
            print('Newly Complete:')
            for complete in newly_complete:
                print(complete)
            if not project.proc_list and not project.process: # Exits upon completion of all samples #
                print('Batch finished, fairwell!')
                sys.exit()

if __name__ == '__main__':
    project_path = sys.argv[1].rstrip('/')
    main(project_path)