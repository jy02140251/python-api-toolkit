"""
Python API Toolkit - Package Setup.

Build and distribution configuration for the API toolkit package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python-api-toolkit",
    version="1.0.0",
    author="jy02140251",
    description="Professional Python toolkit for building robust APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jy02140251/python-api-toolkit",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pyjwt>=2.8.0",
        "redis>=5.0.0",
        "pydantic>=2.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.23.0",
            "coverage>=7.4.0",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
    ],
)