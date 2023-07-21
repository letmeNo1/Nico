import setuptools
from setuptools import setup, find_packages
import glob

with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()


def parse_requirements(filename):
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


setuptools.setup(
    name="adb_uiautomator",
    version="1.0.1",
    author="hank.huang",
    author_email="hank.huang550@gmail.com",
    description="A cross-platform desktop automated testing framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/letmeNo1/Makima",
    packages=setuptools.find_packages(),
    package_data={
<<<<<<< HEAD
        'adb_uiautomator': ['libs/start_auto.sh', 'libs/uiautomator.jar']
=======
        'adb_uiautomator': ['libs/android_test.apk', 'libs/app.apk']
>>>>>>> 27b78adcd6c451af86a53020d2c5171b0196d0b6
    },
    install_requires=[
        'lxml',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data = True
)