import sys
import types

import pytest


class FakeMatlabObject:
    """Stands in for `matlab.object` (in-process runtime)."""


class FakeRemoteHandle:
    """Stands in for `matlab_runtime.remote.RemoteHandle`."""


def _make_fake_matlab():
    matlab = types.ModuleType("matlab")
    matlab.object = FakeMatlabObject
    for name in ("double", "single", "logical", "uint64", "uint32",
                 "uint16", "uint8", "int64", "int32", "int16", "int8"):
        setattr(matlab, name, type(name, (list,), {}))
    return matlab


def _make_fake_remote():
    remote = types.ModuleType("matlab_runtime.remote")
    remote.RemoteHandle = FakeRemoteHandle
    remote.is_matlab_object = (
        lambda x: isinstance(x, (FakeRemoteHandle, FakeMatlabObject))
    )
    return remote


@pytest.fixture
def no_runtime(monkeypatch):
    """Neither `matlab` nor `matlab_runtime.remote` is available."""
    # A None entry in sys.modules makes `import matlab` raise ImportError
    monkeypatch.setitem(sys.modules, "matlab", None)
    monkeypatch.delitem(sys.modules, "matlab_runtime.remote", raising=False)


@pytest.fixture
def fake_matlab(no_runtime, monkeypatch):
    """Old matlab-runtime: `matlab` importable in-process, no remote."""
    matlab = _make_fake_matlab()
    monkeypatch.setitem(sys.modules, "matlab", matlab)
    return matlab


@pytest.fixture
def fake_remote(no_runtime, monkeypatch):
    """New matlab-runtime in remote mode: `matlab` NOT importable."""
    remote = _make_fake_remote()
    monkeypatch.setitem(sys.modules, "matlab_runtime.remote", remote)
    return remote
