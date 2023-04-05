# This file is part of visier-connector-python.
#
# visier-connector-python is free software: you can redistribute it and/or modify
# it under the terms of the Apache License, Version 2.0 (the "License").
#
# visier-connector-python is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License, Version 2.0 for more details.
#
# You should have received a copy of the Apache License, Version 2.0
# along with visier-connector-python. If not, see <https://www.apache.org/licenses/LICENSE-2.0>.

"""
Visier Python Connector
"""

from setuptools import setup, find_packages  # noqa: H301
import visier


NAME = "visier-connector"
VERSION = visier.__version__

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "requests >= 2.28",
]

setup(
    name=NAME,
    version=VERSION,
    description="Visier People Data connector through the Visier SQL-like API",
    author="Visier Research & Development",
    author_email="info@visier.com",
    url="",
    keywords=["Visier Public Platform APIs", "Visier SQL-like"],
    python_requires=">=3.7",
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test", "tests"]),
    include_package_data=True,
    license="Apache License, Version 2.0",
    long_description="""\
    Simple Python Connector to simplify ingesting Visier People data into Python Frameworks like Pandas,
    though it can be used for any other purpose.
    The connector provides functions that enable execution of:
    * SQL-like queries
    * Aggregate queries
    * List, aka Detail, queries
    """
)
