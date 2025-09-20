VIRTUAL_ENV_PATH=venv
SKIP_VENV="${NO_VENV}"
SHELL := /bin/bash
PYTHON := python3.12
SRC_ROOT := ./src
ROOT_PACKAGE := django_quotas
.DEFAULT_GOAL := pre_commit
POETRY := poetry@2

FORMAT_PATH := $(SRC_ROOT)
LINT_PATH := $(SRC_ROOT)
MYPY_PATH := $(SRC_ROOT)

pre_commit: pre_commit_hook lint

UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S),Darwin)
    SED_COMMAND := gsed
else
    SED_COMMAND := sed
endif

pre_commit_hook:
	@( \
		if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
		pre-commit run --all --hook-stage=commit; \
	)

verify-prerequisites:
	@(development/ensure-dependencies.sh)

setup: verify-prerequisites venv deps
	@( \
		if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
		pre-commit install; \
		echo "DONE: setup"; \
	)

.PHONY: deps
deps:
	@( \
		set -e; \
		if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
		$(POETRY) install --all-extras --no-root; \
	)
	
deps-lock:
	@( \
		if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
		$(POETRY) lock; \
	)
	
.PHONY: deps-sync
deps-sync:
	@set -e; \
	$(call activate_venv) \
	echo "Syncing dependencies..."; \
	$(POETRY) sync --all-extras --no-root --with "$(POETRY_GROUPS)"; \
	echo "DONE: all dependencies are synchronized";

.PHONY: deps-update
deps-update:
	@( \
		if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
		$(POETRY) lock; \
	)
	
# Update a specific dependency
.PHONY: deps-update-dep
deps-update-dep:
	@( \
		$(call activate_venv) \
		set -e; \
		echo "Updating dependency $(DEPENDENCY)..."; \
		$(POETRY) update $(DEPENDENCY) --with "$(POETRY_GROUPS)"; \
		echo "DONE: dependency $(DEPENDENCY) is updated"; \
	)

# Show dependencies tree
.PHONY: deps-tree
deps-tree:
	@( \
		if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
		$(POETRY) show --tree; \
	)

.PHONY: venv
venv:
	@( \
	  	set -e; \
		  $(PYTHON) -m venv $(VIRTUAL_ENV_PATH); \
		  source ./venv/bin/activate; \
	)
	
.PHONY: copyright
copyright:
	@( \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Applying copyright..."; \
       for p in $(FORMAT_PATH); do \
       	 licenseheaders -t ./development/copyright.tmpl -E ".py" -cy -d $$p; \
       done; \
       echo "DONE: copyright"; \
    )
    

ruff-fix-pyupgrade:
	@( \
	   $(call activate_venv) \
       echo "Applying pyupgrade..."; \
       ruff check --select UP --fix; \
       echo "DONE: pyupgrade"; \
    )

.PHONY: ruff-fix-pyupgrade-unsafe
ruff-fix-pyupgrade-unsafe:
	@( \
	   $(call activate_venv) \
	   echo "Applying pyupgrade..."; \
	   ruff check --select UP --fix --unsafe-fixes; \
	   echo "DONE: pyupgrade"; \
	)

ruff-format:
	@( \
	   $(call activate_venv) \
	   echo "Running Ruff code formatter..."; \
	   ruff format $(FORMAT_PATH); \
	   echo "DONE: Ruff"; \
	)

ruff-format-check:
	@( \
	   $(call activate_venv) \
	   echo "Running Ruff format check..."; \
	   ruff format --diff $(FORMAT_PATH) || exit 1; \
	   echo "DONE: Ruff"; \
	)

ruff-import-sort:
	@( \
	   $(call activate_venv) \
	   echo "Running Ruff import sort..."; \
	   ruff check --select I --fix; \
	   echo "DONE: Ruff"; \
	)

ruff-import-sort-check:
	@( \
	   $(call activate_venv) \
	   echo "Running Ruff import sort..."; \
	   ruff check --select I || exit 1; \
	   echo "DONE: Ruff"; \
	)

ruff-lint:
	@( \
	   $(call activate_venv) \
	   echo "Running Ruff link..."; \
	   ruff check $(LINT_PATH) || exit 1; \
	   echo "DONE: Ruff"; \
	)

format: ruff-import-sort ruff-format
check-format: ruff-import-sort-check ruff-format-check

.PHONY: mypy
mypy:
	@( \
       set -e; \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Running MyPy checks..."; \
       mypy $(MYPY_PATH); \
       echo "DONE: MyPy"; \
    )

lint: mypy check-format

.PHONY: build
build:
	@( \
		echo "Building packages"; \
		set -e; \
		if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
		rm -rf dist/*; \
		$(POETRY) build; \
		echo "DONE: Building packages"; \
	)
	
.PHONY: build
publish: build
	@( \
		echo "Publishing packages"; \
		set -e; \
		if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
		$(POETRY) publish; \
		echo "DONE: Publishing packages"; \
	)
	
.PHONY: coverage
coverage:
	@( \
		echo "Running coverage"; \
		set -e; \
		if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
		coverage run --source $(SRC_ROOT)/$(ROOT_PACKAGE) -m pytest; \
		coverage html; \
		echo "DONE: Coverage"; \
	)

.PHONY: test
test:
	@( \
		echo "Running tests"; \
		set -e; \
		if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
		echo pytest -v --cov-report term-missing --cov=$(SRC_ROOT)/$(ROOT_PACKAGE); \
		pytest -v --html=test-report.html --self-contained-html; \
		echo "DONE: Tests"; \
	)

.PHONY: changelog
changelog:
	@( \
		echo "Generating changelog"; \
		set -e; \
		if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
		cz changelog --incremental; \
		echo "DONE: Changelog"; \
	)

.PHONY: print-changelog
print-changelog:
	@( \
		if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
		cz changelog --dry-run --incremental; \
	)

.PHONY: release
release:
	@( \
		echo "Preparing release"; \
		set -e; \
		if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
		cz bump --changelog; \
		echo "DONE: Preparing release"; \
	)

.PHONY: print-version
print-version:
	@( \
		if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
		cz version --project; \
	)

.PHONY: get-version
get-version: set-meta-info
	@echo $(VERSION)

.PHONY: get-semver-version
get-semver-version: set-meta-info
	@echo $(SEMVER)
