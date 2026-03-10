"""
Simplified VM code which works for some cases.
You need extend/rewrite code to pass all cases.
"""

import builtins
import collections
import dis
import types
import typing as tp
from typing import Any

CO_VARARGS = 4
CO_VARKEYWORDS = 8

ERR_TOO_MANY_POS_ARGS = 'Too many positional arguments'
ERR_TOO_MANY_KW_ARGS = 'Too many keyword arguments'
ERR_MULT_VALUES_FOR_ARG = 'Multiple values for arguments'
ERR_MISSING_POS_ARGS = 'Missing positional arguments'
ERR_MISSING_KWONLY_ARGS = 'Missing keyword-only arguments'
ERR_POSONLY_PASSED_AS_KW = 'Positional-only argument passed as keyword argument'


def bind_args(code: types.CodeType, defaults = (), kwdefaults = {}, *args: Any, **kwargs ) -> dict[str, Any]:

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
               break
            if i >= len(defaults) + len(args):
                break
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
    if code.co_flags & CO_VARKEYWORDS:
        answer_dict[kwargs_location] = rest_kwargs
    else:
        if len(rest_kwargs) > 0:
            raise TypeError(ERR_TOO_MANY_KW_ARGS)
    return answer_dict


class Cell:
    def __init__(self, value=None):
        self.cell_contents = value



class Frame:
    """
    Frame header in cpython with description
        https://github.com/python/cpython/blob/3.13/Include/internal/pycore_frame.h

    Text description of frame parameters
        https://docs.python.org/3/library/inspect.html?highlight=frame#types-and-members
    """
    def __init__(self,
                 frame_code: types.CodeType,
                 frame_builtins: dict[str, tp.Any],
                 frame_globals: dict[str, tp.Any],
                 frame_locals: dict[str, tp.Any]) -> None:
        self.code = frame_code
        self.builtins = frame_builtins
        self.globals = frame_globals
        self.locals = frame_locals
        self.data_stack: tp.Any = []
        self.return_value = None
        self.ind = 0
        self.offset_to_index = {}
        self.current_offset = 0
        self.names = []
        self.cells = {}
        self.global_arg = 0
        self.exception_state = None

    def top(self) -> tp.Any:
        return self.data_stack[-1]

    def pop(self) -> tp.Any:
        return self.data_stack.pop()

    def push(self, *values: tp.Any) -> None:
        self.data_stack.extend(values)

    def popn(self, n: int) -> tp.Any:
        """
        Pop a number of values from the value stack.
        A list of n values is returned, the deepest value first.
        """
        if n > 0:
            returned = self.data_stack[-n:]
            self.data_stack[-n:] = []
            return returned
        else:
            return []

    def run(self) -> tp.Any:
        self.ind = 0
        instructions = list(dis.get_instructions(self.code))


        self.offset_to_index = {instruction.offset: i for i, instruction in enumerate(instructions)}

        while self.ind < len(instructions):
            instruction = instructions[self.ind]
            self.current_offset = instruction.offset
            self.global_arg = instruction.arg if instruction.arg is not None else 0
            getattr(self, instruction.opname.lower() + "_op")(instruction.argval)
            self.ind += 1
        return self.return_value

