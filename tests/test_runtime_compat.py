import numpy as np
import pytest

from mpython import Runtime
from mpython.array import Array
from mpython.core import MatlabType
from mpython.matlab_function import MatlabFunction
from mpython.utils import _is_matlab_object, _matlab_array_types

from conftest import FakeMatlabObject, FakeRemoteHandle


class FakeEndpoint:
    def __init__(self):
        self.calls = []

    def mpython_endpoint(self, fn, *args, **kwargs):
        self.calls.append((fn, args, kwargs))
        return 42.0


def make_runtime():
    endpoint = FakeEndpoint()

    class FakeRuntime(Runtime):
        verbose = False

        @classmethod
        def _import_runtime(cls):
            return endpoint

    return FakeRuntime, endpoint


# --- old path: in-process `matlab` -----------------------------------------

def test_old_matlab_object(fake_matlab):
    obj = FakeMatlabObject()
    assert _is_matlab_object(obj)
    out = MatlabType.from_any(obj)
    assert isinstance(out, MatlabFunction)
    assert MatlabType._to_runtime(out) is obj


def test_old_uint32_dtype(fake_matlab):
    types = _matlab_array_types()
    assert types[fake_matlab.uint32] is np.uint32
    assert types[fake_matlab.uint64] is np.uint64


def test_old_function_call(fake_matlab):
    runtime, endpoint = make_runtime()
    obj = FakeMatlabObject()
    fn = MatlabType.from_any(obj, _runtime=runtime)
    assert fn(1.0) == 42.0
    assert endpoint.calls[0][0] is obj


# --- new path: out-of-process runtime, no `matlab` --------------------------

def test_remote_handle(fake_remote):
    handle = FakeRemoteHandle()
    assert _is_matlab_object(handle)
    assert _matlab_array_types() == {}
    runtime, endpoint = make_runtime()
    fn = MatlabType.from_any(handle, _runtime=runtime)
    assert isinstance(fn, MatlabFunction)
    assert MatlabType._to_runtime(fn) is handle
    assert fn(1.0, x=2.0) == 42.0
    called, args, kwargs = endpoint.calls[0]
    assert called is handle
    assert args == (1.0,)
    assert kwargs == {"x": 2.0}


def test_remote_handle_not_treated_as_iterable(fake_remote):
    class IterableHandle(FakeRemoteHandle):
        def __iter__(self):
            raise AssertionError("handle must not be iterated")

    assert isinstance(MatlabType.from_any(IterableHandle()), MatlabFunction)


def test_remote_handle_passed_back_as_argument(fake_remote):
    runtime, endpoint = make_runtime()
    handle = FakeRemoteHandle()
    fn = MatlabType.from_any(handle, _runtime=runtime)
    runtime.call("feval", fn, np.ones(3))
    called, args, _ = endpoint.calls[0]
    assert called == "feval"
    assert args[0] is handle


def test_remote_numpy_results(fake_remote):
    runtime, _ = make_runtime()
    out = MatlabType._from_runtime(np.arange(6.0).reshape(1, 6), runtime)
    assert isinstance(out, Array)
    assert out.shape == (6,)
    out = MatlabType._from_runtime(np.int32(3), runtime)
    assert isinstance(out, Array)
    assert out.dtype == np.int32


def test_remote_cell_and_struct(fake_remote):
    runtime, _ = make_runtime()
    handle = FakeRemoteHandle()
    cell = MatlabType._from_runtime(
        {"type__": "cell", "size__": np.array([[1, 2]]),
         "data__": [np.ones((1, 2)), handle]},
        runtime,
    )
    assert isinstance(cell[1], MatlabFunction)
    struct = MatlabType._from_runtime(
        {"type__": "structarray", "size__": np.array([[1, 1]]),
         "data__": [{"a": np.ones((1, 2)), "f": handle}]},
        runtime,
    )
    assert isinstance(struct[0]["f"], MatlabFunction)


# --- neither available ------------------------------------------------------

def test_no_runtime_plain_values(no_runtime):
    assert not _is_matlab_object(object())
    assert _matlab_array_types() == {}
    assert isinstance(MatlabType.from_any(1.0), Array)
    assert isinstance(MatlabType.from_any(np.ones(3)), Array)
    assert MatlabType.from_any("abc") == "abc"
    assert MatlabType.from_any(None) is None


def test_no_runtime_unknown_object(no_runtime):
    with pytest.raises(TypeError):
        MatlabType.from_any(object())
    with pytest.raises(TypeError):
        MatlabFunction(object(), None)


def test_matlab_without_remote_rejects_handle(fake_matlab):
    with pytest.raises(TypeError):
        MatlabType.from_any(FakeRemoteHandle())
