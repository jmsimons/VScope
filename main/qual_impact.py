#!/usr/bin/python3.5

# # #  Analyses the impact of quality threshold on mutation spectrum from 0-228 # # # 

import sys
from collections import OrderedDict
from main.mutation_stats import aggregate_chars
from main.compile_group import load_group
from main.subtract import find_singles, count_mutations
# from pickle_utils import dump, load

def write_output(path, group_num, list): ### Writes string to quality_impact txt file ###
	filepath = '{}/stats/quality_impact.group-{}_p.txt'.format(path, group_num)
	with open(filepath, 'w') as f:
		f.write('qual\tavg\tsnp\tAT-CG\tAT-GC\tAT-TA\tGC-AT\tGC-CG\tGC-TA\n')
		for line in list:
			f.write(line + '\n')

def find_data(path, group, dictionary_pair, end): ### Searches for singleton data in group vcf files ###
	found = 0
	for sample in group:
		i = 0
		filepath = '{}/{}/out/{}{}.vcf'.format(path, sample, sample, end)
		with open(filepath) as f:
			for line in f:
				if line[0] == '#': pass
				else:
					temp = line.split('\t')
					check = '{}:{}'.format(temp[0], temp[1])
					qual = float(temp[5])
					indel = True if temp[7][:5] == 'INDEL' else False
					if check in dictionary_pair[0] and not indel:
							dictionary_pair[0][check] = line
							i += 1
					elif check in dictionary_pair[1] and indel:
							dictionary_pair[1][check] = line
							i += 1
		found += i
	return dictionary_pair, found

def combine_dicts(dictionary_pair):
	new_dict = {k: v for k, v in dictionary_pair[0].items()}
	for k, v in dictionary_pair[1].items():
		if k in new_dict: k += '_'
		new_dict[k] = v
	return new_dict

def analyse(path, group_num, dictionary, group_len): ### Analyses threshold impact by iterating through a threshold range ###
	list = []
	for i in range(0, 229):
		temp_dict = {}
		for key, value in dictionary.items():
			qual = float(value.split('\t')[5])
			if qual >= i:
				temp_dict[key] = value
		chars_dict = count_mutations(temp_dict)
		chars_dict = aggregate_chars([], chars_dict)
		chars_dict = OrderedDict(sorted(chars_dict.items()))
		avg = round(chars_dict['total'] / group_len, 1)
		snp = round(chars_dict['snp'] / chars_dict['total'] * 100, 2)
		vals = [v for v in chars_dict.values()]
		vals = [round(v / vals[6] * 100, 2) for v in vals[:6]]
		string = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(i, avg, snp, vals[0], vals[1], vals[2], vals[3], vals[4], vals[5])
		list.append(string)
	return list

def main(proj_path):
	group_num = '1'
	end = '_p'
	group = load_group(proj_path)
	dictionary_pair, total = find_singles(proj_path, group, end) # Change to dict_pair
	dictionary_pair, found = find_data(proj_path, group, dictionary_pair, end)
	print('Group total muts:', total, found)
	combined_dict = combine_dicts(dictionary_pair)
	results = analyse(proj_path, group_num, combined_dict, len(group))
	write_output(proj_path, group_num, results)

if __name__ == '__main__':
	proj_path = sys.argv[0]
	main(proj_path)