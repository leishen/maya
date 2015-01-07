"""ctypeshelper is a module that simplifies ctypes function call creation.

"""

from _ctypes import Array
from ctypes import Structure, Union


def dict2struct(d, cls):
    x = cls()
    for name, typ in cls._fields_:
        t = RawParam.get_base_type(typ)
        if issubclass(t, Union) or issubclass(t, Structure):
            setattr(x, name, dict2struct(d[name], t))
        elif 'Array' in typ.__class__.__name__:
            if issubclass(typ._type_, Structure):
                lst = []
                arr = getattr(x, name)
                for i in range(len(d[name])):
                    arr[i] = dict2struct(d[name][i], typ._type_)
                #setattr(x, name, *lst)
            else:
                setattr(x, name, typ(*d[name]))
        else:
            setattr(x, name, typ(d[name]))
    return x


def struct2dict(cval):
    if not isinstance(cval, Structure):
        raise ValueError("Must be a structure")
    d = {}
    if hasattr(cval, '_unions_'):
        d['_unions_'] = cval._unions_
    for name, typ in cval._fields_:
        d[name] = getattr(cval, name)
    return d


def resolve(cval):
    """Given a ctypes value (cval), convert all values into types and values
    meaningful to Python.
    :param cval: Ctypes value to resolve
    :return: python type
    """
    def resolve_union(cval, switch):
        if hasattr(cval.__class__, "_map_"):
            which = cval._map_[switch]
            return resolve(getattr(cval, which))
        else:
            return cval

    if hasattr(cval, "value"):             # basic type
        return cval.value
    elif hasattr(cval, "contents"):        # pointer type
        ret = resolve(cval.contents)
        return ret
    elif isinstance(cval, Array):
        if issubclass(cval._type_, Structure):
            return list(map(resolve, cval[:]))
        else:
            return bytes(cval[:])
    elif isinstance(cval, dict) or isinstance(cval, Structure):
        # If it's a dict, we got this from an errcheck call using parameters instead of a structure
        if isinstance(cval, Structure):
            # Map structure to dict just to ease maintenance
            cval = struct2dict(cval)
        f = {}
        for name, value in cval.items():
            if name == '_unions_':
                continue
            val = value
            while hasattr(val, "contents"):
                val = val.contents
            cls = RawParam.get_base_type(val.__class__)
            if issubclass(cls, Union):
                if '_unions_' in cval:
                    f[cval['_unions_'][name]] = resolve(cval[cval['_unions_'][name]])
                    f[name] = resolve_union(val, f[cval['_unions_'][name]])
                else:
                    f[name] = cval[name]
            else:
                f[name] = resolve(cval[name])
        return f
    else:
        return cval


class AutoStructure(Structure):
    pass


class RawParam:
    """A raw parameter that resolves to itself.  Useful for debugging
    and for one-off cases only.

    This is the foundation class for all other parameters.
    """
    def __init__(self, name, flags, ctype, generator, should_return, switch_is=None):
        self._name = name
        self._flags = flags     # direction
        self._param_type = ctype
        self._generate = generator
        self._should_return = should_return

        if switch_is:
            typ = RawParam.get_base_type(ctype)
            if not issubclass(typ, Union):
                raise ValueError("{0} is not a subclass of Union".format(ctype))
            self._switch_is = switch_is

    @staticmethod
    def get_base_type(cval):
        if hasattr(cval, "contents"):
            return RawParam.get_base_type(cval._type_)
        return cval

    @property
    def flags(self):
        """The directionality of the parameters for ctypes:

        1 -> input
        2 -> output
        4 -> input, defaults to 0
        """
        return self._flags

    @property
    def param_type(self):
        """The ctypes type of the parameter"""
        return self._param_type

    @property
    def name(self):
        """The name of the function"""
        return self._name

    @property
    def should_return(self):
        """Specifies whether this parameter should be returned when the function returns.  In many cases,
        output parameters from ctypes are not meaningful to Python, and can be filtered using this flag.
        """
        return self._should_return

    def resolve(self, instance):
        """Attempt to map an instance of a ctypes variable to a native Python type"""
        return instance

    @property
    def switch_is(self):
        return self._switch_is

    @property
    def has_generator(self):
        """Specifies whether this parameter has a generator.  See :func:`generate`"""
        return self._generate is not None

    def generate(self):
        """Used to generate a new instance of the parameter.  This is used to create a new input to a function
        call every time it is done, which defeats the problem inherent in ctypes in which parameters are reused
        when ctypes functions are specified globally"""
        return self._generate()


