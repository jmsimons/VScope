import os, shutil

def zip(self, ext): ### Sets up process() to run gzip on .fastq files ###
	for file in self.files[ext]:
		command = 'gzip {}.{}'.format(file, ext)
		self.process(command, 3)
		self.add_file('gz')

def wget_reads(self): ### Downloads remote file using wget ###
	addr = self.proj_dict['repo']

def copy_reads(self): ### Creates copy of sample reads files ###
	found = False
	for file in self.complete:
		if '.fastq' in file or '.fa' in file:
			found = True
	if found:
		print('Detected .fastq files, skipping reads file link')
		self.write('Detected .fastq files, skipping reads file link')
	else:
		print('Copying reads files')
		self.write('Copying reads files')
		repo_path = self.proj_dict['repo']
		for file in os.listdir(repo_path):
			if self.name in file:
				src = '{}/{}'.format(repo_path, file)
				dst = '{}/{}'.format(self.aln_path, file)
				self.write('Copying {}'.format(file))
				try:
					shutil.copy(src, dst)
				except:
					self.exit('Halt: Unable to find reads files at {}'.format(repo_path))
		
		self.add_file('fastq')
		self.add_file('gz')

def fastq_dump(self): ### Sets up process() to run fastq-dump on sample self.name ###
	if self.files['fastq'] or self.files['gz']:
		print('Detected .fastq files, skipping fastq-dump')
		self.write('Detected .fastq files, skipping fastq-dump')
	else:
		stage_desc = 'Fastq-dump: downloading reads files from NCBI'
		command = 'fastq-dump --split-files --gzip -O {} {}'.format(self.aln_path, self.name)
		self.process(stage_desc, command, 'dump')
		self.add_file('fastq')
		self.add_file('gz')

def trim(self): ### Sets up process() to run trimmomatic on sample reads files ###
	if self.files['fastq']: ext = 'fastq'
	else: ext = 'gz'
	try: left, right = self.files[ext][0], self.files[ext][1]
	except: return
	if 'paired_trim' in left and 'paired_trim' in right:
		print('Detected paired_trim files, skipping Trimmomatic')
		self.write('Detected paired_trim files, skipping Trimmomatic')
	else:
		stage_desc = 'Trimmomatic: trimming reads'
		trim_path = '{}/VScope/extensions/{}'.format(self.config['BASE_PATH'], self.config['TRIMM'])
		command = 'java -jar {trimm}/trimmomatic-0.39.jar PE -phred33 -threads {threads} {aln}/{left}.{ext} {aln}/{right}.{ext} {aln}/paired_trim-{left}.{ext} {aln}/ign-unpaired_trim-{left}.{ext} {aln}/paired_trim-{right}.{ext} {aln}/ign-unpaired_trim-{right}.{ext} ILLUMINACLIP:{trimm}/adapters/TruSeq3-PE-2.fa:2:30:10 LEADING:3 TRAILING:3 SLIDINGWINDOW:4:15 MINLEN:36'
		command = command.format(threads = self.threads, trimm = trim_path, aln = self.aln_path, left = left, right = right, ext = ext)
		self.process(stage_desc, command, 'trim')
		self.add_file(ext)
	self.files[ext].remove(left)
	self.files[ext].remove(right)
	os.remove('{}/{}.{}'.format(self.aln_path, left, ext))
	os.remove('{}/{}.{}'.format(self.aln_path, right, ext))

def mem_se(self): ### Sets up process() to run bwa mem on .fastq files, produces _1.sam and _2.sam ###
	if self.files['fastq']: ext = 'fastq'
	else: ext = 'gz'
	for file in self.files[ext].copy():
		check = '{}.sam'.format(file.split('.')[0])
		if check in self.complete:
			print('Detected {}.sam, skipping bwa mem'.format(file))
			self.write('Detected {}.sam, skipping bwa mem'.format(file))
		else:
			command = 'bwa mem -t {} {} {}/{}.gz > {}/{}.sam'.format(self.threads, self.reference, self.aln_path, file, self.aln_path, file.split('.')[0])
			self.process(command, 'mem')
			self.add_file('sam')

