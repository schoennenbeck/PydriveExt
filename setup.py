import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = []
with open('requirements.txt', 'r') as req:
    for line in req:
        install_requires.append(line.strip())

setuptools.setup(
    name="PydriveExt",
    version="0.0.1dev",
    author="Sebastian Schönnenbeck",
    author_email="schoennenbeck@gmail.com",
    description="Comfort extensions for pydrive.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/schoennenbeck/pydriveext",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
    install_requires=install_requires,
)