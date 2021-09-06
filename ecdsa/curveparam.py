from .data_conversion import octet_str_to_int, octet_str_to_point


class CurveParam:
    def __init__(self, name: str, p: str, a: str, b: str, G: str, n: str, h: str):
        """
        Initialize a CurveParam object.

        :param p: An octet string representation of p specifying the field F_p.
        :param a: An octet string representation of the coeff. a of EC.
        :param b: An octet string representation of the coeff. b of EC.
        :param G: An octet string representation of the base point G.
        :param n: An octet string representation of the group order n.
        :param h: An octet string representation of the cofactor h.
        """
        self.name = name
        self.params = {
            "p": octet_str_to_int(p),
            "a": octet_str_to_int(a),
            "b": octet_str_to_int(b),
            "n": octet_str_to_int(n),
            "h": octet_str_to_int(h),
        }
        assert 4 * (self.params["a"] ** 3) + 27 * (self.params["b"] ** 2) != 0
        self.basepoint = octet_str_to_point(G, self.params)


secp256r1 = CurveParam(
    "secp256r1",
    "FFFFFFFF 00000001 00000000 00000000 00000000 FFFFFFFF FFFFFFFF FFFFFFFF",
    "FFFFFFFF 00000001 00000000 00000000 00000000 FFFFFFFF FFFFFFFF FFFFFFFC",
    "5AC635D8 AA3A93E7 B3EBBD55 769886BC 651D06B0 CC53B0F6 3BCE3C3E 27D2604B",
    "03 6B17D1F2 E12C4247 F8BCE6E5 63A440F2 77037D81 2DEB33A0 F4A13945 D898C296",
    "FFFFFFFF 00000000 FFFFFFFF FFFFFFFF BCE6FAAD A7179E84 F3B9CAC2 FC632551",
    "01",
)
