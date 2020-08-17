#!/usr/bin/python3.5

# # # Ferforms pairwise analysis on sample vcf files to detect pollen contamination # # #

from compile_group import load_group
from collections import OrderedDict

def write_output(proj_path, group_num, results):
	filepath = '{}/stats/pollen_contam.group-{}.txt'.format(proj_path, group_num)
	with open(filepath, 'w') as f:
		f.write('Sample1-Sample2\tsample1_tot\tsample2_tot\tsimilar\n')
		for key, value in results.items():
			key = key.split('-')
			sample1, sample2 = key[0], key[1]
			f.write('{}\t{}\t{}\t{}\t{}\n'.format(sample1, sample2, value[1], value[2], value[0]))

def collect_sample(proj_path, sample, end): ### Collects dictionary of CHROM:POS for a given sample and given end ###
	filepath = '{}/{}/out/{}{}.vcf'.format(proj_path, sample, sample, end)
	list = []
	with open(filepath) as f:
		for line in f:
			if line[0] == '#': pass
			else:
				line = line.split('\t')
				key = '{}:{}'.format(line[0], line[1])
				list.append(key)
	return list

def compare(vcf_data, group):
	results = {}
	sample_a = 0
	while sample_a < len(vcf_data) - 1:
		sample_b = sample_a + 1
		while sample_b < len(vcf_data):
			key = '{}-{}'.format(group[sample_a], group[sample_b])
			val = len(set(vcf_data[sample_a]).intersection(vcf_data[sample_b]))
			results[key] = (val, len(vcf_data[sample_a]), len(vcf_data[sample_b]))
			sample_b += 1
		sample_a +=1
	return results

def main():
	group_num = '1'
	proj_path = '/home/jsimons/research/PRJNA385509'
	group = load_group(proj_path, group_num)
	ends = ('_p', ) # _1, _2
	vcf_data = []
	for sample in group:
		for end in ends:
			sample_dict = collect_sample(proj_path, sample, end)
			vcf_data.append(sample_dict)
	results = compare(vcf_data, group)
	results = OrderedDict(sorted(results.items()))
	write_output(proj_path, group_num, results)

if __name__ == '__main__':
	main()