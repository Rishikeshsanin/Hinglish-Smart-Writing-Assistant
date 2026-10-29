"""Unit test for cold-load concurrency: fake modules, no real neural inference."""

import contextlib
import importlib
import sys
import threading
import time
import types
from concurrent.futures import ThreadPoolExecutor


def test_simultaneous_cold_requests_initialize_one_model(monkeypatch):
    import indicwrite.engine as backend

    count = 0
    count_lock = threading.Lock()

    def fake_xlit(*args, **kwargs):
        nonlocal count
        with count_lock:
            count += 1
        time.sleep(0.025)
        return object()

    fake_torch = types.ModuleType("torch")
    fake_torch.serialization = types.SimpleNamespace(
        safe_globals=lambda globals_list: contextlib.nullcontext()
    )
    fake_pkg = types.ModuleType("ai4bharat")
    fake_pkg.__path__ = []
    fake_sub = types.ModuleType("ai4bharat.transliteration")
    fake_sub.XlitEngine = fake_xlit
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    monkeypatch.setitem(sys.modules, "ai4bharat", fake_pkg)
    monkeypatch.setitem(sys.modules, "ai4bharat.transliteration", fake_sub)

    backend._load_indicxlit_cached.cache_clear()
    try:
        with ThreadPoolExecutor(max_workers=6) as executor:
            models = list(executor.map(lambda _: backend.load_indicxlit(), range(6)))
        assert count == 1
        assert all(m is models[0] for m in models)
    finally:
        backend._load_indicxlit_cached.cache_clear()
