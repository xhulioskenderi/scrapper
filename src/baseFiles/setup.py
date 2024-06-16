from setuptools import setup, find_packages

setup(
    name='baseFiles',
    version='1.0',
    packages=find_packages(),
    package_data={
        'baseFiles': ['*'],
    },
)