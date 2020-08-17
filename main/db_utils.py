import sqlalchemy
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DB:

    def __init__(self, project_path, project_id):
        self.db = sqlalchemy.create_engine('sqlite:///{}/{}.db'.format(project_path, project_id))

class Sample(Base):
    __tablename__ = 'sample'
    id = Column(Integer, primary_key = True)
    sample_id = Column(String(30), unique = True, nullable = False)
    total_vars = Column(Integer, nullable = False)
    total_snps = Column(Integer, nullable = False)

    def __init__(self, sample_id, total_vars, total_snps):
        self.sample_id = sample_id
        self.total_vars = total_vars
        self.total_snps = total_snps
    
    def __repr__(self):
        return "{}\t{}\t{}".format(self.sample_id, self.total_vars, self.total_snps)

class Variant(Base):
    __tablename__ = 'variant'
    id = Column(Integer, primary_key = True)
    sample_id = Column(String(30), unique = False, nullable = False)
    chromosome = Column(String(10), unique = False, nullable = False)
    position = Column(Integer, nullable = False)
    reference = Column(String(4), nullable = False)
    alternate = Column(String(4), nullable = False)
    snp = Column(Boolean, nullable = False)
    quality = Column(Integer, nullable = False)
    impact = Column(String(12), nullable = True)
    info = Column(String(100), nullable = False)
    annotation = Column(String(100), nullable = True)

    def __init__(self, sample_id, chrom, pos, ref, alt, snp, qual, info, impact = None, anno = None):
        self.sample_id = sample_id
        self.chromosome = chrom
        self.position = pos
        self.reference = ref
        self.alternate = alt
        self.snp = snp
        self.quality = qual
        self.impact = impact
        self.info = info
        self.annotation = anno
        # print(str(self))
    
    def __repr__(self):
        string = "{}\t{}\t{}\t{}\t{}\t{}\t{}".format(self.sample_id, self.chromosome, self.position, self.reference, self.alternate, self.snp, self.quality)
        if self.impact: string += "\t{}".format(self.impact)
        if self.annotation: string += "\t{}".format(self.annotation)
        string += "\t{}".format(self.info)
        return string
