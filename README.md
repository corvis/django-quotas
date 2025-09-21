# Django Quotas

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A robust, extensible quotas and plan management library for Django applications. This package provides a flexible
framework for defining, assigning, and tracking quotas (limits) for users, accounts, or any custom entity in your Django
project.

## Features

- Strictly typed, modular codebase with clear separation between core logic, database implementations, and utilities
- Abstract base classes and DTOs for easy extension
- Default and database-specific implementations provided
- Supports hourly, daily, monthly, and total quota buckets
- Pluggable quota models and account models via Django settings
- Utilities for dynamic model/class loading
- Designed for integration with Django 5.x and Python 3.11/3.12

## Installation

```sh
pip install django-quotas
```

Or, if using Poetry:

```sh
poetry add django-quotas
```

## Quickstart

1. **Add to `INSTALLED_APPS` (to use standard Quota model and database storage backend):**

   ```python
   INSTALLED_APPS = [
       # ...
       'django_quotas',
       'django_quotas.defaults',
       'django_quotas.backends.db'
   ]
   ```

2. **Configure (optional):**
   You can override default models and table prefixes in your Django settings:

   ```python
   DJANGO_QUOTAS_TABLE_PREFIX = 'myquotas'  # default: 'django_quotas'
   DJANGO_QUOTAS_QUOTA_MODEL_NAME = 'myapp.MyQuotaModel'  # default: 'django_quotas.defaults.QuotaModel'
   DJANGO_QUOTAS_RELATED_ACCOUNT_MODEL = 'auth.User'  # or your custom user/account model
   ```

3. **Run migrations:**

   ```sh
   python manage.py migrate
   ```

4. **Assign quotas:**
   Use the provided models or extend them to assign quotas to users/accounts.

## Configuration

All configuration is done via Django settings. See `src/django_quotas/config.py` for all available options.

- `DJANGO_QUOTAS_TABLE_PREFIX`: Prefix for all quota-related tables.
- `DJANGO_QUOTAS_QUOTA_MODEL_NAME`: Dotted path to the quota model.
- `DJANGO_QUOTAS_RELATED_ACCOUNT_MODEL`: Dotted path to the related account/user model.

## API Overview

### Core Data Structures

- `QuotaBucket`: Enum for supported buckets (`hourly`, `daily`, `monthly`, `total`)
- `ValuePerBucket`: Dataclass holding quota values for each bucket
- `QuotaStatus`, `QuotaStats`, `QuotaUseForBucket`, `Quota`, `QuotaUsage`: DTOs for quota management

### Abstract Service

- `QuotaService`: Abstract base class for quota management logic
- `QuotaExceededError`: Exception raised when a quota is exceeded

### Models

- `BaseQuotaModel`: Abstract base model for quotas
- `DefaultQuotaModel`: Default implementation for quota assignment
- `QuotaUsageModel`: Tracks quota usage per account/feature/time

### Utilities

- `get_model_by_name(model_name: str)`: Load a Django model by dotted name
- `get_class_by_name(dotted_path: str)`: Import a class by dotted path
- `datetime_now()`: Get current UTC datetime

## Extending & Customization

- **Custom Quota Models:** Inherit from `BaseQuotaModel` and register via settings.
- **Custom Account Models:** Set `DJANGO_QUOTAS_RELATED_ACCOUNT_MODEL` to your user/account model.
- **Custom Quota Logic:** Implement your own `QuotaService` subclass.

## Contributing

Contributions are welcome! If you have ideas or find bugs, feel free to open an issue or submit a pull request.

Please:

- Follow PEP8 and project code style (see `.github/copilot-instructions.md`)
- Use type hints and docstrings (PEP257)
- Run `make setup` and `make` before submitting a PR
- Add unit tests for new features or bugfixes

## Credits

* Dmitry Berezovsky (@corvis) - Author and maintainer

## License

Django Quotas is licensed under the MIT License. See LICENSE for more details.

---

For more details, see the source code in `src/django_quotas/` and the included docstrings.
