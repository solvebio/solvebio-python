# Note: This makefile include remake-style target comments.
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

PHONY=check clean dist distclean test clean_pyc lint
GIT2CL ?= git2cl
PYTHON ?= python
PYTHON3 ?= python3
RM      ?= rm
LINT    = flake8

#: the default target - same as running "check"
all: check

#: Run all tests
check:
	$(PYTHON) ./setup.py test
#	$(PYTHON3) ./setup.py test

#: Clean up temporary files and .pyc files
clean: clean_pyc
	$(PYTHON) ./setup.py $@

#: Create source (tarball) and binary (egg) distribution
dist:
	$(PYTHON) ./setup.py sdist bdist

#: Remove .pyc files
clean_pyc:
	$(RM) -f */*.pyc */*/*.pyc

#: Create source tarball
sdist:
	$(PYTHON) ./setup.py sdist

#: Style check. Set env var LINT to pyflakes, flake, or flake8
lint:
	$(LINT)

#: Create binary egg distribution
bdist_egg:
	$(PYTHON) ./setup.py bdist_egg

# It is too much work to figure out how to add a new command to distutils
# to do the following. I'm sure distutils will someday get there.
DISTCLEAN_FILES = build dist *.egg-info *.pyc *.so py*.py

#: Remove ALL derived files
distclean: clean
	-rm -fr $(DISTCLEAN_FILES) || true

#: Install package locally
install:
	$(PYTHON) ./setup.py install

#: Same as 'check' target
test: check

#: Run a specific unit test, eg test-sample runs solvebio.test.test_sample
test-%:
	python -m unittest solvebio.test.$(subst test-,test_,$@)

changelog:
	github_changelog_generator

.PHONY: $(PHONY)
