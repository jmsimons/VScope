#!/usr/bin/python3.5

import sys, os, psutil, signal, time
import multiprocessing as mp
from webapp import db, config
from webapp.collect_data import list_file
from webapp.models import Project

mp.set_start_method('fork')


### Functions for performing project actions ###

def setup_project(project): ### Runs project setup ###
    from main import su_project
    project_dict = project.get_dict()
    if not project_dict['thds']:
        project_dict['thds'] = 'Auto'
    project_dict['path'] = '{}/Projects/{}'.format(config['BASE_PATH'], project_dict['name'])
    # su_project.main(project_dict)
    process = mp.Process(target = su_project.main, args = (project_dict, ))
    process.start()

def run_project(project_path): ### Runs batch in a subprocess ###
    from main import run_batch
    process = mp.Process(target = run_batch.main, args = (project_path, ))
    process.start()

def stop_project(project_dict): ### Interupts project process ###
    log_lines = list_file('{}/{}.log'.format(project_dict['path'], project_dict['id']))
    for line in log_lines[::-1]:
        if 'Batch' in line and 'PID' in line:
            last_PID = line.split(':')[-1].strip()
            try:
                proc = psutil.Process(int(last_PID))
            except:
                print('Cannot find process')
                return False
            proc.send_signal(signal.SIGINT)
            # proc.kill()
            return True
    return False

def run_subtraction(project_path, quality): ### Runs subtractions on project .vcf files in a subprocess ###
    from main import subtract
    process = mp.Process(target = subtract.main, args = (project_path, quality))
    process.start()

def run_annotation(project_path): ### Runs annotation on project .vcf files in a subprocess ###
    from main import snpEff_utils
    process = mp.Process(target = snpEff_utils.main, args = (project_path, ))
    process.start()

def run_analysis(project_path): ### Runs quality impact analysis on project .vcf files in a subprocess ###
    from main import qual_impact
    process = mp.Process(target = qual_impact.main, args = (project_path, ))
    process.start()

def archive_project(project_path): ### Runs the archive tool on project files ###
    from main.archive_remove import archive_project
    archive_project(project_path)
    project_id = project_path.split('/')[-1]
    project = Project.query.filter_by(name = project_id).first()
    project.active = False
    db.session.commit()

def remove_project(project_path, complete = True): ### Runs the removal tool on project and removes entry in assets/active_projects.txt ###
    from main.archive_remove import remove_project
    remove_project(project_path)
    if complete:
        project_id = project_path.split('/')[-1]
        project = Project.query.filter_by(name = project_id).first()
        db.session.delete(project)
        db.session.commit()
