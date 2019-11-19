"""Setup and packaging for Synse LoadGen."""

import os

from setuptools import find_packages, setup


here = os.path.abspath(os.path.dirname(__file__))

# Load the package's __init__.py file as a dictionary.
pkg = {}
with open(os.path.join(here, 'synse_loadgen', '__init__.py')) as f:
    exec(f.read(), pkg)

# Load the README
readme = ""
if os.path.exists('README.md'):
    with open('README.md', 'r') as f:
        readme = f.read()

setup(
    name=pkg['__title__'],
    version=pkg['__version__'],
    description=pkg['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    url=pkg['__url__'],
    author=pkg['__author__'],
    author_email=pkg['__author_email__'],
    license=pkg['__license__'],
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    python_requires='>=3.6',
    package_data={
        '': ['LICENSE'],
    },
    entry_points={
        'console_scripts': [
            'synse_loadgen = synse_loadgen.__main__:main',
        ],
    },
    install_requires=[
        'synse==3.0.0a6',
        'aiocache',
        'asyncio-throttle',
        'bison>=0.1.0',
        'structlog',
    ],
    zip_safe=False,
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ]
)
