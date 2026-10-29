"""Narrow import-only compatibility for legacy Fairseq dataclass defaults.

Python 3.11 rejects unhashable dataclass instances as field defaults, which
fairseq==0.12.2 and its Hydra dependency use. This does not replace or emulate the pretrained neural
model. It temporarily fixes only fairseq.* and hydra.conf.* class declarations during the
official model import. Python 3.10 never enters this compatibility path.
"""

from __future__ import annotations
from contextlib import contextmanager
import copy
import dataclasses
import sys


@contextmanager
def fairseq_py311_dataclass_context():
    if sys.version_info < (3, 11):
        yield
        return
    original = dataclasses._get_field

    def guarded_get_field(cls, name, field_type, kw_only):
        if cls.__module__.startswith("fairseq.") or cls.__module__ == "hydra.conf" or cls.__module__.startswith("hydra.conf."):
            value = cls.__dict__.get(name, dataclasses.MISSING)
            if value is not dataclasses.MISSING and dataclasses.is_dataclass(value) and not isinstance(value, type):
                dataclasses_field = dataclasses.field(
                    default_factory=lambda template=value: copy.deepcopy(template)
                )
                setattr(cls, name, dataclasses_field)
        return original(cls, name, field_type, kw_only)

    dataclasses._get_field = guarded_get_field
    try:
        yield
    finally:
        dataclasses._get_field = original
