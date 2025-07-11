from setuptools import setup, find_packages

setup(
    name="aesdrive-decryptor",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "cryptography>=41.0.0",
        "colorama>=0.4.6",
        "tqdm>=4.65.0",
    ],
    entry_points={
        "console_scripts": [
            "aes-decrypt=src.aes_decryptor:main",
        ],
    },
    author="Your Name",
    description="Professional AES Drive decryptor",
    long_description=open("docs/README.md").read(),
    long_description_content_type="text/markdown",
)