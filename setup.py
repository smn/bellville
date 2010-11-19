from setuptools import setup, find_packages

setup(
    name = "smn-bellville",
    version = "0.1",
    url = 'http://github.com/smn/bellville',
    license = 'BSD',
    description = "Clickatell HTTP library",
    long_description = open('README.md', 'r').read(),
    author = 'Simon de Haan',
    author_email = "simon@praekeltfoundation.org",
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = [
        'setuptools',
        'pyOpenSSL',
        'nose',
    ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

