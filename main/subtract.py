#!/usr/bin/python3.5

# # #  Performs subtraction by adding all calls for each end from group then subtracting repeat calls  # # #

import sys
from collections import OrderedDict
from main.compile_group import load_group
from main.mutation_stats import aggregate_chars
# from pickle_utils import dump, load


def write_log(path, string): ### Writes figures to log file ###
	log_file = '{}/stats/subtraction.log'.format(path)
	print(string)
	with open(log_file, 'a+') as f:
		f.write(string+'\n')

def write_chars(path, end, dictionary): ### Writes figures to output file ###
	out_file = '{}/stats/spectrum{}.txt'.format(path, end)
	with open(out_file, 'w') as f:
		f.write('snp\tcount\n') # SNP mutation characterisitics #
		for key, value in dictionary.items():
			f.write('{}\t{}\n'.format(key, value))

def find_singles(path, group, end): ### Gathers all calls for given end from group, then removes repeats ###
	snp_calls = {} # New calls added to dictionary #
	indel_calls = {}
	for sample in group:
		filepath = '{}/{}/out/{}{}.vcf'.format(path, sample, sample, end)
		with open(filepath) as f:
			for line in f:
				if line[0] == '#': pass
				else:
					line = line.split('\t')
					key = '{}:{}'.format(line[0], line[1])
					if line[7][:5] == 'INDEL': # Handles INDEL and SNP calls in their own dictionary #
						if key not in indel_calls:
							indel_calls[key] = 0 # Adds new calls to calls dict #
						else:
							indel_calls[key] += 1 # Increments repeat calls #
					else:
						if key not in snp_calls:
							snp_calls[key] = 0
						else:
							snp_calls[key] += 1
	snp_singles = {k:v for k, v in snp_calls.items() if not v}
	indel_singles = {k:v for k, v in indel_calls.items() if not v}
	total = 0
	for dict in (snp_singles, indel_singles): # Count each dict
		total += len(dict.keys())
	dictionary_pair = (snp_singles, indel_singles) # Pack dicts in tuple
	return dictionary_pair, total

def find_data(path, dictionary_pair, total, group, end, threshold): ### Matches call data from sample vcf line to singleton dictionary and writes data to sample dir ###
	found = 0
	for sample in group:
		i = 0
		inpath = '{}/{}/out/{}{}.vcf'.format(path, sample, sample, end)
		outpath = '{}/{}/out/subtracted-{}{}.vcf'.format(path, sample, sample, end)
		with open(inpath) as inf:
			with open(outpath, 'w') as outf:
				for line in inf:
					if line[0] == '#':
						outf.write(line)
					else:
						temp = line.split('\t')
						check = '{}:{}'.format(temp[0], temp[1])
						qual = float(temp[5])
						indel = True if temp[7][:5] == 'INDEL' else False
						if check in dictionary_pair[0] and not indel:
							if  qual >= threshold:
								outf.write(line)
								dictionary_pair[0][check] = line
								i += 1
							else:
								dictionary_pair[0].pop(check)
						elif check in dictionary_pair[1] and indel:
							if  qual >= threshold:
								outf.write(line)
								dictionary_pair[1][check] = line
								i += 1
							else:
								dictionary_pair[1].pop(check)
		write_log(path, '{} collected from {}'.format(i, sample))
		found += i
	return dictionary_pair, found

def count_mutations(mutations_dict): ### Counts subtracted mutations from dictionary ###
	dictionary = {}
	dictionary['total'] = 0
	dictionary['snp'] = 0
	for line in mutations_dict.values():
		if line[0] == '#' or line == '': pass
		else:
			dictionary['total'] += 1 # Counts each mutation #
			check = line.split('\t')[7][:5]
			if check != 'INDEL':
				line = line.split()
				dictionary['snp'] += 1 # Counts each SNP (non-INDEL) #
				variation = '{}-{}'.format(line[3], line[4])
				if variation in dictionary:
					dictionary[variation] += 1
				else:
					dictionary[variation] = 1
	return dictionary

def rename_chars(dictionary): ### Rename snp categories ###
	rename = (('G-A', 'GC-AT'), ('G-T', 'GC-TA'), ('G-C', 'GC-CG'),
			  ('A-G', 'AT-GC'), ('A-C', 'AT-CG'), ('A-T', 'AT-TA'),
			  ('total', 'tot_var'), ('snp', 'tot_snp'))
	for pair in rename:
		dictionary[pair[1]] = dictionary.pop(pair[0])
	return dictionary

def print_dict(dict):
	for key, value in dict.items():
		print(key, value)

def main(path, threshold):
	write_log(path, 'Performing subtraction with a quality threshold of {}'.format(threshold))
	group = load_group(path)
	ends = ('_p', ) # '_1', '_2', 
	for end in ends:
		dictionary_pair, total = find_singles(path, group, end)
		write_log(path, 'Processing {} total single occurrences from end {}'.format(total, end))
		dictionary_pair, found = find_data(path, dictionary_pair, total, group, end, threshold)
		write_log(path, 'Found records for {} out of {} single occurrences.'.format(found, total))
		chars_dict = count_mutations(dictionary_pair[0])
		print_dict(chars_dict)
		for key, value in count_mutations(dictionary_pair[1]).items(): # Combine indels and snps
			chars_dict[key] += value
		print_dict(chars_dict)
		chars_dict = aggregate_chars([], chars_dict)
		chars_dict = rename_chars(chars_dict)
		chars_dict = OrderedDict(sorted(chars_dict.items()))
		write_chars(path, end, chars_dict)

if __name__ == '__main__':
	proj_path = sys.argv[1].rstrip('/')
	if len(sys.argv) < 2:
		threshold = sys.argv[2]
	else:
		threshold = 0
	main(proj_path, threshold)
