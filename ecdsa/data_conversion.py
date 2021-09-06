from itertools import zip_longest
from math import ceil, log2
from typing import Dict, Iterable, List, Tuple
from .numbertheory import tonelli


def octet_str_to_int(octet_str: str) -> int:
    """
    Convert octet string to integer.

    :param octet_str: Octet string to convert.
    :returns: Converted integer.
    """
    return int(octet_str.replace(" ", ""), 16)


def grouper(n: int, iterable: Iterable) -> List[int]:
    """
    Group iterable to list of n-tuples.

    :param n: Length of tuples.
    :param iterable: Iterable to group.
    :returns: Grouped iterable content.
    """
    return list(
        map(
            lambda x: int("".join(x), 16),
            zip_longest(*[iter(iterable)] * n, fillvalue=None),
        )
    )


def octet_str_to_octet_list(octet_str: str) -> List[int]:
    """
    Convert octet string to octet list.

    :param octet_str: Octet string to convert.
    :returns: Converted octet list.
    """
    stripped = "".join(octet_str.split())
    if len(stripped) % 2 != 0:
        stripped = "0" + stripped
    return grouper(2, stripped)


def octet_list_to_int(octet_list: List[int]) -> int:
    """
    Convert octet list to integer.

    :param octet_list: Octet list to convert.
    :returns: Converted integer.
    """
    result = 0
    for octet in octet_list:
        result <<= 8
        result += octet
    return result


def octet_list_to_field_elem(octet_list: List[int], p: int) -> int:
    """
    Convert octet list to field element. Note that field F_{2^m} is not
    supported in this implementation.

    :param octet_list: Octet list to convert.
    :param p: Order of group F_p.
    :returns: Converted integer, which is a field element.
    """
    elem = octet_list_to_int(octet_list)
    if not 0 <= elem < p:
        raise ValueError(f"Field F_{p} does not contain: {elem}")
    return elem


def field_elem_to_octet_list(elem: int) -> List[int]:
    """
    Convert an element of field F_p to octet list. Note that F_{2^m} is not
    supported in this implementation.

    :param elem: Element of field F_p
    :returns: Converted octet list.
    """
    octet_str = hex(elem).replace("0x", "", 1)
    if len(octet_str) % 2 != 0:
        octet_str = "0" + octet_str
    return grouper(2, octet_str)


def octet_str_to_point(octet_str: str, params: Dict[str, int]) -> Tuple[int, int]:
    """
    Convert octet string to EC point.

    :param octet_str: Octet string to convert.
    :param params: EC params p, a, b in dict form.
    :returns: Converted EC point (x, y).
    :raises ValueError: ValueError is raised when octet string is invalid.
    :raises NotImplementedError: Support for curve over F_(2^m) is not
    implemented.
    """
    octets = octet_str_to_octet_list(octet_str)
    if len(octets) == 1 and octets[0] == "00":
        return (0, 0)
    if len(octets) == ceil(log2(params["p"]) / 8) + 1:
        Y = octets[0]
        X = octets[1:]
        x_P = octet_list_to_field_elem(X, params["p"])
        if Y not in (2, 3):
            raise ValueError(f"Invalid Y value: {Y}")
        y_tilde_P = 0 if Y == 2 else 1
        if params["p"] % 2 == 0:
            raise NotImplementedError("Support for F_{2^m} is not implemented")
        alpha = (x_P ** 3 + params["a"] * x_P + params["b"]) % params["p"]
        beta = tonelli(alpha, params["p"])
        if (beta - y_tilde_P) % 2 == 0:
            y_P = beta
        else:
            y_P = params["p"] - beta
        return (x_P, y_P)
    elif len(octets) == 2 * ceil(log2(params["p"]) / 8) + 1:
        W = octets[0]
        coord_len = ceil(log2(params["p"]) / 8)
        X = octets[1 : coord_len + 1]
        Y = octets[coord_len + 1 :]
        if W != 4:
            raise ValueError(f"Invalid W value: {W}")
        x_P = octet_list_to_field_elem(X, params["p"])
        y_P = octet_list_to_field_elem(Y, params["p"])
        return (x_P, y_P)
    raise ValueError("Invalid octet string length")
