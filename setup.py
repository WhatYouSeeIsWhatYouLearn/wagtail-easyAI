import os
import sys
from setuptools import setup
from setuptools.command.install import install

from wagtail_easyai import __version__


this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


# class VerifyVersionCommand(install):
#     """Custom command to verify that the git tag matches our version"""
#     description = 'verify that the git tag matches our version'

#     def run(self):
#         tag = os.getenv('CIRCLE_TAG')

#         if tag != __version__:
#             info = f"Git tag: {tag} does not match the version of this app: {__version__}"
#             sys.exit(info)


setup(
    name="wagtail-easyAI",
    version=__version__,
    description="Automated machine learning for Wagtail CMS",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Finn Burmeister-Morton",
    # author_email="",
    url="https://github.com/whatyouseeiswhatyoulearn/wagtail-easyAI",
    packages=["wagtail_easyai"],
    include_package_data=True,
    license="GPL 3",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Framework :: Django :: 3.1",
        "Framework :: Wagtail :: 2",
    ],
    keywords="wagtail machine-learning automl",
    install_requires=["Wagtail>=2.4,<3",
                      "TPOT>=0.11",
                      "wagtail-generic-chooser>=0.1.0",],
    python_requires=">=3.5",
    extras_require={
    },
    # cmdclass={
    #     'verify': VerifyVersionCommand,
    # }
)
