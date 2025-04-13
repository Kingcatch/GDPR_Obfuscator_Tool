#################################################################################
# Makefile to build the project using python -m venv (bootcamp-friendly version)
#################################################################################

PROJECT_NAME = gdpr_obfuscator_tool
REGION = eu-west-2
PYTHON_INTERPRETER = python
WD = $(shell pwd)
PYTHONPATH = $(WD)
SHELL := /bin/bash
PIP := pip

## Create python virtual environment
create-environment:
	@echo ">>> Creating environment for: $(PROJECT_NAME)..."
	@$(PYTHON_INTERPRETER) --version
	@echo ">>> Setting up venv with python -m venv..."
	$(PYTHON_INTERPRETER) -m venv venv
	@echo ">>> Virtual environment created at ./venv"

# Define utility variable to help calling Python from the virtual environment
ACTIVATE_ENV := source venv/bin/activate

# Execute Python-related functionalities within the virtual environment
define execute_in_env
	$(ACTIVATE_ENV) && $1
endef

################################################################################################################
# Set Up
setupreq:
	$(call execute_in_env, $(PIP) install -r ./requirements.txt)

bandit:
	$(call execute_in_env, $(PIP) install bandit)

safety:
	$(call execute_in_env, $(PIP) install safety)

black:
	$(call execute_in_env, $(PIP) install black)

coverage:
	$(call execute_in_env, $(PIP) install coverage)

## Install all dev requirements
dev-setup: setupreq bandit safety black coverage

################################################################################################################
# Build / Run

## Run the security test (bandit only for now)
security-test:
	$(call execute_in_env, bandit -lll */*.py *c/*/*.py)

## Run the black code formatting check
run-black:
	$(call execute_in_env, black ./src/*.py ./test/*.py)

## Run unit tests with coverage
unit-test:
	$(call execute_in_env, PYTHONPATH=$(PYTHONPATH) coverage run --source=./src/ -m pytest -vv)
	$(call execute_in_env, PYTHONPATH=$(PYTHONPATH) coverage report)

## Run all quality checks
run-checks: security-test run-black unit-test
