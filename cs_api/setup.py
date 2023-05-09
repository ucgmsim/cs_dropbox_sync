"""
Install script for the cs_api package.
"""
from setuptools import setup, find_packages

setup(
    name="cs_api",
    version="1.0",
    packages=find_packages(),
    url="https://github.com/ucgmsim/cs_dropbox_sync",
    description="Cybershake Archive API",
    install_requires=["flask", "flask_cors", "pyyaml", "uwsgi"],
)
