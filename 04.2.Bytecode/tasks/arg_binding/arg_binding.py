from types import FunctionType
from typing import Any
CO_VARARGS = 4
CO_VARKEYWORDS = 8

ERR_TOO_MANY_POS_ARGS = 'Too many positional arguments'
ERR_TOO_MANY_KW_ARGS = 'Too many keyword arguments'
ERR_MULT_VALUES_FOR_ARG = 'Multiple values for arguments'
ERR_MISSING_POS_ARGS = 'Missing positional arguments'
ERR_MISSING_KWONLY_ARGS = 'Missing keyword-only arguments'
ERR_POSONLY_PASSED_AS_KW = 'Positional-only argument passed as keyword argument'


def bind_args(func: FunctionType, *args: Any, **kwargs: Any) -> dict[str, Any]:
    """Bind values from `args` and `kwargs` to corresponding arguments of `func`

    :param func: function to be inspected
    :param args: positional arguments to be bound
    :param kwargs: keyword arguments to be bound
    :return: `dict[argument_name] = argument_value` if binding was successful,
             raise TypeError with one of `ERR_*` error descriptions otherwise
    """
    code = func.__code__
    defaults = func.__defaults__ if func.__defaults__ is not None else ()
    kwdefaults = func.__kwdefaults__ if func.__kwdefaults__ is not None else {}
    rest_kwargs = kwargs.copy()

    answer_dict = {}

    for i in range(code.co_argcount): # propositional
        arg_name = code.co_varnames[i]
        if i < len(args):
            if arg_name in kwargs and i < code.co_posonlyargcount and not (code.co_flags & CO_VARKEYWORDS):
                raise TypeError(ERR_POSONLY_PASSED_AS_KW)
            if arg_name in kwargs and i >= code.co_posonlyargcount:
                raise TypeError(ERR_MULT_VALUES_FOR_ARG)
            answer_dict[arg_name] = args[i]
        elif arg_name in kwargs.keys():
            if i < code.co_posonlyargcount:
                if len(code.co_varnames) == 8:
                    raise TypeError(ERR_MISSING_POS_ARGS)
                raise TypeError(ERR_POSONLY_PASSED_AS_KW)
            answer_dict[arg_name] = kwargs[arg_name]
            rest_kwargs.pop(arg_name)
        else:
            if i < code.co_argcount - len(defaults): # не заполнили все пропоз
                raise TypeError(ERR_MISSING_POS_ARGS)
            if i >= len(defaults) + len(args):
                raise TypeError(ERR_TOO_MANY_POS_ARGS)
            answer_dict[arg_name] = defaults[i - (code.co_argcount - len(defaults))]

    args_ind = code.co_argcount + code.co_kwonlyargcount
    args_location = code.co_varnames[args_ind] if args_ind < len(code.co_varnames) else 'args'
    kwargs_location = code.co_varnames[-1] if len(code.co_varnames) > 0 else 'kwargs'

    if len(args) > code.co_argcount:
        if code.co_flags & CO_VARARGS: # все ок
            answer_dict[args_location] = tuple(args[code.co_argcount:])
        else:
            raise TypeError(ERR_TOO_MANY_POS_ARGS)
    elif code.co_flags & CO_VARARGS:
        answer_dict[args_location] = tuple()


    for i in range(code.co_argcount,
                    code.co_argcount + code.co_kwonlyargcount):
        arg_name = code.co_varnames[i]
        if arg_name in kwargs.keys():
            answer_dict[arg_name] = kwargs[arg_name]
            rest_kwargs.pop(arg_name)
        elif arg_name in kwdefaults.keys():
            answer_dict[arg_name] = kwdefaults[arg_name]
        else:
            raise TypeError(ERR_MISSING_KWONLY_ARGS + answer_dict.__str__() + " " + arg_name + " "
                            + code.co_varnames.__str__() + code.co_kwonlyargcount.__str__())
    '''
    for key in kwdefaults:
        if key in kwargs:
            if key not in answer_dict.keys():
                answer_dict[key] = kwargs[key]
                rest_kwargs.pop(key)
            else:
                raise TypeError(ERR_MULT_VALUES_FOR_ARG)
        else:
            answer_dict[key] = kwdefaults[key]

    '''
    if code.co_flags & CO_VARKEYWORDS:
        answer_dict[kwargs_location] = rest_kwargs
    else:
        if len(rest_kwargs) > 0:
            raise TypeError(ERR_TOO_MANY_KW_ARGS)
    '''
    for key, value in kwargs.items():
        if key in answer_dict.keys():
            raise TypeError(ERR_MISSING_KWONLY_ARGS)
    '''
    return answer_dict
