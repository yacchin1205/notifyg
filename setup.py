import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="notifyg-yacchin1205",
    version="0.0.1",
    author="Satoshi Yazawa",
    description="Client tools for notify.guru",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://notify.guru",
    packages=setuptools.find_packages(),
    install_requires=['requests', 'qrcode'],
    entry_points={'console_scripts':
                  ['notifyg=notifyg.cli:main']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
