"""
A Python module for creating, validating, parsing, and manipulating tokens that are base-62 encoded.

This module provides several functions:
- register_generation: Adds a new character to the set of valid generations.
- _b62_encode and _b62_decode: Functions for converting between integer and base-62 representations.
- new: Generates a new token with a given prefix, generation character, timestamp, and entropy part.
- is_valid: Validates tokens by checking their character sets and structure.
- parse: Parses a token into a named tuple (prefix, generation, timestamp, entropy).
- swap_prefix: Changes the prefix in a given token to a new prefix.

The tokens generated by this module are unique, contain a timestamp, and can be used for various
purposes such as access tokens, event tokens, etc. in various applications.

The module also contains a nested class, ParsedToken, which is a named tuple useful for returning
multiple values and referencing them with readable attribute names.
"""

import datetime
import random
import typing


B62_CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

_VALID_GENERATIONS = set('0')


def register_generation(generation: str) -> None:
    """
    Function adds a given generation to the set of valid generations.
    Throws a ValueError if the generation is more than a single character.

    :param generation: A string character representing the generation
    """
    if len(generation) > 1:
        raise ValueError("Generation must be a single character.")
    _VALID_GENERATIONS.add(generation)


def _b62_encode(n: int) -> str:
    """
    Encodes a given integer into a base 62 string. Returns "0" if not integer is given.

    :param n: An integer to encode
    :return: The base-62 encoded string of the input integer
    """
    chars = []
    while n > 0:
        n, r = divmod(n, 62)
        chars.insert(0, B62_CHARSET[r])

    if not chars:
        return "0"

    return "".join(chars)


def _b62_decode(encoded: str) -> int:
    """
    Decodes a base 62 string into an integer.

    :param n: A base 62 string
    :return: The integer represented by the input string
    """
    l, i, v = len(encoded), 0, 0
    for x in encoded:
        v += B62_CHARSET.index(x) * (62 ** (l - (i + 1)))
        i += 1

    return v


def new(prefix: str, generation: str = '0', timestamp: typing.Union[float, None] = None, entropy: typing.Union[str,int] = 10) -> str:
    """
    Generates a new token with a given prefix, generation, timestamp, and entropy.
    Throws a ValueError if the given generation is not valid.

    :param prefix: A string representing the prefix of the token
    :param generation: A string representing the generation of the token
    :param timestamp: A float timestamp to use in the token
    :param entropy: Integer determining size of entropy part of token, or string to use as entropy
    :return: A string representing the generated token
    """
    if generation not in _VALID_GENERATIONS:
        raise ValueError("Generation must be one of {_VALID_GENERATIONS}")
    ts = timestamp or datetime.datetime.now().timestamp()
    ts = int(ts)
    ts_encoded = _b62_encode(ts).zfill(8)
    if isinstance(entropy, int):
        entropy_str = ''.join(random.sample(B62_CHARSET, entropy))
    elif isinstance(entropy, str):
        entropy_str = entropy
    else:
        raise ValueError("Entropy must be either an integer or a string")
    return f"{prefix}_{generation}{ts_encoded}{entropy_str}"


def is_valid(token: str) -> bool:
    """
    Checks if a given token is valid by checking its characters and structure.

    :param token: String potentially being a token
    :return: A Boolean representing whether the input string is a valid token
    """
    last_delimiter = token.rfind('_')
    prefix, suffix = token[:last_delimiter], token[last_delimiter + 1:]
    for char in prefix:
        if char not in B62_CHARSET and char != '_':
            return False
    for char in suffix:
        if char not in B62_CHARSET:
            return False

    return True


class ParsedToken(typing.NamedTuple):
    """
    Creates a named tuple ParsedToken containing four fields:
    prefix: A string representing the prefix of the token
    generation: A string representing the generation of the token
    timestamp: A float representing the timestamp of the token
    entropy: A string representing the entropy of the token
    """
    prefix: str
    generation: str
    timestamp: float
    entropy: str


def parse(token: str) -> typing.Union[ParsedToken, None]:
    """
    Parses a token. If the token is valid, returns a ParsedToken instance, else returns None.

    :param token: A string representing the token to parse
    :return: An instance of the ParsedToken class
    """
    if not is_valid(token):
        return None
    last_delimiter = token.rfind('_')
    prefix, suffix = token[:last_delimiter], token[last_delimiter + 1:]
    ts_part = suffix[1:9]

    return ParsedToken(
        prefix=prefix,
        generation=suffix[0],
        timestamp=float(_b62_decode(ts_part.lstrip('0'))),
        entropy=suffix[9:]
    )


def swap_prefix(token: str, new_prefix: str) -> str:
    """
    Swaps the prefix of a given token with a new prefix.

    :param token: A string representing the original token
    :param new_prefix: A string representing the new prefix for the token
    :return: A string representing the token with the new prefix
    """
    suffix = token[token.rfind('_') + 1:]
    return new_prefix + '_' + suffix