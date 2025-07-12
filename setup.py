#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README_improved.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aesdrive-tools",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Tools for working with AES Drive encrypted files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aesdrive-zendev",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "cryptography>=3.4.0",
        "colorama>=0.4.4",
        "typing-extensions>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "aesdecryptor=aesdecryptor_improved:main",
            "compare-directories=compare_directories_improved:main",
        ],
    },
)