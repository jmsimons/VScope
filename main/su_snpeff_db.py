#!/usr/bin/python3.5

import os, time, subprocess, re, shutil, sys
from main.snpEff_utils import write_log, load_db_tag

### Functions defined to set up and add SnpEff database from project reference genome ###

def create_dirs(path_to_snpEff, proj_path, db_name): ### Creates data/db_name and data/genomes directories if necessary ###
    write_log('Preparing to create directorires', proj_path)
    paths = ('{}/data/{}'.format(path_to_snpEff, db_name),
             '{}/data/genomes'.format(path_to_snpEff))
    for path in paths:
        if not os.path.exists(path):
            write_log('Creating directory {}'.format(path), proj_path)
            os.makedirs(path)
        else:
            write_log('{} already exists.'.format(path), proj_path)

def copy_rename(path_to_snpEff, proj_path, db_name, genome, exons): ### Copies and renames ref.fa and associated .gff or .gtf files to snpEff directory ###
    write_log('Preparing to copy reference files', proj_path)
    exons_ext = exons.split('.')[-1]
    if 'gff' in exons_ext: exons_ext = 'gff'
    else: exons_ext = 'gtf'
    new_exons = 'genes.{}'.format(exons_ext)
    check = '{}/data/{}/{}'.format(path_to_snpEff, db_name, new_exons)
    try:
        os.stat(check)
        write_log('{} already exists'.format(check), proj_path)
    except:
        write_log('Copying {} to {}'.format(exons, check), proj_path)
        shutil.copy('{}/reference/{}'.format(proj_path, exons), check)
    new_genome = '{}.{}'.format(db_name, genome.split('.')[-1])
    check = '{}/data/genomes/{}'.format(path_to_snpEff, new_genome)
    try:
        os.stat(check)
        write_log('{} already exists'.format(check), proj_path)
    except:
        write_log('Copying {} to {}'.format(genome, check), proj_path)
        shutil.copy('{}/reference/{}'.format(proj_path, genome), check)

def update_conf(path_to_snpEff, proj_path, name, version): ### Checks for new database in snpEff.config, adds if not found ###
    write_log('Preparing to update SnpEff.config', proj_path)
    filepath = '{}/snpEff.config'.format(path_to_snpEff.rstrip('/'))
    str_to_add = '\n# {name} genome, version {version}\n{name}.{version}.genome : N/A\n'.format(name = name, version = version)
    with open(filepath, 'r+') as f:
        file = f.read()
        if str_to_add in file: # re.search(str_to_add, file)
            write_log('SnpEff.config already contains db tag', proj_path)
        else:
            write_log('Adding database to SnpEff.config', proj_path)
            f.write(str_to_add)

def build_db(path_to_snpEff, proj_path, db_name, genes): ### Runs snpEff build database ###
    if 'snpEffPredictor.bin' in os.listdir('{}/data/{}'.format(path_to_snpEff, db_name)):
        write_log('Database already exists', proj_path)
        return
    write_log('Building SnpEff databade', proj_path)
    if 'gff' in genes.split('.')[-1]: setting = 'gff3'
    else: setting = 'gtf22'
    command = 'java -jar {}/snpEff.jar build -{} -v {}'.format(path_to_snpEff, setting, db_name)
    print(command)
    pipe = subprocess.PIPE
    proc = subprocess.run(command, shell = True, stdout = pipe, stderr = pipe)
    if proc.stdout: write_log('[stdout]\n{}'.format(proc.stdout.decode()), proj_path)
    if proc.stderr: write_log('[stderr]\n{}'.format(proc.stderr.decode()), proj_path)

def main(proj_path, snpEff_path):
    proj_path = proj_path.rstrip('/')
    snpEff_path = snpEff_path.rstrip('/')
    write_log('Setting up SnpEff database for project reference genome', proj_path)
    name, version, genome, exons = load_db_tag(proj_path)
    db_name = '{}.{}'.format(name, version)
    create_dirs(snpEff_path, proj_path, db_name)
    copy_rename(snpEff_path, proj_path, db_name, genome, exons)
    update_conf(snpEff_path, proj_path, name, version)
    build_db(snpEff_path, proj_path, db_name, exons)
    write_log('New database set-up complete', proj_path)

if __name__ == '__main__':
    proj_path = sys.argv[1]
    snpEff_path = sys.argv[2]
    main(proj_path, snpEff_path)