class ResolvedParam(RawParam):
    """A parameter that can be resolved from a ctypes type to a native Python type"""
    def resolve(self, p, resolved={}):
        pass


class InParam(ResolvedParam):
    """An input parameter to a function"""
    def __init__(self, ctype, name, generator=None, switch_is=None):
        super(self.__class__, self).__init__(name, 1, ctype, generator, False, switch_is=switch_is)


class ReturnInParam(ResolvedParam):
    """An input parameter that we wish to return upon execution of the foreign function"""
    def __init__(self, ctype, name, generator=None, switch_is=None):
        super(self.__class__, self).__init__(name, 1, ctype, generator, True, switch_is=switch_is)


class OutParam(ResolvedParam):
    """A ctypes output parameter"""
    def __init__(self, ctype, name, generator=None, switch_is=None):
        super(self.__class__, self).__init__(name, 2, ctype, generator, False, switch_is=switch_is)


class ReturnOutParam(ResolvedParam):
    """A ctypes output parameter that we wish to return from the foreign function"""
    def __init__(self, ctype, name, generator=None, switch_is=None):
        super(self.__class__, self).__init__(name, 2, ctype, generator, True, switch_is=switch_is)


class InOutParam(ResolvedParam):
    """A ctypes in/out parameter"""
    def __init__(self, ctype, name, generator=None, switch_is=None):
        super(self.__class__, self).__init__(name, 3, ctype, generator, False, switch_is=switch_is)


class ReturnInOutParam(ResolvedParam):
    """A ctypes in/out parameter that we wish to return from the foreign function"""
    def __init__(self, ctype, name, generator=None, switch_is=None):
        super(self.__class__, self).__init__(name, 3, ctype, generator, True, switch_is=switch_is)


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
        ret = []
        # Create dictionary of {name: cval}
        d = dict([(x.name, y) for x, y in zip(obj.params, args)])
        d['_unions_'] = {}
        # For the return values to be meaningful, we have a few things to do:
        # * drill down through pointers
        # * resolve unions so that we return the right dictionary
        for p, a in zip(obj.params, args):
            val = a
            while hasattr(val, "contents"):
                val = val.contents
            if issubclass(RawParam.get_base_type(val.__class__), Union):
                d['_unions_'][p.name] = p.switch_is
        if not d['_unions_']:
            del d['_unions_']
        # convert all return values to native python types
        resolved = resolve(d)
        # Return a list of values of the parameters with 'Return' in the class name
        for x in obj.params:
            if 'Return' in x.__class__.__name__:
                # This becomes the dict
                ret.append(resolved[x.name])
        # Return only the parameters specified by the user
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

        #
        # Dictionaries must be converted to their associated structures.  Unfortunately,
        # this is mildly irritating
        #
        def map_args(params, *args, **kwargs):
            a = []
            kw = {}
            params = [(x.name, x) for x in params]
            # Remove the number of params from args
            for i in range(len(args)):
                typ = RawParam.get_base_type(params[i][1].param_type)
                if issubclass(typ, Structure):
                    a.append(dict2struct(args[i], typ))
                else:
                    a.append(args[i])
            params = dict(params[len(args):])
            for k, v in kwargs.items():
                typ = RawParam.get_base_type(params[k].param_type)
                if issubclass(typ, Structure):
                    kw[k] = dict2struct(v, typ)
                else:
                    kw[k] = v
            return a, kw

        a, kw = map_args(self._params, *args, **kwargs)
        ret = fn(*a, **kw)
        # TODO What happens when there are no output parameters???
        if (isinstance(ret, list) or isinstance(ret, tuple)) and len(ret) == 1:
            return ret[0]
        else:
            return ret