def mem_pe(self): ### Sets up process() to run bwa mem in paired-end mode, produces _p.sam ###
	check = '{}_p.sam'.format(self.name)
	if check in self.complete:
		print('Detected {}, skipping bwa mem'.format(check))
		self.write('Detected {}, skipping bwa mem'.format(check))
	else:
		stage_desc = 'BWA mem: mapping reads to reference genome'
		if self.files['fastq']: ext = 'fastq'
		else: ext = 'gz'
		print(self.files[ext])
		left, right = self.files[ext][0], self.files[ext][1]
		bwa_path = '{}/VScope/extensions/{}'.format(self.config['BASE_PATH'], self.config['BWA'])
		command = '{}/bwa mem -t {} {} {}/{}.{} {}/{}.{} > {}/{}_p.sam'.format(bwa_path, self.threads, self.reference, self.aln_path, left, ext, self.aln_path, right, ext, self.aln_path, self.name)
		self.process(stage_desc, command, 'mem')
		self.add_file('sam')
		self.write('Removing {}.{}'.format(left, ext))
		os.remove('{}/{}.{}'.format(self.aln_path, left, ext))
		self.write('Removing {}.{}'.format(right, ext))
		os.remove('{}/{}.{}'.format(self.aln_path, right, ext))

def bam(self): ### Sets up process() to run samtools view on .sam files to produce .bam files ###
	for file in self.files['sam']:
		stage_desc = 'Samtools view: compressing .sam to .bam'
		samtools_path = '{}/VScope/extensions/{}'.format(self.config['BASE_PATH'], self.config['SAMTOOLS'])
		command = '{}/samtools view -bS {}/{}.sam > {}/{}.bam'.format(samtools_path, self.aln_path, file, self.aln_path, file)
		self.process(stage_desc, command, 'bam')
		self.add_file('bam')
		print('Removing {}.sam'.format(file))
		self.write('Removing {}.sam'.format(file))
		os.remove('{}/{}.sam'.format(self.aln_path, file))
		self.files['sam'].remove(file)

def fstat(self): ### Sets up process() to run samtools flagstat on .bam files, produces fs-.txt files ###
	for file in self.files['bam']:
		if 'fs-{}.txt'.format(file) in self.complete or 'sort' in file:
			print('Detected fs-{}.txt, skipping samtools flagstat'.format(file))
			self.write('Detected fs-{}.txt, skipping samtools flagstat'.format(file))
		else:
			stage_desc = 'Samtools flagstat: generating alignment statistics'
			samtools_path = '{}/VScope/extensions/{}'.format(self.config['BASE_PATH'], self.config['SAMTOOLS'])
			command = '{}/samtools flagstat {}/{}.bam > {}/fs-{}.txt'.format(samtools_path, self.aln_path, file, self.out_path, file)
			self.process(stage_desc, command, 'stats')
			self.add_file('txt')

def n_sort(self): ### Sets up process() to run samtools sort by name on .bam files, produces sorted-.bam files ###
	for file in self.files['bam'].copy():
		if 'n_sort' in file:
			print('Detected {}.bam, skipping samtools sort'.format(file))
			self.write('Detected {}.bam, skipping samtools sort'.format(file))
		else:
			stage_desc = 'Samtools sort: sorting alignment data by name'
			samtools_path = '{}/VScope/extensions/{}'.format(self.config['BASE_PATH'], self.config['SAMTOOLS'])
			command = '{}/samtools sort -@ {} -n -o {}/n_sort-{}.bam {}/{}.bam'.format(samtools_path, self.threads, self.aln_path, file, self.aln_path, file)
			self.process(stage_desc, command, 'sort')
			self.add_file('bam')
			print('Removing {}.bam'.format(file))
			self.write('Removing {}.bam'.format(file))
			os.remove('{}/{}.bam'.format(self.aln_path, file))
			self.files['bam'].remove(file)

