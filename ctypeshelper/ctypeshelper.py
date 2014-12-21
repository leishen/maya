from _ctypes import Array

__all__ = ['RawParam', 'ResolvedParam',
           'InParam', 'ReturnInParam',
           'OutParam', 'ReturnOutParam',
           'InOutParam', 'ReturnInOutParam',
           'HelperFunc']


class RawParam:
    """A raw parameter that resolves to itself.  Useful for debugging
    and for one-off cases only.
    """
    def __init__(self, name, flags, ctype, generator, should_return):
        self._name = name
        self._flags = flags     # direction
        self._param_type = ctype
        self._generate = generator
        self._should_return = should_return

    @property
    def flags(self):
        return self._flags

    @property
    def param_type(self):
        return self._param_type

    @property
    def name(self):
        return self._name

    @property
    def should_return(self):
        return self._should_return

    def resolve(self, p):
        return p

    @property
    def has_generator(self):
        return self._generate is not None

    def generate(self):
        return self._generate()


class ResolvedParam(RawParam):
    """A parameter that can be resolved from a ctypes type to a native Python type"""
    def resolve(self, p):
        # TODO Find a good way to do a type safety check.  Otherwise, this class is effectively useless
        # How do we determine that one ctypes type can be interpreted as another?  Should we?
        if hasattr(p, "value"):             # basic type
            return p.value
        elif hasattr(p, "contents"):        # pointer type
            return self.resolve(p.contents)
        elif isinstance(p, Array):
            return bytes(p[:])
        else:
            return p


class InParam(ResolvedParam):
    def __init__(self, ctype, name, generator=None):
        super(self.__class__, self).__init__(name, 1, ctype, generator, False)


class ReturnInParam(ResolvedParam):
    def __init__(self, ctype, name, generator=None):
        super(self.__class__, self).__init__(name, 1, ctype, generator, True)


class OutParam(ResolvedParam):
    def __init__(self, ctype, name, generator=None):
        super(self.__class__, self).__init__(name, 2, ctype, generator, False)


class ReturnOutParam(ResolvedParam):
    def __init__(self, ctype, name, generator=None):
        super(self.__class__, self).__init__(name, 2, ctype, generator, True)


class InOutParam(ResolvedParam):
    def __init__(self, ctype, name, generator=None):
        super(self.__class__, self).__init__(name, 3, ctype, generator, False)


class ReturnInOutParam(ResolvedParam):
    def __init__(self, ctype, name, generator=None):
        super(self.__class__, self).__init__(name, 3, ctype, generator, True)


class HelperFunc:
    def __init__(self, generator, name, module, ret):
        self._gen = generator
        self._name = name
        self._module = module
        self._rettype = ret
        self._params = ()       # These MUST not store any actual instance information

    @staticmethod
    def errcheck(result, func, args):
        obj = func.object
        # return just the output params
        ret = []
        for i in range(len(obj.params)):
            if 'Return' in obj.params[i].__class__.__name__:
                ret.append(obj.params[i].resolve(args[i]))
        return ret

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, value):
        valid = all([isinstance(x, RawParam) for x in value])
        if not valid:
            raise ValueError("Only params are supported")
        self._params = tuple(value)

    def __call__(self, *args, **kwargs):
        prototype = self._gen(self._rettype, *[x.param_type for x in self._params])
        paramflags = []
        for p in self._params:
            if p.has_generator:
                paramflags.append((p.flags, p.name, p.generate()))
            else:
                paramflags.append((p.flags, p.name))
        fn = prototype((self._name, self._module), tuple(paramflags))
        # Link the object to the function so we can intelligently reason about
        # the output parameters post-execution
        fn.object = self
        retfunc = getattr(self, "errcheck", None)
        if retfunc:
            fn.errcheck = retfunc
        ret = fn(*args, **kwargs)
        if (isinstance(ret, list) or isinstance(ret, tuple)) and len(ret) == 1:
            return ret[0]
        else:
            return ret
