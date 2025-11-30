#!/usr/bin/env python3
"""
Setup script for PyRadio
Provides compatibility with debhelper and older build systems.
"""

from setuptools import setup, find_packages

setup(
    name='pyradio',
    version='1.0.0',
    description='Internet radio player for Linux desktop',
    long_description=open('README.md').read() if __name__ == '__main__' else '',
    long_description_content_type='text/markdown',
    author='PyRadio Developers',
    license='GPL-3.0-or-later',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'PyGObject>=3.40.0',
    ],
    entry_points={
        'console_scripts': [
            'pyradio=pyradio.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
