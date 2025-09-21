# Copilot Coding Agent Onboarding Instructions

## High-Level Repository Overview

- **Purpose**: This repository implements a Django-based quotas management library, designed to provide quota, plan, and
  account management for Django applications.
- **Type**: Python library, intended for integration with Django projects.
- **Languages/Frameworks**: Python 3.11/3.12, Django 5.x, Poetry for dependency management.
- **Size**: Medium-sized, with a modular structure and clear separation between core logic, database implementations,
  and utilities.

## Build, Test, and Validation Instructions

### Environment Setup

- **Python Version**: Requires Python 3.12 (minimum 3.11, as per `pyproject.toml`).
- **Dependency Management**: Uses Poetry (version 2.x recommended).
- **Virtual Environment**: By default, uses a `venv` directory. Most scripts and Makefile targets expect the virtual
  environment to be activated unless `NO_VENV` is set.

#### Steps to Bootstrap

1. **Setup Project**:
    - Run: `make setup`
    - This will:
        - Create and activate the virtual environment (unless `NO_VENV` is set).
        - Install dependencies via Poetry.
        - Install pre-commit hooks.

### Code style

- **REQUIRED** Always write strictly typed code with type hints. The project uses mypy with strict settings.
- **REQUIRED** Always use type hints for function signatures and variable declarations.
- **REQUIRED** Use __all__ to define public API in modules.
- Docstrings:
   - **REQUIRED** Follow PEP257 for docstrings, define parameters in reST format, do not define `:type` and `:rtype`
     as we already have typings.
   - Whenever possible generate documentation strings for public functions/classes/methods. Never define docstrings 
     for modules unless you were specifically asked to do so.
- Logging:
    - Use logging instead of print statements. Prefer adding LogMixin to class and use `self.log.info(....)`.
    - When makes sense add additional context to log messages (e.g. user id, object id) using `extra={}` parameter.
    - Avoid f-strings for log messages; use lazy formatting with `%s` placeholders.

- Use `pathlib.Path` for filesystem paths instead of string paths.
- General style: follow PEP8 as enforced by ruff and flake8.
- When possible generate unit tests when adding new functionality or fixing bugs.
- Add __all__ to modules to define public API.

### Build and Lint

- **Linting**: Run `make lint` (if defined) or use pre-commit hooks directly:
    - `pre-commit run --all-files`
    - Linting uses `ruff`, `yamllint`, and other pre-commit hooks as defined in `.pre-commit-config.yaml`.

- **Formatting**: Use `ruff` for code formatting and import sorting.

### Testing

- **Test Framework**: Uses `pytest` (see `pyproject.toml` for plugins).
- **Run Tests**: After setup, run:
  ```
  poetry run pytest
  ```
  or, if using the virtual environment:
  ```
  source venv/bin/activate
  pytest
  ```

### Pre-commit and Validation

- **Pre-commit Hooks**: Configured in `.pre-commit-config.yaml`. Always run `pre-commit run --all-files` before
  committing.
- **CI/CD**: No GitHub Actions workflows are present, so local validation is critical.
- **Manual Validation**: Run `make pre_commit` to execute all pre-commit hooks and linting.

### Other Scripts

- **apply-copyright.sh**: Applies license headers to changed Python files.
- **ensure-dependencies.sh**: Checks for required system dependencies.

## Project Layout and Key Files

- **Root Files**:
    - `Makefile`: Main entry for setup, dependency management, and validation.
    - `pyproject.toml`: Project metadata, dependencies, and tool configuration.
    - `poetry.lock`: Locked dependency versions.
    - `.pre-commit-config.yaml`, `.yamllint.yaml`: Linting and pre-commit configuration.
    - `development/`: Contains utility scripts for copyright and dependency checks.

- **Source Code**: Located in `src/django_quotas/`
    - `__init__.py`, `apps.py`, `config.py`, `models.py`, `utils.py`: Core logic.
    - `base/`: Abstract base classes and DTOs.
    - `impl_db/`: Database-specific implementations.
    - `migrations/`: Django migration files.

## Explicit Validation Steps

- Always run `make setup` before any build or test.
- Always activate the virtual environment or set `NO_VENV=1` if you wish to skip it.
- Always run `make` before committing.
- Run tests with `pytest` after making changes.

## Common pitfalls & gotchas (save time by avoiding these)

- Poetry version mismatch: Makefile expects `poetry@2` (pipx suffix). If you don't use pipx, run commands as
  `POETRY=poetry make <target>` after upgrading your system poetry to v2.

## Additional Notes

- Trust these instructions for build, test, and validation. Only search for additional information if these steps fail
  or are incomplete.