############################ load / store ############################

    def load_const_op(self, arg: tp.Any) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.13.7/library/dis.html#opcode-LOAD_CONST
        """
        self.push(arg)

    def load_fast_op(self, arg) -> None:
        if arg in self.locals.keys():
            self.push(self.locals[arg])
        elif arg in self.globals.keys():
            self.push(self.globals[arg])
        elif arg in self.builtins.keys():
            self.push(self.builtins[arg])
        else:
            raise NameError()

    def delete_fast_op(self, arg)->None:
        del self.locals[arg]

    def store_fast_op(self, arg):
        self.locals[arg] = self.pop()

    def check_eg_match(self, arg):
        pass

    def check_exc_match(self, arg):
        pass

    def match_mapping_op(self, arg):
        if isinstance(self.top(), collections.abc.Mapping):
            self.push(True)
        else:
            self.push(False)

    def load_fast_check_op(self, arg):
        if arg in self.locals.keys():
            self.push(self.locals[arg])
        else:
            raise UnboundLocalError("The local variable has not been initialized.")

    def load_global_op(self, arg: str) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.13.7/library/dis.html#opcode-LOAD_GLOBAL
        """
        if arg in self.globals:
            self.push(self.globals[arg])
        elif arg in self.builtins:
            self.push(self.builtins[arg])
        else:
           raise NameError()
        if self.global_arg & 1:
            self.push(None)

    def store_global_op(self, arg: str) -> None:
        self.globals[arg] = self.pop()

    def delete_global_op(self, arg: str) -> None:
        if arg in self.globals.keys():
            del self.globals[arg]
        else:
            raise NameError()


    def setup_annotations_op(self, arg):
        if "__annotations__" not in self.locals:
            self.locals["__annotations__"] = {}

    def load_fast_and_clear_op(self, arg):
        if arg in self.locals:
            self.push(self.locals[arg])
        else:
            self.push(None)
        self.locals[arg] = None




    def load_locals_op(self, arg):
        self.push(self.locals)


    # def load_from_dict_or_globals_op(self, arg):


    def store_fast_load_fast_op(self, arg):
        store_name = arg[0]
        load_name = arg[1]
        value = self.pop()
        self.locals[store_name] = value
        self.push(self.locals[load_name])

    def load_fast_load_fast_op(self, arg):
        self.push(self.locals[arg[0]])
        self.push(self.locals[arg[1]])

    ############################ arithmetic operations ############################


    def binary_op_op(self, op) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.13.7/library/dis.html#opcode-BINARY_OP
        """
        rhs = self.pop()
        lhs = self.pop()
        match op:
            case 0:
                self.push(lhs + rhs)
            case 1:
                self.push(lhs & rhs)
            case 2:
                self.push(lhs // rhs)
            case 3:
                self.push(lhs << rhs)
            case 4:
                self.push(lhs @ rhs)
            case 5:
                self.push(lhs * rhs)
            case 6:
                self.push(lhs % rhs)
            case 7:
                self.push(lhs | rhs)
            case 8:
                self.push(lhs**rhs)
            case 9:
                self.push(lhs >> rhs)
            case 10:
                self.push(lhs - rhs)
            case 11:
                self.push(lhs / rhs)
            case 12:
                self.push(lhs ^ rhs)
            case 13:
                self.push(lhs + rhs)
            case 14:
                self.push(lhs & rhs)
            case 15:
                self.push(lhs // rhs)
            case 16:
                self.push(lhs << rhs)
            case 17:
                self.push(lhs @ rhs)
            case 18:
                self.push(lhs * rhs)
            case 19:
                self.push(lhs % rhs)
            case 20:
                self.push(lhs | rhs)
            case 21:
                self.push(lhs**rhs)
            case 22:
                self.push(lhs >> rhs)
            case 23:
                self.push(lhs - rhs)
            case 24:
                self.push(lhs / rhs)
            case 25:
                self.push(lhs ^ rhs)
            case _:
                raise NameError(op)

    def call_intrinsic_1_op(self, arg):
        value = self.pop()
        match arg:
            case 2:
                for name in dir(value):
                    if not name.startswith("__"):
                        self.globals[name] = getattr(value, name)
                self.push(None)
            case 5:
                self.push(+value)
            case 6:
                self.push(tuple(value))
            case 3:
                self.push(value.value)
            case 1:
                self.push(print(value))
            case _:
                self.push(value)

    def call_intrinsic_2_op(self, arg):
        pass

    def unary_negative_op(self, arg):
        self.push(-self.pop())

    def unary_not_op(self, arg):
        self.push(not self.pop())

    def unary_invert_op(self, arg):
        self.push(~self.pop())

    def nop_op(self, arg):
        pass

    def contains_op_op(self, arg):
        container = self.pop()
        element = self.pop()
        if element in container:
            self.push( True if arg == 0 else False)
        else:
            self.push(False if arg == 0 else True)

    def is_op_op(self, arg):
        first = self.pop()
        second = self.pop()
        if first is second:
            self.push(True if arg != 1 else False)
        else:
            self.push(False if arg != 1 else True)

    def to_bool_op_op(self, arg) -> None:
        self.push(bool(self.pop()))

    def convert_value_op(self, arg):
        value = self.pop()
        if arg == 1:
            self.push(str(value))
        elif arg == 2:
            self.push(repr(value))
        else:
            self.push(ascii(value))

    def to_bool_op(self, arg) -> None:
        self.push(bool(self.pop()))

    def compare_op_op(self, op):
        rhs = self.pop()
        lhs = self.pop()
        match op:
            case '==':
                self.push(bool(lhs == rhs))
            case "!=":
                self.push(bool(lhs != rhs))
            case "<":
                self.push(bool(lhs < rhs))
            case ">":
                self.push(bool(lhs > rhs))
            case "<=":
                self.push(bool(lhs <= rhs))
            case ">=":
                self.push(bool(lhs >= rhs))
            case _:
                raise NameError(op)
    ############################ slices ############################
    def binary_slice_op(self, arg):
        end = self.pop()
        start = self.pop()
        container = self.pop()
        self.push(container[start:end])

    def store_slice_op(self, arg):
        end = self.pop()
        start = self.pop()
        container = self.pop()
        values = self.pop()
        container[start:end] = values
        self.push(container)

    def build_slice_op(self, argc):
        if argc == 2:
            end = self.pop()
            start = self.pop()
            self.push(slice(start, end))
        elif argc == 3:
            step = self.pop()
            end = self.pop()
            start = self.pop()
            self.push(slice(start, end, step))

    def binary_subscr_op(self, arg):
        key = self.pop()
        container = self.pop()
        self.push(container[key])

    def delete_subscr_op(self, arg):
        key = self.pop()
        container = self.pop()
        del container[key]
        self.push(container)

    def store_subscr_op(self, arg):
        key = self.pop()
        container = self.pop()
        value = self.pop()
        container[key] = value
        self.push(container)


    def swap_op(self, arg):
        temp = self.data_stack[-1]
        self.data_stack[-1] = self.data_stack[-arg]
        self.data_stack[-arg] = temp

    def before_with_op(self, arg):
        pass

############################ list, tuple ############################
    def build_tuple_op(self, arg):
        value = ()
        if arg != 0:
            value = tuple(self.data_stack[-arg:])
            self.popn(arg)
        self.push(value)

    def build_list_op(self, arg):
        value = []
        if arg != 0:
            value = list(self.data_stack[-arg:])
            self.popn(arg)
        self.push(value)

    def build_set_op(self, arg):
        value = set()
        if arg != 0:
            value = set(self.data_stack[-arg:])
            self.popn(arg)
        self.push(value)

    def list_append_op(self, arg):
        item = self.pop()
        self.data_stack[-arg].append(item)

    def set_add_op(self, arg):
        item = self.pop()
        self.data_stack[-arg].add(item)

    def map_add_op(self, arg):
        item = self.pop()
        key = self.pop()
        self.data_stack[-arg][key] = item

    def list_extend_op(self, arg):
        seq = self.pop()
        self.data_stack[-arg].extend(seq)

    def set_update_op(self, arg):
        seq = self.pop()
        self.data_stack[-arg].update(seq)

    def dict_update_op(self, arg):
        seq = self.pop()
        self.data_stack[-arg].update(seq)

    def dict_merge_op(self, arg):
        seq = self.pop()
        self.data_stack[-arg].update(seq)

    def build_map_op(self, count):
        new_dict = {}
        for i in range(count):
            value = self.pop()
            key = self.pop()
            new_dict[key] = value
        self.push(new_dict)

    def build_const_key_map_op(self, count):
        keys = self.pop()
        values = []
        for i in range(count):
            values.append(self.pop())
        values.reverse()
        new_dict = {keys[ind]: values[ind] for ind in range(len(keys))}
        self.push(new_dict)

############################ for and if ############################
    def pop_except(self, arg):
        self.exception_state = self.pop()

    def pop_jump_if_false_op(self, arg):
        val = self.pop()
        if not val:
            self.ind = self.offset_to_index[arg] - 1

    def pop_jump_if_true_op(self, arg):
        val = self.pop()
        if val:
            self.ind = self.offset_to_index[arg] - 1
    def pop_jump_if_none(self, arg):
        val = self.pop()
        if val is None:
            self.ind = self.offset_to_index[arg] - 1
    def pop_jump_if_not_none(self, arg):
        val = self.pop()
        if val is not None:
            self.ind = self.offset_to_index[arg] - 1

    def get_iter_op(self, arg):
        self.push(iter(self.pop()))

    def get_len_op(self, arg):
        self.push(len(self.top()))

    def for_iter_op(self, arg):
        iterator = self.data_stack[-1]
        try:
            value = next(iterator)
            self.push(value)
        except StopIteration:
            self.ind = self.offset_to_index[arg]

    def jump_backward_no_interrupt_op(self, arg):
        self.ind = self.offset_to_index[arg] - 1

    def jump_backward_op(self, arg):
        #pass
        self.ind = self.offset_to_index[arg] - 1

    def jump_forward_op(self, arg):
        self.ind = self.offset_to_index[arg] - 1

    def end_for_op(self, arg):
        pass

    def push_exc_info_op(self, arg):
        value = self.pop()
        self.push(self.exception_state)
        self.push(value)


############################ inplace operators ############################

    def unpack_sequence_op(self, count):
        assert len(self.data_stack[-1]) == count
        self.data_stack.extend(self.pop()[: -count - 1 : -1])

    ############################ etc ############################2
    def resume_op(self, arg: int) -> tp.Any:
        pass

    def push_null_op(self, arg: int) -> tp.Any:
        self.push(None)

    def precall_op(self, arg: int) -> tp.Any:
        pass

    def call_op(self, arg: int) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.13.7/library/dis.html#opcode-CALL
        """
        arguments = self.popn(arg)
        null = self.pop() #
        f = self.pop()
        if null is not None:
            self.push(f(null, *arguments))
        else:
            self.push(f(*arguments))

    def load_name_op(self, arg: str) -> None:
        """
        Partial realization

        Operation description:
            https://docs.python.org/release/3.13.7/library/dis.html#opcode-LOAD_NAME
        """
        if arg in self.locals:
            self.push(self.locals[arg])
        elif arg in self.globals:
            self.push(self.globals[arg])
        elif arg in self.builtins:
            self.push(self.builtins[arg])
        else:
            raise NameError(arg)

    def extended_arg_op(self, arg):
        pass

    def unpack_ex_op(self, arg):
        seq = self.pop()
        seq = reversed(seq)
        self.push(*seq)

    def import_from_op(self, arg):
        self.push(getattr(self.data_stack[-1], arg))

    def import_name_op(self, arg):
        fromlist = self.pop()
        level = self.pop()
        module = __import__(arg, globals=self.globals, locals=self.locals, fromlist=fromlist, level=level)
        self.push(module)

    def delete_name_op(self, arg):
        del self.locals[arg]

    def return_value_op(self, arg: tp.Any) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.13.7/library/dis.html#opcode-RETURN_VALUE
        """
        self.return_value = self.pop()

    def return_const_op(self, arg: tp.Any) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.13.7/library/dis.html#opcode-RETURN_VALUE
        """
        self.return_value = arg
        self.ind = int(1e10)

    def pop_top_op(self, arg: tp.Any) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.13.7/library/dis.html#opcode-POP_TOP
        """
        self.pop()

    ############################ Functions ############################
    def set_function_attribute_op(self, flag):
        func = self.pop()
        attr_value = self.pop()

        if flag == 0x01:
            func.__defaults__ = attr_value
        elif flag == 0x02:
            func.__kwdefaults__ = attr_value
        elif flag == 0x04:
            func.__annotations__ = attr_value
        elif flag == 0x08:
            func.__closure__ = attr_value
        else:
            raise IndexError(flag)
        self.push(func)

    def call_function_ex_op(self, count):
        kwargs = {}
        if self.global_arg & 1:
            kwargs = self.pop()
        args = self.pop()
        func = self.pop()
        result = func(*args, **kwargs)
        self.push(result)

    def kw_names_op(self, arg):
        pass


    def call_kw_op(self, count):
        kwnames = self.pop()
        n_kw = len(kwnames) if kwnames is not None else 0
        n_pos = count - n_kw
        kwvalues = []
        for ind in range(n_kw):
            kwvalues.append(self.pop())
        args = []
        for ind in range(n_pos):
            args.append(self.pop())
        args.reverse()
        kwvalues.reverse()
        null = self.pop()
        func = self.pop()
        kwargs = {}
        if kwnames:
            for i, name in enumerate(kwnames):
                kwargs[name] = kwvalues[i]
        if null is not None:
            self.push(func(null, *args, **kwargs))
        else:
            self.push(func(*args, **kwargs))
    def make_function_op(self, arg: int) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.13.7/library/dis.html#opcode-MAKE_FUNCTION
        """
        code = self.pop()  # the code associated with the function (at TOS1)
        def f(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
            # TODO: parse input arguments using code attributes such as co_argcount
            parsed_args: dict[str, tp.Any] = bind_args(code, (), {},*args, **kwargs)
            f_locals = dict(self.locals)
            f_locals.update(parsed_args)

            frame = Frame(code, self.builtins, self.globals, f_locals)  # Run code in prepared environment
            return frame.run()

        self.push(f)

    def store_name_op(self, arg: str) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.13.7/library/dis.html#opcode-STORE_NAME
        """
        const = self.pop()
        self.locals[arg] = const


    ############################ Strings ############################
    def format_simple_op(self, arg):
        value = self.pop()
        result = value.__format__("")
        self.push(result)

    def format_with_spec_op(self, arg):
        spec = self.pop()
        value = self.pop()
        result = value.__format__(spec)
        self.push(result)

    def build_string_op(self, arg):
        temp = []
        for i in range(arg):
            temp.append(self.pop())
        temp.reverse()
        self.push(''.join(temp))

    ############################ Objects ############################
    def reraise(self, arg):
        exception = self.pop()
        if arg != 0:
            self.pop()
            raise exception
        else:
            raise exception

    def raise_varargs_op(self, arg):
        if arg == 0:
            raise
        elif arg == 1:
            raise self.pop()
        else:
            cause = self.pop()
            raise self.pop() from cause

    def return_generator_op(self, arg):
        pass

    def load_attr_op(self, arg):
        obj = self.pop()

        if self.global_arg & 1:
            try:
                attr = getattr(type(obj), arg)
                self.push(attr)
                self.push(obj)
            except AttributeError:
                try:
                    attr = getattr(obj, arg)
                    self.push(attr)
                    self.push(None)
                except AttributeError:
                    self.push(None)
                    self.push(None)
        else:
            attr = getattr(obj, arg)
            self.push(attr)


    def store_attr_op(self, name):
        obj = self.pop()
        value = self.pop()
        setattr(obj, name, value)
        self.push(obj)

    def load_build_class_op(self, arg):
        self.push(builtins.__build_class__)

    def delete_attr_op(self, name):
        obj = self.pop()
        if hasattr(obj, name):
            delattr(obj, name)
        self.push(obj)

    def copy_op(self, arg):
        self.push(self.data_stack[-arg])
    ############################ Exceptions ############################
    def load_assertion_error_op(self, arg):
        self.push(AssertionError())


    ############################ Cells ############################


    def make_cell_op(self, name):
        if name in self.locals:
            value = self.locals[name]
            del self.locals[name]
            self.cells[name] = Cell(value)
        else:
            self.cells[name] = Cell(None)





class VirtualMachine:
    def run(self, code_obj: types.CodeType) -> None:
        """
        :param code_obj: code for interpreting
        """
        globals_context: dict[str, tp.Any] = {}
        frame = Frame(code_obj, builtins.globals()['__builtins__'], globals_context, globals_context)
        return frame.run()
