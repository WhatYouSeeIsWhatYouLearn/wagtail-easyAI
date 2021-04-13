from os import path
from setuptools import find_packages, setup
from wagtail_automl import __version__


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="wagtail-automl",
    version=__version__,
    description="Automated machine learning for Wagtail CMS",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Finn Burmeister-Morton",
    # author_email="",
    url="https://github.com/whatyouseeiswhatyoulearn/wagtail-automl",
    packages=find_packages(),
    include_package_data=True,
    license="GPL 3",
    classifiers=[
        # "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GPL 3 License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Framework :: Django :: 3.1",
        "Framework :: Wagtail :: 2",
    ],
    install_requires=["Django>=2.2,<3.2",
                      "Wagtail>=2.1,<3",
                      "TPOT>=0.11",
                      "WagtailModelChooser>=0.3.0",],
    extras_require={
        # "testing": ["dj-database-url==0.5.0", "freezegun==0.3.15"],
        # "documentation": [
        #     "mkdocs==1.1.2",
        #     "mkdocs-material==6.2.8",
        #     "mkdocs-mermaid2-plugin==0.5.1",
        #     "mkdocstrings==0.14.0",
        #     "mkdocs-include-markdown-plugin==2.8.0",
        # ],
    },
)
