import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FlexModule",
    version="0.3",
    author="Open Research Institute",
    author_email="steve@conklinhouse.com",
    description="Python client API for the FLEX 6000/6400 radio",
    license="GPL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/phase4ground/flexmodule",
    project_urls={
        "Bug Tracker": "https://github.com/phase4ground/flexmodule/issues",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
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
