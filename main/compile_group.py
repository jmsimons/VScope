
import sys

# # # This script compiles flagstat data for a group of samples loaded from the project's assets directory and writes file to stats directory # # #


def load_group(proj_path): ### Creates list of sample in group (from sub_grp_*.txt), also used by other scripts ###
	with open('{}/assets/accession.txt'.format(proj_path)) as f:
		group = [i for i in f.read().split('\n') if i != '']
	return group

def write_fs(path, group, dictionary): ### Writes figures to log file ###
	out_file = '{}/stats/flagstats.txt'.format(path)
	with open(out_file, 'w') as f:
		f.write('sample\treads\tmapped\tpaired\n')
		for sample in group:
			nums = dictionary[sample]
			f.write('{}\t{}\t{}\t{}\n'.format(sample, nums[0], nums[1], nums[2]))

def compile_fs(path, group): ### Compiles statistics from flagstat files ###
	dictionary = {}
	group_total = 0
	group_mapped = 0
	group_paired = 0
	for sample in group:
		ends = ('_p', ) # '_1', '_2', 
		for end in ends:
			lines = []
			filepath = '{}/{}/out/fs-{}{}.txt'.format(path, sample, sample, end)
			with open(filepath) as f:
				for line in f:
					lines.append(line)
				total = lines[0].split()[0] # Total reads #
				mapped = lines[4].split()[0] # Mapped reads #
				paired = lines[8].split()[0] # Properly paired reads #
			dictionary[sample] = [total, mapped, paired]
	return dictionary

def main(proj_path):
	group = load_group(proj_path)
	sample_dict = compile_fs(proj_path, group)
	write_fs(proj_path, group, sample_dict)

if __name__ == '__main__':
	proj_path = sys.argv[1].rstrip('/')
	main(proj_path)