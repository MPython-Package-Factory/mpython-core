from .core import MatlabType
from .utils import _import_matlab


class MatlabFunction(MatlabType):
    """
    Wrapper for matlab function handles.

    End users should not have to instantiate such objects themselves.

    Example
    -------
    ```python
    times2 = Runtime.call("eval", "@(x) 2.*x")
    assert(time2(1) == 2)
    ```
    """

    def __init__(self, matlab_object, runtime):
        super().__init__()

        matlab = _import_matlab()
        if not isinstance(matlab_object, matlab.object):
            raise TypeError("Expected a matlab.object")

        self._matlab_object = matlab_object
        self._runtime = runtime

    def _as_runtime(self):
        return self._matlab_object

    @classmethod
    def _from_runtime(cls, other, runtime):
        return cls(other, runtime)

    @classmethod
    def from_any(cls, other, runtime=None):
        if isinstance(other, MatlabFunction):
            return other
        return cls._from_runtime(other, runtime)

    def __call__(self, *args, **kwargs):
        return self._runtime.call(self._matlab_object, *args, **kwargs)
