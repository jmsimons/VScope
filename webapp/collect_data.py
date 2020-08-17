
# # # Functions for retrieving project and sample data for web_app # # #

import os, psutil
from webapp import db, config
from webapp.models import Project

def list_file(filepath):
    list = []
    try:
        with open(filepath) as f:
            list = [i for i in f.read().split('\n') if i != '']
    except: print('{} not found'.format(filepath))
    return list

def list_ext(project_path, sample, ext):
    list = []
    for dirpath, dirnames, filenames in os.walk('{}/{}'.format(project_path, sample)):
            for f in sorted(filenames):
                if f[0] != '.':
                    f = f.split('.')
                    n, e = f[0], f[-1]
                    if len(f) == 3:
                        n = '{}.{}'.format(n, f[1])
                    if e in ext:
                        list.append('{}.{}'.format(n, e))
    return list

def get_projects():
    # projects_dict = {}
    # projects = list_file('webapp/assets/active_projects.txt')
    projects = Project.query.filter_by(active = True).all()
    projects_dict = {i.name: project_dict(i.name) for i in projects}
    # for project in projects:
        # project = project.split('::')
        # projects_dict[project[0]] = project_dict(project[0], project[1])
    return projects_dict

def get_archive():
    archive_dict = {}
    archive = list_file('webapp/assets/archived_projects.txt')
    for project in archive:
        project = project.split('::')
        archive_dict[project[0]] = project_dict(project[0])
    return archive_dict

def project_dict(project_id):
    project = {}
    project['id'] = project_id
    project['path'] = '{}/Projects/{}'.format(config['BASE_PATH'], project_id)
    log_lines = list_file('{}/{}.log'.format(project['path'], project_id))
    if 'Setup complete' in ' '.join(log_lines):
        project['start'] = log_lines[0][1:20]
        project['setup'] = True
    else:
        project['start'] = 'Not Started'
        project['setup'] = False
    comp_path = '{}/assets/complete.txt'.format(project['path'])
    acc_path = '{}/assets/accession.txt'.format(project['path'])
    comp_list, acc_list = list_file(comp_path), list_file(acc_path)
    project['total'] = len(acc_list)
    project['complete'] = len(comp_list)
    alive = False
    for line in log_lines[::-1]:
        if 'Batch' in line and 'PID' in line:
            last_PID = line.split(':')[-1].strip()
            print('Batch last PID', last_PID)
            try:
                proc = psutil.Process(int(last_PID))
                print('...', proc.name())
                if proc.name() in ('python', 'python3', 'Python', 'Python3'):
                    alive = True
            except: pass
            break
    project['alive'] = alive
    return project

def sample_status(project_path, sample):
    filepath = '{}/{}/{}.log'.format(project_path, sample, sample)
    log_lines = list_file(filepath)
    if log_lines:
        start_time = log_lines[0][1:20]
        last_line = log_lines[-1].rstrip()
        last_time = last_line[1:20]
        if 'Halt' in last_line: status = 'Halt'
        elif 'complete' in last_line: status = 'Complete'
        else: status = 'Running'
        command = last_line[20:]
    else:
        status = 'Unknown'
        start_time = last_time = command = ''
    dictionary = {'id': sample, 'start': start_time, 'last': last_time, 'status': status, 'cur': command}
    return dictionary

def status_list(project): ### Collects list of status dictionry data for each processing sample ###
    samples = list_file('{}/assets/processing.txt'.format(project['path']))
    status_list = []
    for sample in samples:
        status_dict = sample_status(project['path'], sample)
        status_list.append(status_dict)
    return status_list