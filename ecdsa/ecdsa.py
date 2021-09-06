from math import ceil, log2
import secrets
from typing import Callable, Optional, Tuple
from .curvepoint import CurvePoint
from .curveparam import CurveParam
from .data_conversion import octet_list_to_int, octet_str_to_octet_list
from .numbertheory import inv_mod


class ECDSA:
    def __init__(
        self,
        curve: CurveParam,
        hash_func: Callable,
        key_pair: Optional[Tuple[Optional[int], CurvePoint]] = None,
    ):
        """
        Initalize ECDSA.

        :param curve: Curve used to sign.
        :param key_pair: Key pair to use. Private key can be None if the object
        is not intended for signature creation.
        """
        self.curve = curve
        self.hash_func = hash_func
        self.G = CurvePoint(curve, pos=self.curve.basepoint)
        if key_pair == None:
            self.d_U, self.Q_U = self.create_key_pair()
        else:
            self.d_U, self.Q_U = key_pair

    def create_key_pair(self) -> Tuple[int, CurvePoint]:
        """
        Create an ECDSA key pair.

        :returns: ECDSA key pair (d, Q).
        """
        d = secrets.randbelow(self.curve.params["p"] - 1) + 1
        Q = d * self.G
        return (d, Q)

    def create_sign(self, message: bytes) -> Tuple[int, int]:
        """
        Create a signature for message.

        :param message: The message to sign.
        :returns: signature (r, s).
        :raises AssertionError: Assertion fails when private key is None.
        """
        assert self.d_U != None
        r = 0
        k = 0
        R = CurvePoint(self.curve, pos=(0, 0))
        r = 0
        while r == 0:
            k, R = self.create_key_pair()
            x_R = R.x
            r = x_R % self.curve.params["n"]
        s = 0

        H = octet_str_to_octet_list(self.hash_func(message))
        H_bar = octet_list_to_int(H)
        n_bitlen = ceil(log2(self.curve.params["n"]))
        if n_bitlen >= 8 * len(H):
            e = H_bar
        else:
            e = H_bar >> (8 * len(H) - n_bitlen)

        s = (
            inv_mod(k, self.curve.params["n"])
            * (e + r * self.d_U)
            % self.curve.params["n"]
        )
        return (r, s)

    def verify_sign(self, message: bytes, signature: Tuple[int, int]) -> bool:
        """
        Verify a signature for message.

        :param message: The message for verification.
        :param signature: The signature to verify.
        :return: True if signature is valid, and False if invalid.
        """
        r, s = signature
        if not 1 <= r <= (self.curve.params["n"] - 1):
            return False
        if not 1 <= s <= (self.curve.params["n"] - 1):
            return False

        H = octet_str_to_octet_list(self.hash_func(message))
        H_bar = octet_list_to_int(H)
        n_bitlen = ceil(log2(self.curve.params["n"]))
        if n_bitlen >= 8 * len(H):
            e = H_bar
        else:
            e = H_bar >> (8 * len(H) - n_bitlen)

        u1 = e * inv_mod(s, self.curve.params["n"]) % self.curve.params["n"]
        u2 = r * inv_mod(s, self.curve.params["n"]) % self.curve.params["n"]

        R = u1 * self.G + u2 * self.Q_U
        if R.x == R.y == 0:
            return False

        x_R = R.x
        v = x_R % self.curve.params["n"]
        return v == r
