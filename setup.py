
import sys, time, os, shutil, psutil

def try_mkdir(dir_name):
    try:
        os.mkdir(dir_name)
    except Exception as e:
        print(e)

def build_dirs():
    sub_dirs = ('Projects', 'Reference', 'Stage', 'Archive')
    os.chdir('..')
    print('Building Variant-Scope directories...')
    if 'Variant-Scope' in os.getcwd():
        print('Parent directory already exist...')
    else:
        try_mkdir('Variant-Scope')
        shutil.move('VScope', 'Variant-Scope')
        os.chdir('Variant-Scope')
    for dir in sub_dirs:
        try_mkdir(dir)
    base_path = os.getcwd().rstrip('/')
    os.chdir('VScope')
    try_mkdir('webapp/assets')
    return base_path

def configure_app(base_path, cores, extensions, install_type):
    config = {}
    config.update(extensions)
    config['BASE_PATH'] = base_path
    config['CPU_CORES'] = cores
    if install_type == "local":
        config["LOGIN_DISABLED"] = "True"
    if install_type == "web":
        config["LOGIN_DISABLED"] = "False"
    file_path = 'vscope.conf'
    with open(file_path, 'w') as f:
        for k, v in config.items():
            f.write('{}:{}\n'.format(k, v))

def setup_webapp_db():
    from webapp import db, bcrypt, User, Project
    # from webapp.models import User, Project
    print('Building webapp database...')
    hashed_password = bcrypt.generate_password_hash("genomics").decode('utf-8')
    db.create_all()
    db.session.add(User(username = "admin", email = "admin@email.com", password = hashed_password))
    db.session.commit()
    db.session.close()

def try_remove(content):
    try: os.remove(content)
    except: print('Unable to remove', content)

def install_tools(base_path, package):
    os.system('bunzip2 {}'.format(package))
    package = '.'.join(package.split('.')[:-1])
    os.system('tar -xf {}'.format(package))
    try_remove(package)
    package = '.'.join(package.split('.')[:-1])
    os.chdir(package)
    os.system('./configure --prefix={}/VScope/extensions'.format(base_path))
    os.system('make')
    os.system('make install')
    os.chdir('..')
    try_remove(package)
    return 'bin'

def install_bwa(base_path, package):
    os.system('bunzip2 {}'.format(package))
    package = '.'.join(package.split('.')[:-1])
    os.system('tar -xf {}'.format(package))
    try_remove(package)
    package = '.'.join(package.split('.')[:-1])
    os.chdir(package)
    os.system('make')
    os.chdir('..')
    return package

def install_trimm(base_path, package):
    os.system('unzip {}'.format(package))
    try_remove(package)
    package = '.'.join(package.split('.')[:-1])
    return package

def install_snpeff(base_path, package):
    os.system('unzip {}'.format(package))
    try_remove(package)
    return 'snpEff'

def main():
    # Greet and Prompt for Install-Type #
    print("\nHello! Welcome to the Variant-Scope installer, we're glad you are here!\n")
    time.sleep(1)

    install_type = None
    while install_type not in ("local", "web"):
        install_type = input("\nWill this installation be accessed locally or over the web (local/web): ")
        time.sleep(.1)

    cores = psutil.cpu_count(logical = True)
    print("Available Cores:", cores)

    # Build Directories #
    base_path = build_dirs()

    # Decompress, Extract, and Install Third Party Applications #
    extensions = {'SAMTOOLS': 'samtools-1.10.tar.bz2',
                'BCFTOOLS': 'bcftools-1.10.2.tar.bz2',
                'BWA': 'bwa-0.7.17.tar.bz2',
                'TRIMM': 'Trimmomatic-0.39.zip',
                'SNPEFF': 'snpEff_latest_core.zip'}

    os.chdir('extensions')
    extensions['SAMTOOLS'] = install_tools(base_path, extensions['SAMTOOLS'])
    extensions['BCFTOOLS'] = install_tools(base_path, extensions['BCFTOOLS'])
    extensions['BWA'] = install_bwa(base_path, extensions['BWA'])
    extensions['TRIMM'] = install_trimm(base_path, extensions['TRIMM'])
    extensions['SNPEFF'] = install_snpeff(base_path, extensions['SNPEFF'])
    os.chdir('..')

    print('\nAdding paths to config...')
    for k, v in extensions.items():
        print(k, '\t', v)

    # Configure Variant-Scope #
    print(os.getcwd())
    configure_app(base_path, cores, extensions, install_type)
    setup_webapp_db()

    print('\nInstallation of Variant-Scope and its extensions has finished!\n')

if __name__ == '__main__':
    main()