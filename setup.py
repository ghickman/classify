from setuptools import find_packages, setup


setup(
    name='classy',
    version='0.1',
    author='George Hickman',
    author_email='george@ghickman.co.uk',
    license='MIT',
    packages=find_packages(),
    entry_points={'console_scripts': ['classy=classy.main:run']},
)
