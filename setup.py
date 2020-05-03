# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

"""Nuntiare setup script"""

from distutils.core import setup
from nuntiare.version import get_version


def run():
    setup(
        name="Nuntiare",
        version=get_version(),
        url="https://formateli.com/nuntiare/",
        download_url="https://github.com/formateli/nuntiare",
        description="Python report toolkit.",
        author="Fredy Ramirez",
        author_email="",  # TODO
        maintainer_email="",  # TODO
        classifiers=[
            "Development Status :: Prototype",
            "Environment :: Win32 (MS Windows)",
            "Environment :: X11 Applications",
            "Intended Audience :: Developers",
            "Intended Audience :: Information Technology",
            "License :: OSI Approved :: GNU General Public License v3",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
        ],
        license="GNU General Public License v3",
        platforms=["OS Independent"],
        packages=[
            "nuntiare", "nuntiare.data_providers", "nuntiare.outcome",
            "nuntiare.template", "nuntiare.render", "nuntiare.render.html"
        ],
        package_data={'nuntiare': ['nuntiare.cfg']},
        scripts=['scripts/nuntiare', 'scripts/pluma'],
        data_files=[("docs", ["README", "LICENSE", "COPYRIGHT"])],
    )


if __name__ == "__main__":
    run()
