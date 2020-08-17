#!/usr/bin/python3.5

# # # Functions to setup new project directories and assets, and copy and index organism reference files # # #

import os, shutil, sys
sys.path.insert(0, 'tool_kit')
from main import get_config, su_snpeff_db
from main.batch import batch as Batch

base_path = get_config.base_path()

def write_file(filepath, content): ### Writes string content to filepath ###
	with open(filepath, 'w') as f:
		f.write(content)

def create_dirs(project_dict): ### Set up project directory and sub-directories ###
	if not os.path.exists(project_dict['path']):
		os.makedirs(project_dict['path']) # dict.path includes project name as dir #
	subdirs = ('assets', 'reference', 'stats', 'figures')
	for subdir in subdirs:
		path = '{}/{}'.format(project_dict['path'], subdir)
		if not os.path.exists(path):
			os.makedirs(path)
	if project_dict['temp']: # Create temp dir if not None #
		if not os.path.exists(project_dict['temp']):
			os.makedirs(project_dict['temp'])

def move_files(project_dict): ### Move reference genome and sample list files from web-app uploads to project dir ###
	old = '{}/Stage/{}'.format(base_path, project_dict['acc']) # Then move accession list #
	new = '{}/assets/accession.txt'.format(project_dict['path'])
	if not os.path.exists(new):
		shutil.move(old, new)
		# os.remove(old) # Remove file from downloads dir
	else: print('Skipping {} copy'.format(new))
	move = ('ref', 'exon')
	for file in move:
		if project_dict[file]:
			old = '{}/Stage/{}'.format(base_path, project_dict[file]) # First move reference genome and exons files #
			new = '{}/reference/{}'.format(project_dict['path'], project_dict[file])
			if not os.path.exists(new):
				shutil.move(old, new)
			else: print('Skipping {} copy'.format(new))
			if project_dict[file].split('.')[-1] == 'gz':
				os.system('gunzip {}'.format(new))
				project_dict[file] = project_dict[file].rstrip('.gz')
	# if project_dict['acc'].split('.')[-1] == 'gz':
	# 	os.system('gunzip {}'.format(new))

def index_ref(project_dict, bwa_path, samtools_path): ### Indexes reference genome file with bwa and samtools ###
	bwa = '{}/bwa index'.format(bwa_path)
	samtools = '{}/samtools faidx'.format(samtools_path)
	for command in (bwa, samtools):
		filepath = '{}/reference/{}'.format(project_dict['path'], project_dict['ref'])
		command = '{} {}'.format(command, filepath)
		# print(command)
		os.system(command)

def create_assets(project_dict): ## Creates project asset files ##
	
	def create_dict_file(): # Write project dict txt file #
		string = ''
		for key, value in project_dict.items():
			string += '{}::{}\n'.format(key, value)
		filepath = '{}/assets/project_dict.txt'.format(project_dict['path'])
		write_file(filepath, string)

	def create_list_files(): # Create complete and processing txt files #
		assets = ('complete', 'processing')
		for asset in assets:
			filepath = '{}/assets/{}.txt'.format(project_dict['path'], asset)
			if not os.path.exists(filepath):
				write_file(filepath, '')
	
	def create_group_files(): # Write group list txt files #
		filepath = '{}/assets/{}'.format(project_dict['path'], project_dict['acc'])
		access = []
		with open(filepath) as f:
			for line in f:
				access.append(line.rstrip())
		if project_dict['grp']:
			n = project_dict['grp']
			split = []
			for i in range(0, len(access), n):
				split.append(access[i:i + n])
			for i, l in enumerate(split):
				string = ''
				for sample in l:
					string += '{}\n'.format(sample)
				filepath = '{}/assets/group_{}.txt'.format(project_dict['path'], i + 1)
				if not os.path.exists(filepath):
					write_file(filepath, string)
	
	create_dict_file()
	create_list_files()
	# create_group_files()

def create_snpeff_tag(project_dict): ### Writes the add_snpEff_db.txt file in reference dir ###
	name = project_dict['orgn']
	version = project_dict['ver']
	genome = project_dict['ref']
	genes = project_dict['exon']
	string = 'name:{}\nversion:{}\ngenome:{}\ngenes:{}\n'.format(name, version, genome, genes)
	filepath = '{}/reference/add_snpeff_db.txt'.format(project_dict['path'])
	write_file(filepath, string)

def main(project_dict):
	config = get_config.all()
	base_path = config['BASE_PATH']
	create_dirs(project_dict)
	print('Project dirs created')
	move_files(project_dict)
	print('Reference and accession files moved')
	create_assets(project_dict)
	batch_log = Batch(project_dict).log
	batch_log('Setup: Directories and assets complete')
	print('Assets set up')
	bwa_path = "{}/VScope/extensions/{}".format(config['BASE_PATH'], config['BWA'])
	samtools_path = "{}/VScope/extensions/{}".format(config['BASE_PATH'], config['SAMTOOLS'])
	index_ref(project_dict, bwa_path, samtools_path)
	batch_log('Setup: Reference genome indexed')
	print('Reference genome indexed')
	if project_dict['anno']:
		snpEff_path = "{}/VScope/extensions/{}".format(config['BASE_PATH'], config['SNPEFF'])
		create_snpeff_tag(project_dict)
		su_snpeff_db.main(project_dict['path'], snpEff_path)
		print('SnpEff database setup for reference exons')
		batch_log('Setup: Annotation database complete')
	batch_log('Setup complete')
	sys.exit()
