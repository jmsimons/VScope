#!/usr/bin/python3.5

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, BooleanField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from webapp.collect_data import list_file
from webapp.models import User


class RegisterUser(FlaskForm):
    username = StringField('Username', validators = [DataRequired(), Length(min = 5, max = 20)])
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Register User')


class SearchUser(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    search = SubmitField('Search')


class EditUser(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    search = SubmitField('Search')


class RemoveUser(FlaskForm):
    remove = BooleanField('Are you sure you want to permanently remove this user?')
    search = SubmitField('Remove')


class Login(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if not user:
            raise ValidationError('There is no account with that email. Contact the administrator.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class ProjectSetupA(FlaskForm):
    project_name = StringField('Project Name', validators = [DataRequired(), Length(min = 2, max = 30)])
    organism = StringField('Organism Name', validators = [DataRequired(), Length(min = 2, max = 30)])
    # temp_path = StringField('Temporary path (optional, /path/to/directory )')
    submit = SubmitField('Next')

class ProjectSetupB(FlaskForm):
    accession = FileField('Sample list text file:', validators = [DataRequired()])
    sources = ['Local', 'NCBI-SRA', 'wget'] # , 'upload'
    sample_source = SelectField('Sample Reads Data:', choices = [(i, i) for i in sources])
    sample_path = StringField('Path to sample .fastq type reads files')
    reference = FileField('Reference Genome FASTA file (.fa, .fasta, .fas)', validators = [DataRequired()])
    exons = FileField('Reference Annotation file (optional, .gff or .gtf)')
    ex_version = StringField('Reference Annotation version (ie. 7.0.1). This is required only for SnpEff annotation.')
    submit1 = SubmitField('Setup Project')
    submit2 = SubmitField('Advanced Options')

class ProjectSetupC(FlaskForm):
    processes = SelectField('Number of samples to run in parallel', choices = [(i, str(i)) for i in range(1,11)]) # 1-10 selector #
    trd_choices = [('Auto', 'Auto')]
    trd_choices.extend([(i, str(i)) for i in range(0,17)])
    threads = SelectField('Number of additional threads for alignment and other tasks', choices = trd_choices) # 0-16 selector with auto option #
    time_delay = SelectField('Delay (in minutes) between sample deployment', choices = [(i, str(i)) for i in range(0, 61, 15)]) # minutes: 0-60 in steps of 15 #
    submit = SubmitField('Setup Project')

class ConfirmSetup(FlaskForm):
    submit = SubmitField('Setup Project')


class StartStopProject(FlaskForm):
    start = SubmitField('Start Project')
    stop = SubmitField('Stop Project')


class ArchiveRemove(FlaskForm):
    archive = BooleanField('Create archive of project files')
    remove = BooleanField('Remove project directories and files from active projects')
    submit = SubmitField('Perform Actions')


class AnnotateReport(FlaskForm):
    annotate = SubmitField('Annotate Variants')
    analyse = SubmitField('Threshold Analysis')
    subtract = BooleanField('Remove Common Variants')
    quality_choices = [(i, i) for i in range(229)]
    quality = SelectField('Phred Quality Threshold', choices = quality_choices)
    var_type_choices = ['SNP', 'INDEL', 'Both']
    var_type_choices = [(i, i) for i in var_type_choices]
    var_type = SelectField('Mutation Type', choices = var_type_choices)
    filter = SubmitField('Filter Variants')