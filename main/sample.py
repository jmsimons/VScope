#!/usr/bin/python3

import os, time, subprocess
from sys import exit

class sample: ### Data and methods for managing workflow on a single sample ###

	def __init__(self, sample, project_dict, config):
		# Define Class Attributes #
		self.config = config
		self.proj_dict = project_dict
		self.name      = sample
		self.threads   = self.proj_dict['thds']
		if self.threads == 'Auto':
			self.threads = self.config['CPU_CORES']
		proj_path = project_dict['path'].rstrip('/')
		if self.proj_dict['temp']:
			self.aln_path = '{}/{}/aln'.format(self.proj_dict['temp'].rstrip('/'), self.name) # Static aln directory path #
		else:
			self.aln_path = '{}/{}/aln'.format(proj_path, self.name) # Static aln directory path #
		self.out_path  = '{}/{}/out'.format(proj_path, self.name) # Static output directory path #
		self.reference = '{}/reference/{}'.format(proj_path, self.proj_dict['ref'])
		self.files     = {'fastq':[], 'gz':[], 'sam':[], 'bam':[], 'cram':[], 'txt':[], 'bai':[], 'vcf':[]}
		# Set-up/Check Sample Environment #
		if not os.path.exists(self.aln_path): # Sets up sample aln directory #
			os.makedirs(self.aln_path)
		if not os.path.exists(self.out_path): # Sets up sample out directory #
			os.makedirs(self.out_path)
		os.chdir('{}/{}'.format(proj_path, self.name))
		print('Working in...', os.getcwd())
		self.refresh_complete() # Update internal completed files list #
		for key in self.files: # Scans for existing files by extension (ignores log files) #
			self.add_file(key)
		self.write('Sample initialized!')

	def write(self, string, output_file = '', nl = 1): ### Writes to log files, log file name referenced from self.stages ###
		while nl:
			string += '\n'
			nl -= 1
		if output_file == 'complete':
			output = string
		else:
			format = '%Y/%m/%d %H:%M:%S'
			stamp = time.strftime(format, time.localtime(time.time()))
			output = '>{} {}'.format(stamp, string)
		if not output_file: output_file = '{}.log'.format(self.name)
		else: output_file = '{}.{}.log'.format(self.name, output_file)
		with open(output_file, 'a+') as f:
			f.write(output)

	def add_file(self, ext): ### Adds files of a given extension to their respective lists and the master complete.log list ###
		print('Scanning for {} files'.format(ext))
		dirs = (self.out_path, self.aln_path)
		for dir in dirs:
			for f in sorted(os.listdir(dir)):
				if f[0] != '.':
					f = f.split('.')
					n, e = f[0], f[-1]
					if len(f) == 3:
						n = '{}.{}'.format(n, f[1])
					if e in ext:
						if n not in self.files[e]:
							if 'ign' not in n:
								print('Adding {}.{}'.format(n, e))
								self.write('Adding {}.{}'.format(n, e))
								self.files[e].append(n)
							if '{}.{}'.format(n, e) not in self.complete: # adds new files to complete.log #
									self.write('{}.{}'.format(n, e), output_file = 'complete')
		self.files[ext].sort()
		self.refresh_complete()

	def refresh_complete(self): ### Creates/updates complete.log file and internal master complete list ###
		self.complete = []
		if not os.path.exists('{}.complete.log'.format(self.name)):
			self.write('', nl = 0, output_file = 'complete')
		with open('{}.complete.log'.format(self.name)) as f:
			for line in f:
				self.complete.append(line.strip())

	def process(self, stage_desc, command, output_file): ### Executes a shell command and waits for completion, writes stdout and stderr to specified log file, exits program on non-0 return code ###
		self.write(stage_desc)
		print('Executing:', command)
		pipe = subprocess.PIPE
		try: proc = subprocess.run(command, shell = True, stdout = pipe, stderr = pipe) # starts shell process, returns 0 if successful #
		except:
			self.exit('Halt: Sample Interupted!')
		print('[{!r} exited with {}]'.format(command, proc.returncode))
		self.write('[{!r} exited with {}]'.format(command, proc.returncode))
		if proc.stdout: self.write('[stdout]\n{}'.format(proc.stdout.decode()), output_file = output_file)
		if proc.stderr: self.write('[stderr]\n{}'.format(proc.stderr.decode()), output_file = output_file)
		if proc.returncode: # proc.returncode evaluates to True if non-zero #
			self.exit('Halt: Process exited with error!') # exit called with error #

	def exit(self, code = 0):
		if code: ### Process returncode is non-0 or KeyboardInterupt, called from process() upon error, deletes unfinished files ###
			dirs = (self.out_path, self.aln_path)
			for dir in dirs:
				for f in sorted(os.listdir(dir)):
					if f[0] != '.': # Ignores filenames that start with '.' #
						f = f.split('.')
						n, e = f[0], f[-1]
						if len(f) == 3:
							n = '{}.{}'.format(n, f[1])
						if e != 'log': # Ignores log files #
							if n+'.'+e not in self.complete: # Removes from dir if not listed in self.files (assumed to be incomplete) #
								f = '{}.{}'.format(n, e)
								print('Removing {}'.format(f))
								self.write('Removing {}'.format(f))
								os.remove('{}/{}'.format(dir, f))
			print(code)
			self.write(code)
			exit() # sys.exit() when called with error #
		else: ### Successful completion of workflow ###
			print('{} workflow complete.'.format(self.name))
			self.write('{} workflow complete.'.format(self.name))
			file_list = [] # Retained files list returned to the calling script #
			for key in self.files:
				for file in self.files[key]:
					file_list.append('{}.{}'.format(file, key))
			return file_list
