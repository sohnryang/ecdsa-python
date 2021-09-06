def inv_mod(n: int, p: int):
    """
    Find a inverse of n mod p.

    :param n: Value of n where nx === 1 (mod p)
    :param p: Value of p where nx === 1 (mod p)
    :returns: Value of x where nx === 1 (mod p)
    """
    return pow(n, -1, p)


def legendre(a: int, p: int) -> int:
    """
    Calculate value of Legendre symbol (a/p).

    :param a: Value of a in (a/p).
    :param p: Value of p in (a/p).
    :returns: Value of (a/p).
    """
    return pow(a, (p - 1) // 2, p)


def tonelli(n: int, p: int):
    """
    Find a square root of n modulo p.

    :param n: Value of n where r^2 === n (mod p).
    :param p: Value of p where r^2 === n (mod p).
    :returns: Value of r where r^2 === n (mod p).
    :raises AssertionError: Assertion fails when n is not a square number, or
    non-quadratic residue mod p is not found in Z/pZ.
    """
    assert legendre(n, p) == 1, "not a square (mod p)"
    Q = p - 1
    S = 0  # p - 1 = Q * 2 ** S, Q is odd
    while Q % 2 == 0:
        S += 1
        Q //= 2

    z = 1
    while legendre(z, p) != p - 1:
        z += 1
    assert z != 0, "non-quadratic residue mod p not found"

    M = S
    c = pow(z, Q, p)
    t = pow(n, Q, p)
    R = pow(n, (Q + 1) // 2, p)
    while t != 0 and t != 1:
        i = 0
        z = t
        while z != 1 and i < M - 1:
            z = pow(z, 2, p)
            i += 1
        b = c
        for _ in range(M - i - 1, 0, -1):
            b = pow(b, 2, p)
        M = i
        c = pow(b, 2, p)
        t = t * pow(b, 2, p) % p
        R = R * b % p
    if t == 0:
        return 0
    else:
        return R
