from abc import ABC, abstractmethod

from .core import MatlabType
from .utils import _import_matlab


class Runtime(ABC):
    """Namespace that holds the matlab runtime.

    Wrapped packages should implement their own inheriting class
    and define the `_import` method.

    Example
    -------
    ```python
    class SPMRuntime(Runtime):

        @classmethod
        def _import_runtime(cls):
            import spm_runtime
            return spm_runtime
    ```
    """

    _instance = None
    verbose = True

    @classmethod
    @abstractmethod
    def _import_runtime(cls):
        """"""
        ...

    @classmethod
    def instance(cls):
        if cls._instance is None:
            if cls.verbose:
                print("Initializing Matlab Runtime...")
            cls._init_instance()
        return cls._instance

    @classmethod
    def call(cls, fn, *args, **kwargs):
        (args, kwargs) = cls._process_argin(*args, **kwargs)
        res = cls.instance().mpython_endpoint(fn, *args, **kwargs)
        return cls._process_argout(res)

    @classmethod
    def _process_argin(cls, *args, **kwargs):
        to_runtime = MatlabType._to_runtime
        args = tuple(map(to_runtime, args))
        kwargs = dict(zip(kwargs.keys(), map(to_runtime, kwargs.values())))
        return args, kwargs

    @classmethod
    def _process_argout(cls, res):
        return MatlabType._from_runtime(res, _runtime=cls)

    @classmethod
    def _init_instance(cls):
        # NOTE(YB)
        #   I moved the import within a function so that array wrappers
        #   can be imported and used even when matlab is not properly setup.
        if cls._instance:
            return
        try:
            cls._instance = cls._import_runtime()
            # Make sure matlab is imported
            _import_matlab()
        except ImportError as e:
            print(cls._help)
            raise e

    _help = """
    Failed to import package runtime. This can be due to a failure to find the
    MATLAB Runtime. Please verify that MATLAB Runtime is installed and can be
    discovered. See https://github.com/balbasty/matlab-runtime for instructions
    on how to install the MATLAB Runtime.
    If the issue persists, please open an issue with the entire error
    message at https://github.com/MPython-Package-Factory/mpython-core/issues.
    """
