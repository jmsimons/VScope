from PyInstaller.__main__ import run


# Define build info #
package_name = 'VScope'
run_script = 'run_dist.py'
flags = ['--clean']
add_data = [
    './webapp/static/:./webapp/static/',
    './webapp/templates/:./webapp/templates/',
    './LICENSE:.',
    './README.md:.',
    '/Users/jaredsimons/Desktop/Projects/Variant-Scope_Resources/extensions/:./extensions/']
add_binary = ['./env/lib/python3.8/site-packages/_cffi_backend.cpython-38-darwin.so:.']


# Compile build info #
build_info = ['--name={}'.format(package_name), *flags, *['--add-data=' + i for i in add_data], *['--add-binary=' + i for i in add_binary], run_script]


# Run build #
if __name__ == '__main__':
    for i in build_info: print(i)
    run(build_info)