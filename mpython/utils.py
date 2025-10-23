import importlib

import numpy as np

# If scipy is available, convert matlab sparse matrices scipy.sparse
# otherwise, convert them to dense numpy arrays
try:
    from scipy import sparse
except (ImportError, ModuleNotFoundError):
    sparse = None

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


class DelayedImportElement:

    def __init__(self, name, import_path=None):
        self.name = name
        self.import_path = import_path

    def _import(self):
        assert self.import_path
        import_path = self.import_path
        try:
            var = importlib.import_module(import_path)
        except ModuleNotFoundError as e:
            try:
                *import_path, var = import_path.split('.')
                import_path = '.'.join(import_path)
                mod = importlib.import_module(import_path)
                var = getattr(mod, var)
            except (ModuleNotFoundError, AttributeError):
                raise e
        return var

    def __get__(self, instance, owner):
        assert instance is None
        imported = self._import()
        setattr(owner, self.name, imported)
        return imported


class DelayedImport:
    """A utility to delay the import of modules or variables.

    Until they are imported, import paths are wrapped in a
    `DelayedImportElement` object. The first time an element is accessed,
    it triggers the underlying import and assign the imported module or
    object into the `DelayedImport` child class, while getting rid
    of the `DelayedImportElement` wrapper. Thereby, the next time the
    element is accessed, the module is directly obtained. This strategy
    minimizes overhead on subsequent calls (no need to test whether
    the module has already been imported or not).

    Example
    -------
    ```python
    # module_with_definitions.py
    class _imports(DelayedImport):
        Array = 'mpython.array.Array'
        Cell = 'mpython.cell.Cell'

    def foo():
        Array = _imports.Array
        Cell = _imports.Cell
    ```
    """
    def __init_subclass__(cls):
        for key, val in cls.__dict__.items():
            if key.startswith("__"):
                continue
            setattr(cls, key, DelayedImportElement(key, val))


def _import_matlab():
    """
    Delayed matlab import.

    This allows to only complain about the lack of a runtime if we
    really use the runtime. Note that most of the MPython types do
    not need the runtime.
    """
    try:
        import matlab
    except (ImportError, ModuleNotFoundError):
        matlab = None
    return matlab


def _copy_if_needed(out, inp, copy=None) -> np.ndarray:
    """Fallback implementation for asarray(*, copy: bool)"""
    if (
        out is not None
        and isinstance(inp, np.ndarray)
        and np.ndarray.view(out, np.ndarray).data
        != np.ndarray.view(inp, np.ndarray).data
    ):
        if copy:
            out = np.copy(out)
        elif copy is False:
            raise ValueError("Cannot avoid a copy")
    return out


def _spcopy_if_needed(out, inp, copy=None):
    """Fallback implementation for asarray(*, copy: bool)"""
    if (
        out is not None
        and isinstance(inp, sparse.spmatrix)
        and out.data.data != inp.data.data
    ):
        if copy:
            out = out.copy()
        elif copy is False:
            raise ValueError("Cannot avoid a copy")
    return out


def _matlab_array_types():
    """Return a mapping from matlab array type to numpy data dtype."""
    matlab = _import_matlab()
    if matlab:
        return {
            matlab.double: np.float64,
            matlab.single: np.float32,
            matlab.logical: np.bool,
            matlab.uint64: np.uint64,
            matlab.uint32: np.uint64,
            matlab.uint16: np.uint16,
            matlab.uint8: np.uint8,
            matlab.int64: np.int64,
            matlab.int32: np.int32,
            matlab.int16: np.int16,
            matlab.int8: np.int8,
        }
    else:
        return {}


def _empty_array():
    """Matlab's default cell/struct elements are 0x0 arrays."""
    from .array import Array

    return Array.from_shape([0, 0])
