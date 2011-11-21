from setuptools import setup, find_packages

def listify(filename):
    return filter(None, open(filename,'r').read().split('\n'))

setup(
    name = "python-clickatell",
    version = "0.1.3",
    url = 'http://github.com/smn/bellville',
    license = 'BSD',
    description = "Clickatell HTTP library",
    long_description = open('README.rst', 'r').read(),
    author = 'Simon de Haan',
    author_email = "simon@praekeltfoundation.org",
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = listify('requirements.pip'),
    classifiers = listify('CLASSIFIERS')
)

