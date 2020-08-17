
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from webapp import app, db
import time


class User(db.Model, UserMixin): ### User Project database table model ###
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(20), nullable = False)
    admin = db.Column(db.Boolean)

    def get_reset_token(self, expires_sec = 1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return "User('{}', '{}')".format(self.username, self.email)


class Project(db.Model): ### Project database table model ###
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), unique = True, nullable = False)
    organism = db.Column(db.String(32), unique = False)
    temp_path = db.Column(db.String(256), unique = False)
    reads_path = db.Column(db.String(256), unique = False)
    accession = db.Column(db.String(32), unique = False)
    reference = db.Column(db.String(32), unique = False)
    exons = db.Column(db.String(32), unique = False)
    exons_ver = db.Column(db.String(8), unique = False)
    subtract = db.Column(db.Boolean)
    annotate = db.Column(db.Boolean)
    concurrent = db.Column(db.Integer)
    threads = db.Column(db.Integer)
    delay = db.Column(db.Integer)
    active = db.Column(db.Boolean)
    setup = db.Column(db.Float)

    def __init__(self, name):
        self.name = name
        self.temp_path = None
        self.subtract = True
        self.annotate = True
        self.concurrent = 1
        self.threads = 0
        self.delay = 0
        self.active = True
        self.setup = 0

    def get_dict(self):
        return {
            'name': self.name,
            'orgn': self.organism,
            'temp': self.temp_path,
            'repo': self.reads_path,
            'acc': self.accession,
            'ref': self.reference,
            'exon': self.exons,
            'ver': self.exons_ver,
            'sub': self.subtract,
            'anno': self.annotate,
            'proc': self.concurrent,
            'thds': self.threads,
            'dlay': self.delay
        }
