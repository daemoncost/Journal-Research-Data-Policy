# Run python test suite based on `unittest`
test:
	python3 -m unittest discover src/tests/

 # Run test with code coverage report
test-cov:
	pytest --cov=src/daemon_analysis_tools/ --cov-report=html
	firefox htmlcov/index.html

 # Install production version in active environment
install:
	pip install -e .

 # Install developer version in active environment
install-dev:
	pip install -e .[dev]
