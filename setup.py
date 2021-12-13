import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flexclient",
    version="0.7",
    author="Open Research Institute",
    author_email="steve@conklinhouse.com",
    description="Python client API for the FLEX 6000 series radios",
    license="GPL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/phase4ground/flexclient",
    project_urls={
        "Bug Tracker": "https://github.com/phase4ground/flexclient/issues",
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=["selenium"],
    python_requires=">=3.6",
    zip_safe=False,
)
