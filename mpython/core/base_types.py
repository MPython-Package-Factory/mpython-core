from functools import partial

import numpy as np

from ..utils import _import_matlab, _matlab_array_types, DelayedImport


class _imports(DelayedImport):
    Array = 'mpython.array.Array'
    Cell = 'mpython.cell.Cell'
    Struct = 'mpython.struct.Struct'
    SparseArray = 'mpython.sparse_array.SparseArray'
    MatlabClass = 'mpython.matlab_class.MatlabClass'
    MatlabFunction = 'mpython.matlab_function.MatlabFunction'
    AnyDelayedArray = 'mpython.core.delayed_types.AnyDelayedArray'


class MatlabType:
    """Generic type for objects that have an exact matlab equivalent."""

    @classmethod
    def from_any(cls, other, **kwargs):
        """
        Convert python/matlab objects to `MatlabType` objects
        (`Cell`, `Struct`, `Array`, `MatlabClass`).

        !!! warning "Conversion is performed in-place when possible."
        """
        # Circular import
        Array = _imports.Array
        Cell = _imports.Cell
        MatlabClass = _imports.MatlabClass
        MatlabFunction = _imports.MatlabFunction
        SparseArray = _imports.SparseArray
        Struct = _imports.Struct
        AnyDelayedArray = _imports.AnyDelayedArray

        # Conversion rules:
        # - we do not convert to matlab's own array types
        #   (`matlab.double`, etc);
        # - we do not convert to types that can be passed directly to
        #   the matlab runtime;
        # - instead, we convert to python types that mimic matlab types.
        _from_any = partial(cls.from_any, **kwargs)
        _runtime = kwargs.pop("_runtime", None)

        if isinstance(other, MatlabType):
            if isinstance(other, AnyDelayedArray):
                other._error_is_not_finalized()
            return other

        if isinstance(other, dict):
            if "type__" in other:
                type__ = other["type__"]

                if type__ == "none":
                    # MPython returns this when catching a function
                    # that should return no values but is asked for one.
                    return None

                elif type__ == "emptystruct":
                    return Struct.from_shape([0])

                elif type__ == "structarray":
                    # MPython returns a list of dictionaries in data__
                    # and the array shape in size__.
                    return Struct._from_runtime(other, _runtime)

                elif type__ == "cell":
                    # MPython returns a list of dictionaries in data__
                    # and the array shape in size__.
                    return Cell._from_runtime(other, _runtime)

                elif type__ == "object":
                    # MPython returns the object's fields serialized
                    # in a dictionary.
                    return MatlabClass._from_runtime(other, _runtime)

                elif type__ == "sparse":
                    # MPython returns the coordinates and values in a dict.
                    return SparseArray._from_runtime(other, _runtime)

                elif type__ == "char":
                    # Character array that is not a row vector
                    # (row vector are converted to str automatically)
                    # MPython returns all rows in a (F-ordered) cell in data__
                    # Let's use the cell constructor to return a cellstr.
                    # -> A cellstr is a column vector, not a row vector
                    size = np.asarray(other["size__"]).tolist()[0]
                    size = size[:-1] + [1]
                    other["type__"] = "cell"
                    other["size__"] = np.asarray([size])
                    return Cell._from_runtime(other, _runtime)

                else:
                    raise ValueError("Don't know what to do with type", type__)

            else:
                other = type(other)(
                    zip(other.keys(), map(_from_any, other.values()))
                )
                return Struct.from_any(other)

        if isinstance(other, (list, tuple, set)):
            # nested tuples are cells of cells, not cell arrays
            if _runtime:
                return Cell._from_runtime(other, _runtime)
            else:
                return Cell.from_any(other)

        if isinstance(other, (np.ndarray, int, float, complex, bool)):
            # [array of] numbers -> Array
            if _runtime:
                return Array._from_runtime(other, _runtime)
            else:
                return Array.from_any(other)

        if isinstance(other, str):
            return other

        if isinstance(other, bytes):
            return other.decode()

        if other is None:
            # This can happen when matlab code is called without `nargout`
            return other

        matlab = _import_matlab()
        if matlab and isinstance(other, matlab.object):
            return MatlabFunction._from_runtime(other, _runtime)

        if type(other) in _matlab_array_types():
            return Array._from_runtime(other, _runtime)

        if hasattr(other, "__iter__"):
            # Iterable -> let's try to make it a cell
            return cls.from_any(list(other), _runtime=_runtime)

        raise TypeError(f"Cannot convert {type(other)} into a matlab object.")

    @classmethod
    def _from_runtime(cls, obj, _runtime):
        return cls.from_any(obj, _runtime=_runtime)

    @classmethod
    def _to_runtime(cls, obj):
        """
        Convert object to representation that the matlab runtime understands.
        """
        to_runtime = cls._to_runtime
        from ..utils import sparse  # FIXME: Circular import

        if isinstance(obj, MatlabType):
            # class / structarray / cell
            return obj._as_runtime()

        elif isinstance(obj, (list, tuple, set)):
            return type(obj)(map(to_runtime, obj))

        elif isinstance(obj, dict):
            if "type__" in obj:
                return obj
            return type(obj)(zip(obj.keys(), map(to_runtime, obj.values())))

        elif isinstance(obj, np.ndarray):
            obj = np.asarray(obj)
            if obj.dtype in (object, dict):
                shape, dtype = obj.shape, obj.dtype
                obj = np.fromiter(map(to_runtime, obj.flat), dtype=dtype)
                obj = obj.reshape(shape)
                return obj.tolist()
            return obj

        elif sparse and isinstance(obj, sparse.sparray):
            SparseArray = _imports.SparseArray
            return SparseArray.from_any(obj)._as_runtime()

        else:
            # TODO: do we want to raise if the type is not supported by matlab?
            #
            # Valid types for matlab bindings:
            #   - bool, int, float, complex, str, bytes, bytearray
            #
            # Valid matlab types that we have already dealt with:
            #   - list, tuple, set, dict, ndarray
            #
            # All other values/types are invalid (including `None`!)
            return obj

    def _as_runtime(self):
        raise NotImplementedError

    def _as_matlab_object(self):
        # Backward compatibility
        # FIXME: Or just keep `_as_matlab_object` and remove `_as_runtime`?
        return self._as_runtime()


class AnyMatlabArray(MatlabType):
    """Base class for all matlab-like arrays (numeric, cell, struct)."""

    @property
    def as_num(self):
        raise TypeError(
            f"Cannot interpret a {type(self).__name__} as a numeric array"
        )

    @property
    def as_cell(self):
        raise TypeError(
            f"Cannot interpret a {type(self).__name__} as a cell"
        )

    @property
    def as_struct(self):
        raise TypeError(
            f"Cannot interpret a {type(self).__name__} as a struct"
        )

    # TODO: `as_obj` for object arrays?
