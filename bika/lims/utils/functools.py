# -*- coding: utf-8 -*-

import types


def fail(msg):
    """ Raises a RuntimeError with the given error Message

        >>> fail("This failed badly")
        Traceback (most recent call last):
        ...
        RuntimeError: This failed badly
    """
    raise RuntimeError("{0}".format(msg))


def truthy(thing):
    """ checks if a value is True or not None

        >>> truthy(0)
        True
        >>> truthy({})
        True
        >>> truthy([])
        True
        >>> truthy(None)
        False
        >>> truthy(False)
        False
    """
    if thing is False or thing is None:
        return False
    return True


def falsy(thing):
    """ checks if a value is False or None

        >>> falsy(0)
        False
        >>> falsy({})
        False
        >>> falsy([])
        False
        >>> falsy(None)
        True
        >>> falsy(False)
        True
    """
    return not truthy(thing)


def is_string(thing):
    """ checks if an object is a string/unicode type

        >>> is_string("")
        True
        >>> is_string(u"")
        True
        >>> is_string(str())
        True
        >>> is_string(unicode())
        True
        >>> is_string(1)
        False
    """
    return type(thing) in types.StringTypes


def is_list(thing):
    """ checks if an object is a list type

        >>> is_list([])
        True
        >>> is_list(list())
        True
        >>> is_list("[]")
        False
        >>> is_list({})
        False
    """
    return isinstance(thing, types.ListType)


def is_tuple(thing):
    """ checks if an object is a tuple type

        >>> is_tuple(())
        True
        >>> is_tuple(tuple())
        True
        >>> is_tuple("()")
        False
        >>> is_tuple([])
        False
    """
    return isinstance(thing, types.TupleType)


def is_dict(thing):
    """ checks if an object is a dictionary type

        >>> is_dict({})
        True
        >>> is_dict(dict())
        True
        >>> is_dict("{}")
        False
        >>> is_dict([])
        False
    """
    return isinstance(thing, types.DictType)


def is_digit(thing):
    """ checks if an object is a digit

        >>> is_digit(1)
        True
        >>> is_digit("1")
        True
        >>> is_digit("a")
        False
        >>> is_digit([])
        False
    """
    return str(thing).isdigit()


def to_int(thing):
    """ coverts an object to int

        >>> to_int("0")
        0
        >>> to_int(1)
        1
        >>> to_int("1")
        1
        >>> to_int("a")

    """
    if is_digit(thing):
        return int(thing)
    return None


def to_string(thing):
    """ coverts an object to string

        >>> to_string(1)
        '1'
        >>> to_string([])
        '[]'
        >>> to_string(u"a")
        'a'
    """
    return str(thing) or None


def to_list(thing):
    """ converts an object to a list

        >>> to_list(1)
        [1]

        >>> to_list([1,2,3])
        [1, 2, 3]

        >>> to_list(("a", "b", "c"))
        ['a', 'b', 'c']

        >>> to_list(dict(a=1, b=2))
        [{'a': 1, 'b': 2}]

        >>> to_list(None)
        []
    """
    if thing is None:
        return []
    if not (is_list(thing) or is_tuple(thing)):
        return [thing]
    return list(thing)


def convert(value, converter):
    """ Converts a value with a given converter function.

        >>> convert("1", to_int)
        1
        >>> convert("0", to_int)
        0
        >>> convert("a", to_int)

    """
    if not callable(converter):
        fail("Converter must be a function")
    return converter(value)


def pluck(col, key, default=None):
    """ Extracts a list of values from a collection of dictionaries

        >>> stooges = [{"name": "moe",   "age": 40},
        ...            {"name": "larry", "age": 50},
        ...            {"name": "curly", "age": 60}]
        >>> pluck(stooges, "name")
        ['moe', 'larry', 'curly']

        It only works with collections

        >>> curly = stooges.pop()
        >>> pluck(curly, "age")
        Traceback (most recent call last):
        ...
        RuntimeError: First argument must be a list or tuple
    """
    if not (is_list(col) or is_tuple(col)):
        fail("First argument must be a list or tuple")

    def _block(dct):
        if not is_dict(dct):
            return []
        return dct.get(key, default)

    return map(_block, col)


def pick(dct, *keys):
    """ Returns a copy of the dictionary filtered to only have values for the
        whitelisted keys (or list of valid keys)

        >>> pick({"name": "moe", "age": 50, "userid": "moe1"}, "name", "age")
        {'age': 50, 'name': 'moe'}

    """
    copy = dict()
    for key in keys:
        if key in dct.keys():
            copy[key] = dct[key]
    return copy


def omit(dct, *keys):
    """ Returns a copy of the dictionary filtered to omit the blacklisted keys
        (or list of keys)

        >>> omit({"name": "moe", "age": 50, "userid": "moe1"}, "userid", "age")
        {'name': 'moe'}
    """
    copy = dict()
    for key in dct:
        if key not in keys:
            copy[key] = dct[key]
    return copy


def rename(dct, mapping):
    """ Rename the keys of a dictionary with the given mapping

        >>> rename({"a": 1, "BBB": 2}, {"a": "AAA"})
        {'AAA': 1, 'BBB': 2}
    """

    def _block(memo, key):
        if key in dct:
            memo[mapping[key]] = dct[key]
            return memo
        else:
            return memo
    return reduce(_block, mapping, omit(dct, *mapping.keys()))


def alias(col, mapping):
    """ Returns a collection of dictionaries with the keys renamed according to
        the mapping

        >>> libraries = [{"isbn": 1, "ed": 1}, {"isbn": 2, "ed": 2}]
        >>> alias(libraries, {"ed": "edition"})
        [{'edition': 1, 'isbn': 1}, {'edition': 2, 'isbn': 2}]

        >>> alias({"a": 1}, {"a": "b"})
        [{'b': 1}]
    """
    if not is_list(col):
        col = [col]

    def _block(dct):
        return rename(dct, mapping)

    return map(_block, col)


def first(lst, n=None):
    """ get the first element of a list

        >>> lst = [1, 2, 3, 4, 5]
        >>> first(lst)
        1
        >>> first(lst, 3)
        [1, 2, 3]
    """
    return n is None and lst[0] or lst[0:n]


if __name__ == '__main__':
    import doctest
    doctest.testmod(raise_on_error=False,
                    optionflags=doctest.ELLIPSIS |
                    doctest.NORMALIZE_WHITESPACE)
