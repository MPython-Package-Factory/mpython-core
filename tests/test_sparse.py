import numpy as np
import pytest

from mpython import utils
from mpython.sparse_array import SparseArray


def _dense(x):
    if hasattr(x, "todense"):
        return np.asarray(x.todense())
    return np.asarray(x)


def _sparse_dict(values):
    return {
        "type__": "sparse",
        "size__": np.array([[2, 3]]),
        "indices__": np.array([[1, 1], [2, 3]]),
        "values__": values,
    }


EXPECTED = np.array([[1.0, 0, 0], [0, 0, 2.0]])


@pytest.fixture(params=["scipy", "dense"])
def backend(request):
    if request.param == "scipy":
        pytest.importorskip("scipy")
    elif utils.sparse is not None:
        pytest.skip("dense fallback is only used when scipy is missing")
    return request.param


def test_sparse_numpy_values(backend, fake_remote):
    out = SparseArray._from_runtime(_sparse_dict(np.array([[1.0], [2.0]])))
    assert out.shape == (2, 3)
    np.testing.assert_array_equal(_dense(out), EXPECTED)


def test_sparse_numpy_int_values(backend, fake_remote):
    out = SparseArray._from_runtime(
        _sparse_dict(np.array([1, 2], dtype=np.int32))
    )
    assert out.dtype == np.int32
    np.testing.assert_array_equal(_dense(out), EXPECTED)


def test_sparse_numpy_scalar(backend, fake_remote):
    d = {
        "type__": "sparse",
        "size__": np.array([[2, 2]]),
        "indices__": np.array([[2, 1]]),
        "values__": np.float32(5.0),
    }
    out = SparseArray._from_runtime(d)
    assert out.dtype == np.float32
    np.testing.assert_array_equal(_dense(out), [[0, 0], [5.0, 0]])


def test_sparse_float(backend, no_runtime):
    d = {
        "type__": "sparse",
        "size__": [[2, 2]],
        "indices__": [[1, 2]],
        "values__": 5.0,
    }
    out = SparseArray._from_runtime(d)
    assert out.dtype == np.float64
    np.testing.assert_array_equal(_dense(out), [[0, 5.0], [0, 0]])


def test_sparse_matlab_values(backend, fake_matlab):
    d = _sparse_dict(fake_matlab.uint32([[1], [2]]))
    out = SparseArray._from_runtime(d)
    assert out.dtype == np.uint32
    np.testing.assert_array_equal(_dense(out), EXPECTED)
