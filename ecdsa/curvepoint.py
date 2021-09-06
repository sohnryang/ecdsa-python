from typing import Optional, Tuple
from .curveparam import CurveParam
from .data_conversion import (
    field_elem_to_octet_list,
    octet_list_to_int,
    octet_str_to_point,
)
from .numbertheory import inv_mod
from math import floor, log2


class CurvePoint:
    def __init__(
        self,
        curve: CurveParam,
        x: Optional[int] = None,
        y: Optional[int] = None,
        pos: Optional[Tuple[int, int]] = None,
        octet_str: Optional[str] = None,
    ):
        """
        Initialize CurvePoint.

        :param curve: The curve this point belongs to.
        :param x: Optional. x-coordinate of this point.
        :param y: Optional. y-coordinate of this point.
        :param pos: Optional. (x, y)-cordinate of this point.
        :param octet_str: Optional. Octet string form of point.
        """
        if x != None and y != None:
            self.x = x
            self.y = y
        elif pos != None:
            self.x, self.y = pos
        elif octet_str != None:
            self.x, self.y = octet_str_to_point(octet_str, curve.params)
        else:
            raise ValueError("No point specified")
        self.curve = curve

    def __add__(self, another: "CurvePoint") -> "CurvePoint":
        """
        Add two CurvePoint objects.

        :param another: The point to add.
        :raises AssertionError: Assertion fails when two points are from
        different curves.
        :returns: Addition result of two points.
        """
        assert self.curve.params == another.curve.params
        if self.x == self.y == 0:
            return CurvePoint(self.curve, pos=(another.x, another.y))
        elif another.x == another.y == 0:
            return CurvePoint(self.curve, pos=(self.x, self.y))
        elif self.x == another.x:
            if self.y == another.y:
                lambda_ = (
                    (3 * self.x ** 2 + self.curve.params["a"])
                    * inv_mod(2 * self.y, self.curve.params["p"])
                    % self.curve.params["p"]
                )
                result_x = (lambda_ ** 2 - 2 * self.x) % self.curve.params["p"]
                result_y = (lambda_ * (self.x - result_x) - self.y) % self.curve.params[
                    "p"
                ]
                return CurvePoint(self.curve, x=result_x, y=result_y)
            return CurvePoint(self.curve, x=0, y=0)
        lambda_ = (
            (another.y - self.y)
            * inv_mod(another.x - self.x, self.curve.params["p"])
            % self.curve.params["p"]
        )
        result_x = (lambda_ ** 2 - self.x - another.x) % self.curve.params["p"]
        result_y = (lambda_ * (self.x - result_x) - self.y) % self.curve.params["p"]
        return CurvePoint(self.curve, pos=(result_x, result_y))

    def __rmul__(self, scalar: int) -> "CurvePoint":
        """
        Multply the point by scalar.

        :param scalar: The scalar to multiply the point with.
        :returns: Multiplication result.
        """
        if scalar < 0:
            return -((-scalar) * self)
        elif scalar == 0:
            return CurvePoint(self.curve, pos=(0, 0))
        result = CurvePoint(self.curve, pos=(0, 0))
        bitlen = floor(log2(scalar)) + 1
        for shift in range(bitlen - 1, -1, -1):
            bit = (scalar >> shift) & 1
            result += result
            if bit == 1:
                result += self
        return result

    def __neg__(self) -> "CurvePoint":
        """
        Negate the point.

        :returns: Negative of self.
        """
        return CurvePoint(self.curve, pos=(self.x, -self.y))

    def __eq__(self, another: "CurvePoint") -> bool:
        """
        Check equality of two points.

        :param another: The point to compare with.
        :returns: Equality check result.
        """
        return (
            self.x == another.x
            and self.y == another.y
            and self.curve.name == another.curve.name
        )

    def __repr__(self) -> str:
        """
        Get a representation of the point.

        :returns: Representation in string.
        """
        return (
            f"({self.x}, {self.y}) on curve "
            f"y^2 = x^3 + {self.curve.params['a']}x + {self.curve.params['b']}, "
            f"F_{self.curve.params['p']}"
        )

    def octet_str(self) -> str:
        """
        Serialize to compressed octet string form.
        """
        if self.x == self.y == 0:
            return "00"
        octet_list = []
        y_tilde_P = self.y % 2
        if y_tilde_P == 0:
            octet_list.append(2)
        else:
            octet_list.append(3)
        octet_list.extend(field_elem_to_octet_list(self.x))
        octet_str = hex(octet_list_to_int(octet_list)).replace("0x", "", 1)
        if len(octet_str) % 2 != 0:
            octet_str = "0" + octet_str
        return octet_str
