import setuptools
from setuptools import setup, find_packages
import glob

with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()


def parse_requirements(filename):
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


setuptools.setup(
    name="AutoNico",
    version="1.0.2",
    author="Hank Hang",
    author_email="hanhuang@jabra.com",
    description="Provide Basic Interface to control Mobile UI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/letmeNo1/nico",
    packages=setuptools.find_packages(),
    package_data={
        'apollo_nico': ['package/android_test.apk', 'package/app.apk']
    },
    install_requires=[
        'opencv-python'
        'lxml'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'nico_dump = auto_nico.console_scripts.dump_ui:main',
            'nico_screenshot = auto_nico.console_scripts.screenshot:main',

        ],
    },
    python_requires='>=3.6',
    include_package_data=True)
