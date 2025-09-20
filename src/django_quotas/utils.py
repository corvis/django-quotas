#
#  Copyright 2025 by Dmitry Berezovsky, MIT License
#
import datetime
from typing import cast

from django.apps import apps
from django.db import models
from django.utils.module_loading import import_string


def get_model_by_name(model_name: str) -> type[models.Model]:
    try:
        return cast(type[models.Model], apps.get_model(*model_name.split(".", 1)))
    except LookupError:
        raise ValueError(f"Model {model_name} not found")


def get_class_by_name(dotted_path: str) -> type:
    return import_string(dotted_path)


def datetime_now() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.UTC)
