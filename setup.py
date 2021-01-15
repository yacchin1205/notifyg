import sys
import setuptools
from io import open

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

pillow_version = ''
if sys.version_info[0] == 2:
    pillow_version = '<=6.2.2'

setuptools.setup(
    name="notifyg-yacchin1205",
    version="0.0.2",
    author="Satoshi Yazawa",
    description="Client tools for notify.guru",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://notify.guru",
    packages=setuptools.find_packages(),
    install_requires=['requests', 'six', 'qrcode', 'Pillow{}'.format(pillow_version), 'python-magic'],
    entry_points={'console_scripts':
                  ['notifyg=notifyg.cli:main']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
