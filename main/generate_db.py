from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
import main.compile_group as compile_group

base_path = '/home/jsimons/vscope'
proj_path = '{}/projects'.format(base_path)

project_id = 'PRJNA385509'
db_filename = '{}_variants.db'.format(project_id)

def collect_sample(path, sample): ### Gathers all calls for a given sample in project, adds Sample and Variants to db ###
    filepath = '{}/{}/out/{}_p.vcf'.format(path, sample, sample)
    annotated = False
    total_vars = 0
    total_snps = 0
    print('Collecting variants for {}'.format(sample))
    session = Session()
    with open(filepath) as f:
        for line in f:
            if line[0] == '#':
                if 'SnpEff' in line:
                    annotated = True
            else:
                total_vars += 1
                line = line.split()
                chrom, pos, ref, alt, qual = line[0], line[1], line[3], line[4], line[5]
                if 'INDEL' in line[7][:9]:
                    snp = False
                else:
                    snp = True
                    total_snps += 1
                if annotated:
                    info = ';'.join([i for i in line[7].split(';') if 'ANN=' not in i])
                    anno = [i for i in line[7].split(';') if 'ANN=' in i][0]
                    impact = anno[80].split('|')[2]
                    # if 'MODIFIER' in anno: impact = 'MODIFIER'
                    # elif 'LOW' in anno: impact = 'LOW'
                    # elif 'MODERATE' in anno: impact = 'MODERATE'
                    # elif 'HIGH' in anno: impact = 'HIGH'
                    # else: impact = 'UNKNOWN'
                    new_variant = Variant(sample, chrom, pos, ref, alt, snp, qual, info, impact = impact, anno = anno)
                else:
                    info = '\t'.join(line[7:])
                    new_variant = Variant(sample, chrom, pos, ref, alt, snp, qual, info)
                session.add(new_variant)
    new_sample = Sample(sample, total_vars, total_snps)
    session.add(new_sample)
    print('Committing {} with {} variant records'.format(sample, total_vars))
    session.commit()
    session.close()

def build_db(proj_path, project_id, sample_list):
    # TODO: Create Session
    for sample in sample_list:
        collect_sample(proj_path, sample)
    # TODO: Close Session

def main(proj_path, project_id):
    global Session, Sample, Variant
    engine = create_engine('sqlite:///{}/{}'.format(proj_path, db_filename))
    from db_utils import Sample, Variant, Base
    Base.metadata.create_all(bind = engine)
    Session = sessionmaker(bind = engine)
    proj_path = '{}/{}'.format(proj_path, project_id)
    sample_list = compile_group.load_group(proj_path)
    build_db(proj_path, project_id, sample_list)

if __name__ == '__main__':
    main(proj_path, project_id)