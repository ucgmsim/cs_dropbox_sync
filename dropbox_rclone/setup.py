"""
Install script for the cs_api package.
"""
from setuptools import setup, find_packages

setup(
    name="dropbox_rclone",
    version="1.0",
    packages=find_packages(),
    url="https://github.com/ucgmsim/cs_dropbox_sync",
    description="Provides rclone functions to retrieve information from dropbox",
    install_requires=["pandas", "pyyaml"],
)
