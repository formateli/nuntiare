# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

"""Nuntiare setup script"""

import setuptools
from nuntiare.version import get_version


with open('README.rst', 'r') as fh:
    long_description = fh.read()


setuptools.setup(
    name='Nuntiare',
    version=get_version(),
    author='Fredy Ramirez <https://formateli.com>',
    author_email='',
    description='Python report toolkit',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://formateli.com/nuntiare',
    download_url='https://github.com/formateli/nuntiare',
    packages=setuptools.find_packages(),
    keywords='python report toolkit database',
    project_urls={
        "Bug Tracker": 'https://github.com/formateli/nuntiare',
        "Documentation": 'https://formateli.com/nuntiare/docs',
        "Forum": '',
        "Source Code": 'https://github.com/formateli/nuntiare',
        },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Natural Language :: Spanish",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Database",
        "Topic :: Office/Business",
        "Topic :: Printing",
    ],
    install_requires=[],
    python_requires='>=3.6',
)
