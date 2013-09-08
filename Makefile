SHELL := /bin/bash

release:
	python setup.py register sdist upload
	python setup.py register bdist_wheel upload
