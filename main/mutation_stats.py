#!/usr/bin/python3.5

# # # Counts SNP and INDEL mutations per sample in a given group # # #

from collections import OrderedDict
from main.compile_group import load_group

proj_path = '/home/jsimons/vscope/projects/PRJNA385509'
group_num = '1'

def write_output(path, group, group_num, dictionary): ### Writes figures to output file ###
	out_file = '{}/stats/initial_mutations.group-{}.txt'.format(path, group_num)
	with open(out_file, 'w') as f:
		f.write('sample\ttotal\tsnp\n')
		for sample in group:
			f.write('{}\t{}\t{}\n'.format(sample, dictionary[sample][0], dictionary[sample][1]))
			dictionary.pop(sample)
		# f.write('\nCategory:Percent\n') # SNP mutation characterisitics #
		# for key in dictionary:
		# 	if key not in ('total', 'snp'):
		# 		f.write('{}:{:.2f}\n'.format(key, (dictionary[key] / dictionary['snp'] * 100)))

def count_mutations(path, group): ### Counts mutations from _p.vcf per sample ###
	dictionary = {}
	dictionary['total'] = 0
	dictionary['snp'] = 0
	for sample in group:
		# print(sample)
		count = 0
		snp = 0
		filepath = '{}/{}/out/{}_p.vcf'.format(path, sample, sample)
		with open(filepath) as f:
			for line in f:
				if line[0] == '#' or line[0] == '': pass
				else:
					count += 1 # Counts each mutation #
					dictionary['total'] += 1
					if line.split()[7][:5] != 'INDEL':
						line = line.split()
						snp += 1 # Counts each SNP (non-INDEL) #
						dictionary['snp'] += 1
						variation = '{}-{}'.format(line[3], line[4])
						if variation in dictionary:
							dictionary[variation] += 1
						else:
							dictionary[variation] = 1
		dictionary[sample] = [count, snp]
	return dictionary

def aggregate_chars(group, dictionary): ### Aggregate SNP mutation characteristics ###
	categories = ('G-A', 'G-T', 'G-C', 'A-G', 'A-C', 'A-T') # Each mutation fits into one of these six categories #
	new_dict = {k: 0.0 for k in categories} 
	for sample in group: # Move sample stats to new_dict #
		new_dict[sample] = dictionary.pop(sample)
	new_dict['total'] = dictionary.pop('total') # Move total and snp stats to new_dict #
	new_dict['snp'] = dictionary.pop('snp')
	compliment = {'C':'G', 'T':'A', 'G':'C', 'A':'T'}
	for key, value in dictionary.items():
		key = key.split('-')
		if len(key[1]) > 1: # If mutation is ambiguous, incriment each possible category by 0.5 #
			key[1] = key[1].split(',')			
			cat_1 = '{}-{}'.format(key[0], key[1][0])
			try: new_dict[cat_1] += (value / 2)
			except: # Flip mutation to compliment if necessary #
				key[0] = compliment[key[0]]
				key[1][0] = compliment[key[1][0]]
				cat_1 = '{}-{}'.format(key[0], key[1][0])
				new_dict[cat_1] += (value / 2)
			cat_2 = '{}-{}'.format(key[0], key[1][1])
			try: new_dict[cat_2] += (value / 2)
			except: # Flip mutation to compliment if necessary #
				key[1][1] = compliment[key[1][1]]
				cat_2 = '{}-{}'.format(key[0], key[1][1])
				new_dict[cat_2] += (value / 2)
		else: # Incriment mutation category by 1 #
			category = '{}-{}'.format(key[0], key[1])
			try: new_dict[category] += value
			except: # Flip mutation to compliment if necessary #
				key[0] = compliment[key[0]]
				key[1] = compliment[key[1]]
				category = '{}-{}'.format(key[0], key[1])
				new_dict[category] += value
	return new_dict

def main(path):
	path = path.rstrip('/')
	group = load_group(path)
	dictionary = count_mutations(path, group)
	dictionary = aggregate_chars(group, dictionary)
	dictionary = OrderedDict(sorted(dictionary.items()))
	write_output(path, group, group_num, dictionary)

if __name__ == '__main__':
    main(proj_path)