def fxmate(self): ### Sets up process() to run samtools fixmate on .bam files, produces fxmt-.bam files ###
	for file in self.files['bam'].copy():
		if 'fxmt' in file:
			print('Detected {}.bam, skipping samtools sort'.format(file))
			self.write('Detected {}.bam, skipping samtools sort'.format(file))
		else:
			stage_desc = 'Samtools fixmate: finding mate coordinates and insert sizes'
			samtools_path = '{}/VScope/extensions/{}'.format(self.config['BASE_PATH'], self.config['SAMTOOLS'])
			command = '{}/samtools fixmate -@ {} -m {}/{}.bam {}/fxmt-{}.bam'.format(samtools_path, self.threads, self.aln_path, file, self.aln_path, file)
			self.process(stage_desc, command, 'fxmate')
			self.add_file('bam')
			print('Removing {}.bam'.format(file))
			self.write('Removing {}.bam'.format(file))
			os.remove('{}/{}.bam'.format(self.aln_path, file))
			self.files['bam'].remove(file)

def p_sort(self): ### Sets up process() to run samtools sort by position on .bam files, produces p_sort-.bam files ###
	for file in self.files['bam'].copy():
		if 'p_sort' in file:
			print('Detected {}.bam, skipping samtools sort'.format(file))
			self.write('Detected {}.bam, skipping samtools sort'.format(file))
		else:
			stage_desc = 'Samtools sort: sorting alignment data by position'
			samtools_path = '{}/VScope/extensions/{}'.format(self.config['BASE_PATH'], self.config['SAMTOOLS'])
			command = '{}/samtools sort -@ {} -o {}/p_sort-{}.bam {}/{}.bam'.format(samtools_path, self.threads, self.aln_path, file, self.aln_path, file)
			self.process(stage_desc, command, 'sort')
			self.add_file('bam')
			print('Removing {}.bam'.format(file))
			self.write('Removing {}.bam'.format(file))
			os.remove('{}/{}.bam'.format(self.aln_path, file))
			self.files['bam'].remove(file)

def mrkdup(self): ### Sets up process() to run samtools markdup on .bam files, produces mrkdup-.bam files ###
	for file in self.files['bam'].copy():
		if 'mrkdup' in file:
			print('Detected {}.bam, skipping samtools sort'.format(file))
			self.write('Detected {}.bam, skipping samtools sort'.format(file))
		else:
			stage_desc = 'Samtools markdup: marking duplicate alignments'
			samtools_path = '{}/VScope/extensions/{}'.format(self.config['BASE_PATH'], self.config['SAMTOOLS'])
			command = '{}/samtools markdup -@ {} {}/{}.bam {}/mrkdup-{}.bam'.format(samtools_path, self.threads, self.aln_path, file, self.aln_path, file)
			self.process(stage_desc, command, 'mrkdup')
			self.add_file('bam')
			print('Removing {}.bam'.format(file))
			self.write('Removing {}.bam'.format(file))
			os.remove('{}/{}.bam'.format(self.aln_path, file))
			self.files['bam'].remove(file)

def index(self): ### Sets up process() to run samtools index on .bam files, produces .bai index files ###
	for file in self.files['bam']:
		if '{}.bam.bai'.format(file) in self.complete:
			print('Detected {}.bai, skipping samtools index'.format(file))
			self.write('Detected {}.bai, skipping samtools index'.format(file))
		else:
			stage_desc = 'Samtools index: indexing alignment data'
			samtools_path = '{}/VScope/extensions/{}'.format(self.config['BASE_PATH'], self.config['SAMTOOLS'])
			command = '{}/samtools index {}/{}.bam'.format(samtools_path, self.aln_path, file)
			self.process(stage_desc, command, 'index')
			self.add_file('bai')

