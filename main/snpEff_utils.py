#!/usr/bin/python3.5

# # # Functions to perform snpEff annotation of all samples in group and count impact statistics # # #

import sys, os, time, subprocess
from main.compile_group import load_group
from main import get_config

# real_path = os.path.realpath(__file__)
# filename = __file__.split('/')[-1]
# dir_path = real_path.rstrip(filename).rstrip('/')
# up_one = '/'.join(dir_path.split('/')[:-1])
# print(up_one)
# sys.path.insert(0, up_one)

def write_log(string, path): ### Logger, time-stamps and appends string to log file ###
	format = '%Y/%m/%d %H:%M:%S'
	stamp = time.strftime(format, time.localtime(time.time()))
	output = '>{} {}\n'.format(stamp, string)
	log_file = '{}/snpeff_utils.log'.format(path)
	with open(log_file, 'a') as f:
		f.write(output)

def load_db_tag(proj_path): ### Collects new database setup info from add_snpEff_db.txt in project reference directory ###
    filepath = '{}/reference/add_snpeff_db.txt'.format(proj_path)
    write_log('Loading data from {}'.format(filepath), proj_path)
    with open(filepath) as f:
        name = f.readline().split(':')[1].strip()
        version = f.readline().split(':')[1].strip()
        genome = f.readline().split(':')[1].strip()
        genes = f.readline().split(':')[1].strip()
    return name, version, genome, genes

def snpeff(snpEff_path, db_name, proj_path, sample, end): ### Runs SnpEff for a given sample and given end ###
	path = '{}/{}/out'.format(proj_path, sample)
	command = 'java -Xmx4g -jar {}/snpEff.jar {} {aln}/{}{}.vcf > {aln}/ann-{}{}.vcf'.format(snpEff_path, db_name, sample, end, sample, end, aln = path)
	pipe = subprocess.PIPE
	proc = subprocess.run(command, shell = True, stdout = pipe, stderr = pipe)
	if proc.stdout: write_log('[stdout]\n{}'.format(proc.stdout.decode()), proj_path)
	if proc.stderr: write_log('[stderr]\n{}'.format(proc.stderr.decode()), proj_path)
	if proc.returncode:
		write_log('Annotation of subtracted-{}{}.vcf failed, removing output file'.format(sample, end), proj_path)
		os.remove('{}/ann-{}{}.vcf'.format(path, sample, end))
	else:
		write_log('Annotation of {}{}.vcf successful'.format(sample, end), proj_path)

def snpeff_group(snpEff_path, db_info, proj_path, group): # Calls snpeff() on group #
	write_log('Preparing to annotate .vcf files', proj_path)
	write_log('{} samples in group'.format(len(group)), proj_path)
	db_name = '{}.{}'.format(db_info[0], db_info[1])
	ends = ('_p', )
	for sample in group:
		for end in ends:
			snpeff(snpEff_path, db_name, proj_path, sample, end)

def impact_count(proj_path, group): ### Counts the number of HIGH and MODERATE impact mutations ###
	impact_dict = {'HIGH': 0, 'MODERATE': 0}
	ends = ('_p', )
	for sample in group:
		for end in ends:
			filepath = '{}/{}/out/ann-{}{}.vcf'.format(proj_path, sample, sample, end)
			with open(filepath) as f:
				for line in f:
					if line[0] == '#': pass
					elif 'HIGH' in line: impact_dict['HIGH'] +=1
					elif 'MODERATE' in line: impact_dict['MODERATE'] +=1
	for key, value in impact_dict.items():
		write_log('{}: {}'.format(key, value), proj_path)

def main(proj_path):
	path_config = get_config.all()
	snpEff_path = '{}/VScope/extensions/{}'.format(path_config['BASE_PATH'], path_config['SNPEFF'])
	group = load_group(proj_path)
	print('Annotating vcf files')
	db_info = load_db_tag(proj_path)
	snpeff_group(snpEff_path, db_info, proj_path, group)
	print('Counting impact categories')
	impact_count(proj_path, group)

if __name__ == '__main__':
	proj_path = sys.argv[1].rstrip('/')
	main(proj_path)
