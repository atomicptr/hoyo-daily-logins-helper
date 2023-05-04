import setuptools

with open("README.md", "r") as file:
    long_description = file.read()

with open("requirements.txt", "r") as file:
    requirements = file.read().split("\n")

setuptools.setup(
    name="hoyo_daily_logins_helper",
    version="1.1.0",
    entry_points={
        "console_scripts": ["hoyo-daily-logins-helper=src.main:main"],
    },
    author="Christopher Kaster",
    author_email="me@atomicptr.de",
    description="Get hoyo daily login rewards automatically!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/atomicptr/hoyo-daily-logins-helper",
    install_requires=requirements,
    packages=setuptools.find_packages(exclude="tests"),
    python_requires=">=3.10",
    classifiers=[
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ]
)
