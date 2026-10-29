"""Ensure Fairseq-only Python3.11 compatibility restores stdlib behavior."""
from __future__ import annotations
import dataclasses
import sys
import pytest
from indicwrite.compat_py311 import fairseq_py311_dataclass_context


def test_scoped_fairseq_default_factory_and_restore():
    if sys.version_info < (3, 11):
        pytest.skip("Python 3.10 allows these legacy defaults")
    original = dataclasses._get_field

    @dataclasses.dataclass
    class Child:
        values: list[int] = dataclasses.field(default_factory=list)

    template = Child()
    namespace = {"__module__": "fairseq.dataclass.configs", "__annotations__": {"common": Child}, "common": template}

    with fairseq_py311_dataclass_context():
        Config = type("Config", (), namespace)
        Config = dataclasses.dataclass(Config)
        left, right = Config(), Config()
        left.common.values.append(7)
        assert right.common.values == []
    assert dataclasses._get_field is original


def test_non_fairseq_types_not_modified():
    @dataclasses.dataclass
    class Child:
        value: int = 0
    class Normal:
        value: Child = Child()
    Normal.__annotations__ = {"value": Child}
    with fairseq_py311_dataclass_context():
        # The unrelated dataclass still rejects mutable defaults on Python 3.11+
        import sys, pytest
        if sys.version_info >= (3, 11):
            with pytest.raises(ValueError, match="mutable default"):
                dataclasses.dataclass(Normal)


def test_exact_hydra_conf_module_is_covered():
    if sys.version_info < (3, 11):
        pytest.skip("Python 3.11+ legacy Hydra compatibility only")
    @dataclasses.dataclass
    class Nested:
        x: int = 0
    origin = dataclasses._get_field
    Config = type(
        "MockHydraConfig", (),
        {"__module__": "hydra.conf",
         "__annotations__": {"job": Nested},
         "job": Nested()},
    )
    with fairseq_py311_dataclass_context():
        Decorated = dataclasses.dataclass(Config)
        assert Decorated().job == Nested()
    assert dataclasses._get_field is origin
