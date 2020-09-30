from setuptools import setup

setup(
    name='ujlaser',
    version='0.9',
    description='Library to control a Quantum Composers MicroJewel Laser.',
    url='https://github.com/nschaffin/OASIS-Laser',
    author='Miles Green, Noah Chaffin, Tyler Sengia',
    author_email='tylersengia@gmail.com',
    license='The Unlicense',
    packages=['ujlaser'],
    install_requires=['pyserial>=3.0'],
    classifiers=['Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5'],
)
