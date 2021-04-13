.PHONY: help clean dev docs package test

help:
	@echo "This project assumes that an active Python virtualenv is present."
	@echo "The following make targets are available:"
	@echo "	 dev 	install all deps for dev env"
	@echo "  docs	create pydocs for all relveant modules"
	@echo "	 test	run all tests with coverage"

clean:
	rm -rf dist/*

dev:
	# pip install pipenv
	pipenv install twine wagtail tpot wagtail-generic-chooser coverage

docs:
	$(MAKE) -C docs html

package:
	python setup.py sdist bdist_wheel

test:
	coverage run -m unittest discover
	coverage html
