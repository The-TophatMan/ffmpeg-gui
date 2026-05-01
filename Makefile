DOCS = docs
PYTHONPATH = src
QT_QPA_PLATFORM = offscreen

.PHONY: all check-style fix-style check-type unittest test-coverage create-docs clean

all: check-style check-type test-coverage create-docs clean

check-style:
	flake8 src tests

fix-style:
	autopep8 --in-place --recursive --aggressive --aggressive src tests

check-type:
	PYTHONPATH=$(PYTHONPATH) mypy --disallow-untyped-defs --strict src tests

unittest:
	QT_QPA_PLATFORM=$(QT_QPA_PLATFORM) PYTHONPATH=$(PYTHONPATH) pytest -v tests/

test-coverage:
	QT_QPA_PLATFORM=$(QT_QPA_PLATFORM) PYTHONPATH=$(PYTHONPATH) pytest -v --color=yes --cov=src --cov-report term-missing --cov-report=html:$(DOCS)/htmlcov tests/

create-docs:
	mkdir -p $(DOCS)
	PYTHONPATH=$(PYTHONPATH) pdoc --output-dir $(DOCS)/docs src/

clean:
	rm -rf `find . -type d -name __pycache__`
	rm -rf `find . -type d -name .pytest_cache`
	rm -rf `find . -type d -name .mypy_cache`
	rm -rf `find . -type d -name .hypothesis`
	rm -rf `find . -name .coverage`
	rm -rf $(DOCS)/htmlcov