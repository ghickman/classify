from setuptools import find_packages, setup


setup(
    name='classify',
    version='0.1',
    description='Render a classes collated members using MRO',
    long_description=open('README.rst').read(),
    author='George Hickman',
    author_email='george@ghickman.co.uk',
    license='MIT',
    packages=find_packages(),
    entry_points={'console_scripts': ['classify=classify.main:run']},
    install_requires=['jinja2>=2.7'],
    include_package_data=True,
)
