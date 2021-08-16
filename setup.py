import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "long_description.md").read_text()

# This call to setup() does all the work
setup(
    name="gensim_evaluations",
    version="0.1.2",
    description="Methods for evaluating low-resource word embedding models trained with gensim",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/n8stringham/gensim-evaluations",
    author="Nate Stringham",
    author_email="n8stringham@gmail.com",
    license="LGPL-2.1",
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        "Programming Language :: Python :: 3",
    ],
    packages=["gensim_evaluations"],
    include_package_data=True,
    install_requires=["sparqlwrapper","Wikidata"], 
    python_requires=">=3.7",

)
