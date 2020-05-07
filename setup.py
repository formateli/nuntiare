# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import setuptools
from nuntiare import PROJECT_NAME, DESCRIPTION, AUTHOR, VERSION


with open('README.rst', 'r') as fh:
    long_description = fh.read()


setuptools.setup(
    name=PROJECT_NAME,
    version=VERSION,
    author=AUTHOR,
    author_email='',
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://formateli.com/nuntiare',
    download_url='https://github.com/formateli/nuntiare',
    packages=setuptools.find_packages(),
    keywords='python report toolkit database',
    project_urls={
        'Bug Tracker': 'https://github.com/formateli/nuntiare',
        'Documentation': 'https://formateli.com/nuntiare/docs',
        'Forum': '',
        'Source Code': 'https://github.com/formateli/nuntiare',
        },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',  # noqa: E501
        'Natural Language :: English',
        'Natural Language :: Spanish',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Office/Business',
        'Topic :: Printing',
        ],
    platforms='any',
    scripts=[
        'scripts/nuntiare',
        'scripts/pluma',
        ],
    install_requires=[
        'python-dateutil',
        'psycopg2',
        'pillow',
        'wand',
        'ttkwidgets',
    ],
    python_requires='>=3.6',
)
