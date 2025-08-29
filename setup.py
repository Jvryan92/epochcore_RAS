from setuptools import find_packages, setup

setup(
    name="epoch_ras",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "torch",
        "numpy",
        "pandas"
    ],
)