def stats(self): ### Sets up process() to run samtools stats on .bam files, produces stats-.txt files ###
	for file in self.files['bam']:
		output = 'stats-{}.txt'.format(file.split('-')[-1])
		if output in self.complete:
			print('Detected stats-{}, skipping samtools stats'.format(file))
			self.write('Detected stats-{}, skipping samtools stats'.format(file))
		else:
			stage_desc = 'Samtools stats: generating comprehensive alignment statistics'
			samtools_path = '{}/VScope/extensions/{}'.format(self.config['BASE_PATH'], self.config['SAMTOOLS'])
			command = '{}/samtools stats -d {}/{}.bam > {}/{}'.format(samtools_path, self.aln_path, file, self.out_path, output)
			self.process(stage_desc, command, 'stats')
			self.add_file('txt')

def gencov(self): ### Sets up process() to run bedtools genomecov on .bam files, produces gencov-.txt files ###
	for file in self.files['bam']:
		check = 'gencov-{}.txt'.format(file.split('-')[-1])
		if check in self.complete:
			print('Detected gencov-{}.txt, skipping bedtools genomecov'.format(file))
			self.write('Detected gencov-{}.txt, skipping bedtools genomecov'.format(file))
		else:
			command = 'bedtools genomecov -g {} -ibam {}/{}.bam > {}/gencov-{}.txt'.format(self.reference, self.aln_path, file, self.out_path, file.split('-')[-1])
			self.process(command, 'gencov')
			self.add_file('txt')

def depth(self): ### Sets up process() to run samtools depth on .bam files, produces depth-.txt files ###
	for file in self.files['bam']:
		output = 'depth-{}.txt'.format(file.split('-')[-1])
		if output in self.complete:
			print('Detected depth-{}, skipping samtools depth'.format(file))
			self.write('Detected depth-{}, skipping samtools depth'.format(file))
		else:
			samtools_path = '{}/VScope/extensions/{}'.format(self.config['BASE_PATH'], self.config['SAMTOOLS'])
			command = '{}/samtools depth {}/{}.bam > {}/{}'.format(samtools_path, self.aln_path, file, self.aln_path, output)
			self.process(command, 'depth')
			self.add_file('txt')

def mpileup(self): ### Sets up process() to run samtools mpileup piped into bcftools call on .bam files, produces .vcf files ###
	for file in self.files['bam'].copy():
		output = file.split('-')[-1]
		if '{}.vcf'.format(output) in self.complete:
			print('Detected {}.vcf, skipping samtools mpileup and bcftools call'.format(file))
			self.write('Detected {}.vcf, skipping samtools mpileup and bcftools call'.format(file))
		else:
			stage_desc = 'Samtools mpileup > Bcftools call: performing alignment pileup and calling variants'
			samtools_path = '{}/VScope/extensions/{}'.format(self.config['BASE_PATH'], self.config['SAMTOOLS'])
			bcftools_path = '{}/VScope/extensions/{}'.format(self.config['BASE_PATH'], self.config['BCFTOOLS'])
			command = '{}/samtools mpileup -uf {} {}/{}.bam | {}/bcftools call -mv > {}/{}.vcf'.format(samtools_path, self.reference, self.aln_path, file, bcftools_path, self.out_path, output)
			self.process(stage_desc, command, 'mpileup')
			self.add_file('vcf')
			print('Removing {}.bam'.format(file))
			self.write('Removing {}.bam'.format(file))
			os.remove('{}/{}.bam'.format(self.aln_path, file))
			self.files['bam'].remove(file)

def snpeff(self):
	for file in self.files['vcf'].copy():
		if 'ann-{}'.format(file) in self.complete:
			print('Detected {}.vcf, skipping SnpEff'.format(file))
			self.write('Detected {}.vcf, skipping SnpEff'.format(file))
		else:
			snpeff_path = self.config['SNPEFF']
			command = 'java -Xmx4g -jar {}/snpEff.jar os7.0 {aln}/{}.vcf > {aln}/ann-{}.vcf'.format(snpeff_path, file, file, aln = self.aln_path)
			self.process(command, 'snpeff')
			self.add_file('vcf')
			# print('Removing {}.vcf'.format(file))
			# self.write('Removing {}.vcf'.format(file))
			# os.remove('{}/{}.vcf'.format(self.aln_path, file))
			# self.files['vcf'].remove(file)