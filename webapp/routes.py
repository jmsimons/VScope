
import time
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from webapp import app, config, db, bcrypt, send_reset_email
from webapp.models import User, Project
from webapp.forms import RegisterUser, Login, RequestResetForm, ResetPasswordForm, ProjectSetupA, ProjectSetupB, ProjectSetupC, ConfirmSetup, StartStopProject, ArchiveRemove, AnnotateReport
from webapp.collect_data import list_file, list_ext, get_projects, get_archive, project_dict, sample_status, status_list
from webapp.project_actions import setup_project, run_project, stop_project, run_subtraction, run_annotation, run_analysis, archive_project, remove_project


### User Authentication Web Routes ###

@app.route('/register_user', methods = ['GET', 'POST'])
def register_user():
    form = RegisterUser()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
    return render_template('register_user.html', title = 'Register User', form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        print(user)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            return redirect(url_for('home'))
        flash('Login Unsuccessful. Please check email and password.')
    return render_template('login.html', title = 'Login', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# @app.route('/manage_users')
# @login_required
# def manage_users():
#     users = User.query.all()
#     return render_template('users.html', users = users)

@app.route('/search_user')
@login_required
def search_user():
    form = SearchUser()
    return render_template('search_user.html', form = form)

@app.route('/user_details/<user>')
@login_required
def manage_users(user):
    users = User.query.all()
    return render_template('users.html', users = users)

@app.route('/reset_password', methods = ['GET', 'POST'])
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title = 'Reset Password', form = form)

@app.route('/reset_password/reset_password/<token>', methods = ['GET', 'POST'])
def reset_token(token):
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title = 'Reset Password', form = form)


### Main App Web Routes ###

@app.route('/')
@login_required
def home():
    projects = get_projects()
    return render_template('home.html', projects = projects)

@app.route('/<project_id>', methods = ['GET', 'POST'])
@login_required
def project(project_id):
    form = StartStopProject()
    project = get_projects()[project_id]
    if request.method == 'POST':
        if form.start.data:
            if run_project(project['path']):
                flash('Project Running', 'info')
                time.sleep(2)
        elif form.stop.data:
            if stop_project(project):
                flash('Project Stopped', 'info')
                time.sleep(2)
        return redirect(url_for('project', project_id = project_id))
    processing = status_list(project)
    return render_template('project.html', title = 'Project Dashboard', project = project, processing = processing, form = form)

@app.route('/<project_id>/<sample>')
@login_required
def sample(project_id, sample):
    print('Sample:', sample)
    projects = get_projects()
    project = projects[project_id]
    status = sample_status(project['path'], sample)
    logs = list_ext(project['path'], sample, 'log')
    return render_template('sample.html', title = 'Sample Dashboard', project = project, sample = status, logs = logs)

@app.route('/view/<project_id>/<document>')
@app.route('/view/<project_id>/<sample>/<document>')
@login_required
def file_view(project_id, document, sample = None):
    projects = get_projects()
    project = projects[project_id]
    title = document
    if sample: document = list_file('{}/{}/{}'.format(project['path'], sample, document))
    else: document = list_file('{}/{}'.format(project['path'], document))
    return render_template('file_view.html', title = title, document = document, sample = sample)

@app.route('/<project_id>/accession')
@login_required
def accession(project_id):
    projects = get_projects()
    project = projects[project_id]
    title = '{} Samples'.format(project_id)
    accession = list_file('{}/assets/{}'.format(project['path'], 'accession.txt'))
    return render_template('accession.html', title = title, project_id = project_id, accession = accession)

@app.route('/project_setup', methods = ['GET', 'POST'])
@login_required
def project_setup_A():
    form = ProjectSetupA()
    if form.validate_on_submit():
        project_id = form.project_name.data
        project = Project(project_id)
        project.organism = form.organism.data
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('project_setup_B', project_id = project_id))
    return render_template('proj_setup_A.html', title = 'New Project', form = form)

@app.route('/project_setup-<project_id>', methods = ['GET', 'POST'])
@login_required
def project_setup_B(project_id):
    global config
    form = ProjectSetupB()
    if form.validate_on_submit():
        project = Project.query.filter_by(name = project_id).first()
        project.reads_path = form.sample_path.data
        project.exons_ver = form.ex_version.data
        acc_filename = form.accession.data.filename
        project.accession = acc_filename
        form.accession.data.save('{}/Stage/{}'.format(config['BASE_PATH'], acc_filename))
        ref_filename = form.reference.data.filename
        project.reference = ref_filename
        form.reference.data.save('{}/Stage/{}'.format(config['BASE_PATH'], ref_filename))
        exon_filename = form.exons.data.filename
        project.exons = exon_filename
        form.exons.data.save('{}/Stage/{}'.format(config['BASE_PATH'], exon_filename))
        db.session.commit()
        if form.submit1.data:
            setup_project(project)
            time.sleep(1)
            return redirect(url_for('project', project_id = project_id))
        elif form.submit2.data:
            return redirect(url_for('project_setup_C'))
    return render_template('proj_setup_B.html', title = 'New Project', form = form)

@app.route('/project_setup--<project_id>', methods = ['GET', 'POST'])
@login_required
def project_setup_C(project_id):
    form = ProjectSetupC()
    if request.method == 'POST':
        project = Project.query.filter_by(name = project_id).first()
        project.concurrent = form.processes.data
        project.threads = form.threads.data
        project.delay = form.time_delay.data
        project.active = True
        db.session.add(project)
        db.session.commit()
        setup_project(project)
        time.sleep(2)
        return redirect(url_for('project', project_id = project_id))
        # return redirect(url_for('confirm_setup'))
    return render_template('proj_setup_C.html', title = 'New Project', form = form)

# @app.route('/confirm_setup-<project_id>', methods = ['GET', 'POST'])
# @login_required
# def confirm_setup(project_id):
#     global config
#     form = ConfirmSetup()
#     form_data = new.get_dict()
#     if request.method == 'POST':
#         pass
#     return render_template('confirm_setup.html', form = form, form_data = form_data)

@app.route('/<project_id>/archive_remove', methods = ['GET', 'POST'])
@login_required
def archive_remove(project_id):
    form = ArchiveRemove()
    if form.validate_on_submit():
        project = get_projects()[project_id]
        if form.archive.data:
            archive_project(project['path'])
            flash('{} has been added to archived projects.'.format(project_id), 'info')
        if form.remove.data:
            remove_project(project_id)
            flash('{} has been removed from active projects.'.format(project_id), 'info')
            return redirect(url_for('home'))
        return redirect(url_for('project', project_id = project_id))
    return render_template('archive_remove.html', project_id = project_id, form = form)

@app.route('/archived_projects')
@login_required
def archive():
    projects = get_archive()
    return render_template('archive.html', projects = projects)

@app.route('/<project_id>/annotate_report/', methods = ['GET', 'POST'])
@login_required
def annotate_report(project_id):
    form = AnnotateReport()
    if request.method == 'POST':
        project = get_projects()[project_id]
        # print(request.form)
        if 'annotate' in request.form:
            # print('Annotating Project VCFs')
            run_annotation(project['path'])
        elif 'analyse' in request.form:
            print('Analysing Quality Threshold Impact to Variant Spectrum')
            run_analysis(project['path'])
        elif 'filter' in request.form:
            print('Filtering Variants at a Threshold of:', request.form['quality'])
            print('Removing Common Variants')
            run_subtraction(project['path'], request.form['quality'])
    return render_template('annotate_report.html', project_id = project_id, form = form)