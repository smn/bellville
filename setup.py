from setuptools import setup, find_packages

setup(
    name = "smn-bellville",
    version = "0.1",
    url = 'http://github.com/smn/bellville',
    license = 'BSD',
    description = "Clickatell HTTP library",
    author = 'Simon de Haan',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools',],
)

