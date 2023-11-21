from setuptools import setup

setup(
    name='EcoCounterTool',
    version='1.0',
    install_requires=[
        'matplotlib',
        'geopandas',
        'contextily'
    ],
    author='jstier',
    packages=["code_folder"]
)
