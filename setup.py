import setuptools

with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()


def parse_requirements(filename):
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


setuptools.setup(
    name="AutoNico",
    version="1.3.15",
    author="Hank Huanng",
    author_email="hanhuang@jabra.com",
    description="Provide Basic Interface to conrol Mobile UI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/letmeNo1/nico",
    packages=setuptools.find_packages(),
    package_data={
        'auto_nico': ['android/package/*','console_scripts/inspector_web/templates/xml_template.html',
                        'console_scripts/inspector_web/static/*']
    },
    install_requires=[
        "flask==3.0.3",
        'lxml==5.1.0',
        'numpy>=1.24.4',
        'opencv-python==4.9.0.80',
        'loguru==0.7.2',
        'py-ios==0.1.3'
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
            'nico_ui = auto_nico.console_scripts.inspector_web.nico_inspector:main',
            'nico_uninstall_apk = auto_nico.console_scripts.uninstall_apk:main',

        ],
    },
    python_requires='>=3.6',
    include_package_data=True)
