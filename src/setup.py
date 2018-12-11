import setuptools

setuptools.setup(
    name="virtual_columns",
    version="0.0.1",
    author="Alan NG Ka Hei",
    author_email="kaheicanaan@gmail.com",
    description="Virtual Column Builder",
    url="https://github.com/kaheicanaan/virtual-columns",
    packages=setuptools.find_packages(
        exclude=["build", "__pycache__"]
    ),
    install_requires=["pandas"]
)
