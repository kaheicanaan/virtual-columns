import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="virtual_columns",
    version="0.0.1",
    author="Alan NG Ka Hei",
    author_email="kaheicanaan@gmail.com",
    description="Systematic way to build virtual columns with pandas and dictionary implementation",
    long_description=long_description,
    url="https://github.com/kaheicanaan/virtual-columns",
    packages=setuptools.find_packages(
        exclude=["build", "__pycache__"]
    ),
)
