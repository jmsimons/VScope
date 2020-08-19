#!/usr/bin/python3

import time, os, sys
import multiprocessing as mp
from main.run_sample import main

class batch: ### Data and methods for managing deployment of individual samples from project sample list ###

    def __init__(self, project_dict):
        self.proj_dict = project_dict
        self.project_id = project_dict['name']
        self.path = project_dict['path']
        self.alt_path = project_dict['temp']
        self.process = int(project_dict['proc'])
        self.stop = None
        self.delay = 0
        self.last_deploy = 0
        self.next_sample = 0
        # os.chdir(self.path) # change directory to project dir #
        print('Working in...', os.getcwd())
        self.proj_files = {'accession' : 'accession.txt',
                           'processing': 'processing.txt',
                           'complete'  : 'complete.txt'}
        acc_list, self.proc_list, self.comp_list = self.load_lists()
        self.acc_list = [i for i in acc_list if i not in self.comp_list and i not in self.proc_list]
        self.log('Batch initialized with PID: {}'.format(os.getpid()))
        if self.proc_list:
            for sample in self.proc_list:
                self.deploy_next(sample = sample)
        self.delay = int(project_dict['dlay']) * 60 # convert delay mintutes into seconds #
        # mp.set_start_method('fork')

    def log(self, string): ### Append 'string' to project log file ###
        log_file = '{}/{}.log'.format(self.path, self.project_id)
        format = '%Y/%m/%d %H:%M:%S'
        stamp = time.strftime(format, time.localtime(time.time()))
        output = '>{} {}\n'.format(stamp, string)
        with open(log_file, 'a+') as f:
            f.write(output)

    def load_lists(self): ### Creates lists from accession, processing, and complete txt files ###
        lists = {k: [] for k in self.proj_files}
        for key, value in self.proj_files.items():
            with open('{}/assets/{}'.format(self.path, value)) as f:
                if 'id' in key:
                    proj_id = f.readline()
                    proj_id = proj_id.strip()
                else:
                    for line in f:
                        line = line.strip()
                        lists[key].append(line)
        return lists['accession'], lists['processing'], lists['complete']

    def dump_proc(self):
        with open('{}/assets/{}'.format(self.path, self.proj_files['processing']), 'w') as f: # Replaces processing file with new list #
            for sample in self.proc_list:
                f.write(sample + '\n')

    def dump_comp(self, newly_complete): ### Dumps an updated set of processing and complete lists to project directory ###
        with open('{}/assets/{}'.format(self.path, self.proj_files['complete']), 'a+') as f: # Appends newly complete sample id's to complete list file #
            for sample in newly_complete:
                f.write(sample+'\n')
        
    def get_next_sample(self):
        if self.next_sample == len(self.acc_list):
            return None
        next_sample = self.acc_list[self.next_sample]
        self.next_sample += 1
        return next_sample

    def check_processing(self): ### Checks through each processing sample's comlete.log file to determine its status ###
        newly_complete = []     ### Returns list of completed sample, also removes from self.proc_list ###
        for sample in self.proc_list:
            with open('{}/{}/{}.log'.format(self.path, sample, sample)) as f:
                lines = [i for i in f if i != '']
            if 'workflow complete' in lines[-1]:
                newly_complete.append(sample)
                self.proc_list.remove(sample)
                self.comp_list.append(sample)
        if len(self.proc_list) < self.process: # New samples deployed here #
            sample = self.deploy_next()
        if newly_complete:
            self.dump_comp(newly_complete)
        return newly_complete

    def deploy(self, sample, project_dict): ## This is happening in a new process, this is where the new sample is started, calls sys.exit for subprocess when main finishes ##
        print('{} Started with PID: {}'.format(sample, os.getpid()))
        self.log('{} Started with PID: {}'.format(sample, os.getpid()))
        main(sample, project_dict)
        sys.exit()

    def deploy_next(self, sample = None): ### Deploys a new sample in it's own process, adds sample to self.proc_list ###        
        time_delta = int(time.time()) - self.last_deploy
        if time_delta >= self.delay:
            if not sample: sample = self.get_next_sample()
            process = mp.Process(target = self.deploy, args = (sample, self.proj_dict)) # Starts the new process #
            process.daemon = False
            process.start()
            self.last_deploy = int(time.time())
            if sample not in self.proc_list:
                self.proc_list.append(sample)
                print(self.proc_list)
                self.dump_proc()
            return sample
        else:
            return None