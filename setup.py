from setuptools import setup, find_packages

setup(
    name="PPMS_Toolkit",
    version='0.1',
    author='Yunxiao LIU',
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "pandas"
    ],
    description="A toolkit for processing PPMS measurement data."
)
