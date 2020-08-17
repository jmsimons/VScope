#!/usr/bin/python3.5

import os, shutil, time
import main.get_config as get_config

def update_log(project_id, string): ### Writes archive updates to project log file ###
    path = ''
    log_file = '{}/{}.log'.format(path, project_id)
    format = '%Y/%m/%d %H:%M:%S'
    stamp = time.strftime(format, time.localtime(time.time()))
    output = '>{} {}\n'.format(stamp, string)
    with open(log_file, 'a+') as f:
        f.write(output)

def list_samples(project_path): ### Lists samples file from project assets ###
    with open("{}/assets/accession.txt".format(project_path)) as f:
        return [i for i in f.read().split('\n') if i != '']

def remove_project(project_id): ### Removes project dir and any remaining files ###
    base_path = get_config.base_path()
    try: shutil.rmtree('{}/Projects/{}'.format(base_path, project_id))
    except: print('Project directory not found')

def create_archive(project_id): ### Creates archive directory structure ###
    sub_dirs = ('vcf', 'data', 'logs', 'assets')
    for sub_dir in sub_dirs:
        os.makedirs("{}/{}".format(project_id, sub_dir))

def archive_move(project_path): ### Copies archive files into archive directory ###
    print('Copying log files')
    for file in os.listdir(project_path): # Copy project log files #
        if ".log" in file:
            shutil.copy("{}/{}".format(project_path, file), "logs")
    print('Copying stats files')
    for file in os.listdir("{}/stats".format(project_path)): # Copy project stats #
        shutil.copy("{}/stats/{}".format(project_path, file), "data")
    keep_asset = ('accession.txt', 'project_dict.txt')
    print('Copying project assets')
    for file in os.listdir("{}/assets".format(project_path)): # Copy project assets #
        if file in keep_asset:
            shutil.copy("{}/assets/{}".format(project_path, file), "assets")
    for sample in list_samples(project_path): # copy vcf and other sample files #
        print('Copying vcf files for sample:', sample)
        src_path = "{}/{}/out".format(project_path, sample)
        for file in os.listdir(src_path):
            if "vcf" in file.split('.')[-1]:
                shutil.copy("{}/{}".format(src_path, file), "vcf")

def archive_project(project_path):
    print('Building archive for project at', project_path)
    project_id = project_path.rstrip('/').split('/')[-1]
    base_path = get_config.base_path()
    os.chdir("{}/Archive".format(base_path))
    create_archive(project_id)
    os.chdir(project_id)
    archive_move(project_path)
    os.chdir("{}/VScope/web_app".format(base_path))