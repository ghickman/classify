from setuptools import find_packages, setup


setup(
    name='classify',
    version='0.5.0',
    description='Generate concrete Class documentation for Python Classes.',
    long_description=open('README.rst').read(),
    author='George Hickman',
    author_email='george@ghickman.co.uk',
    url='http://github.com/ghickman/classify',
    license='MIT',
    packages=find_packages(),
    entry_points={'console_scripts': ['classify=classify.main:run']},
    install_requires=['jinja2>=2.7'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Documentation',
    ],
)
