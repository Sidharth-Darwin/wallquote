import setuptools
from setuptools import setup, find_packages

setup(
    name='wallquote',
    version='0.1.0',
    author='Sidharth D',
    author_email='zurajanaikatsurada1222@gmail.com',
    description='A command-line tool to generate quote wallpapers with customizable backgrounds.',
    long_description=open('README.md').read(),
    url='https://github.com/Sidharth-Darwin/wallquote',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'wallquote=wallquote.main:main'
        ]
    },
    install_requires=['Pillow', 'argparse']
)