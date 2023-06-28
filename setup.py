import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cs_dropbox_sync",
    version="1.0.0",
    author="Quakecore",
    description="Package for managing dropbox with simulation run archives",
    url="https://github.com/ucgmsim/cs_dropbox_sync",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
)
