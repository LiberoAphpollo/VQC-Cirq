# Copyright 2018 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import fractions
from typing import Tuple, Union, List, Optional, cast, TypeVar, NamedTuple, \
    Iterable

import abc

import numpy as np

from cirq import value, protocols
from cirq.ops import raw_types
from cirq.type_workarounds import NotImplementedType


TSelf = TypeVar('TSelf', bound='EigenGate')


EigenComponent = NamedTuple(
    'EigenComponent',
    [
        # The θ in λ = exp(i π θ) where λ is a unique eigenvalue. The exponent
        # factor is used, instead of just a raw unit complex number, because it
        # disambiguates several cases. For example, when λ=-1 you can set θ to
        # -1 instead of +1 resulting in square root operations returning -i
        # instead of +1.
        ('eigenvalue_exponent_factor', float),

        # The projection matrix onto the eigenspace of the eigenvalue. Must
        # equal Σ_k |λ_k⟩⟨λ_k| where the |λ_k⟩ vectors form an orthonormal
        # basis for the eigenspace.
        ('eigenspace_projector', np.ndarray),
    ]
)


class EigenGate(raw_types.Gate):
    """A gate with a known eigendecomposition.

    EigenGate is particularly useful when one wishes for different parts of
    the same eigenspace to be extrapolated differently. For example, if a gate
    has a 2-dimensional eigenspace with eigenvalue -1, but one wishes for the
    square root of the gate to split this eigenspace into a part with
    eigenvalue i and a part with eigenvalue -i, then EigenGate allows this
    functionality to be unambiguously specified via the _eigen_components
    method.
    """

    def __init__(self, *,  # Forces keyword args.
                 exponent: Union[value.Symbol, float] = 1.0,
                 global_shift: float = 0.0) -> None:
        """Initializes the parameters used to compute the gate's matrix.

        The eigenvalue of an eigenspace of the gate is computed by:
        1. Starting with an angle returned by the _eigen_components method.
            θ
        2. Shifting the angle by the global_shift.
            θ + s
        3. Scaling the angle by the exponent.
            (θ + s) * e
        4. Converting from half turns to a complex number on the unit circle.
            exp(i * pi * (θ + s) * e)

        Args:
            exponent: How much to scale the eigencomponents' angles by when
                computing the gate's matrix.
            global_shift: Offsets the eigenvalues of the gate at exponent=1.
                In effect, this controls a global phase factor on the gate's
                unitary matrix. The factor is:

                    exp(i * pi * global_shift * exponent)

                For example, `cirq.X**t` uses a `global_shift` of 0 but
                `cirq.Rx(t)` uses a `global_shift` of -0.5, which is why
                `cirq.unitary(cirq.Rx(pi))` equals -iX instead of X.
        """
        self._exponent = exponent
        self._global_shift = global_shift
        self._canonical_exponent_cached = None

    # virtual method
    def _with_exponent(self: TSelf,
                       exponent: Union[value.Symbol, float]) -> TSelf:
        """Return the same kind of gate, but with a different exponent.

        Child classes should override this method if they have an __init__
        method with a differing signature.
        """
        # pylint: disable=unexpected-keyword-arg
        if self._global_shift == 0:
            return type(self)(exponent=exponent)
        return type(self)(
            exponent=exponent,
            global_shift=self._global_shift)
        # pylint: enable=unexpected-keyword-arg

    @abc.abstractmethod
    def _eigen_components(self) -> List[Union[EigenComponent,
                                              Tuple[float, np.ndarray]]]:
        """Describes the eigendecomposition of the gate's matrix.

        Returns:
            A list of EigenComponent tuples. Each tuple in the list
            corresponds to one of the eigenspaces of the gate's matrix. Each
            tuple has two elements. The first element of a tuple is the θ in
            λ = exp(i π θ) (where λ is the eigenvalue of the eigenspace). The
            second element is a projection matrix onto the eigenspace.

        Examples:
            The Pauli Z gate's eigencomponents are:

                [
                    (0, np.array([[1, 0],
                                  [0, 0]])),
                    (1, np.array([[0, 0],
                                  [0, 1]])),
                ]

            Valid eigencomponents for Rz(π) = -iZ are:

                [
                    (-0.5, np.array([[1, 0],
                                    [0, 0]])),
                    (+0.5, np.array([[0, 0],
                                     [0, 1]])),
                ]

            But in principle you could also use this:

                [
                    (+1.5, np.array([[1, 0],
                                    [0, 0]])),
                    (-0.5, np.array([[0, 0],
                                     [0, 1]])),
                ]

                The choice between -0.5 and +1.5 does not affect the gate's
                matrix, but it does affect the matrix of powers of the gates
                (because (x+2)*s != x*s (mod 2) when s is a real number).

            The Pauli X gate's eigencomponents are:

                [
                    (0, np.array([[0.5, 0.5],
                                  [0.5, 0.5]])),
                    (1, np.array([[+0.5, -0.5],
                                  [-0.5, +0.5]])),
                ]
        """
        pass

    def _period(self) -> Optional[float]:
        """Determines how the exponent parameter is canonicalized when equating.

        Returns:
            None if the exponent should not be canonicalized. Otherwise a float
            indicating the period of the exponent. If the period is p, then a
            given exponent will be shifted by p until it is in the range
            (-p/2, p/2] during initialization.
        """
        exponents = [e + self._global_shift
                     for e, _ in self._eigen_components()]
        real_periods = [abs(2/e) for e in exponents if e != 0]
        return _approximate_common_period(real_periods)

    def __pow__(self: TSelf, exponent: Union[float, value.Symbol]) -> TSelf:
        new_exponent = protocols.mul(self._exponent, exponent, NotImplemented)
        if new_exponent is NotImplemented:
            return NotImplemented
        return self._with_exponent(exponent=new_exponent)

    @property
    def _canonical_exponent(self):
        if self._canonical_exponent_cached is None:
            period = self._period()
            if not period or isinstance(self._exponent, value.Symbol):
                self._canonical_exponent_cached = self._exponent
            else:
                self._canonical_exponent_cached = self._exponent % period
        return self._canonical_exponent_cached

    def _identity_tuple(self):
        return (type(self),
                self._canonical_exponent,
                self._global_shift)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._identity_tuple() == other._identity_tuple()

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self._identity_tuple())

    def _trace_distance_bound_(self):
        if isinstance(self._exponent, value.Symbol):
            return 1

        angles = [half_turns for half_turns, _ in self._eigen_components()]
        min_angle = min(angles)
        max_angle = max(angles)
        return abs((max_angle - min_angle) * self._exponent * 3.5)

    def _has_unitary_(self) -> bool:
        return not self._is_parameterized_()

    def _unitary_(self) -> Union[np.ndarray, NotImplementedType]:
        if self._is_parameterized_():
            return NotImplemented
        e = cast(float, self._exponent)
        return np.sum([
            component * 1j**(
                    2 * e * (half_turns + self._global_shift))
            for half_turns, component in self._eigen_components()
        ], axis=0)

    def _is_parameterized_(self) -> bool:
        return isinstance(self._exponent, value.Symbol)

    def _resolve_parameters_(self: TSelf, param_resolver) -> TSelf:
        return self._with_exponent(
                exponent=param_resolver.value_of(self._exponent))


def _lcm(vals: Iterable[int]) -> int:
    t = 1
    for r in vals:
        t = t * r // fractions.gcd(t, r)
    return t


def _approximate_common_period(periods: List[float],
                               approx_denom: int = 60,
                               reject_atol: float = 1e-8) -> Optional[float]:
    """Finds a value that is nearly an integer multiple of multiple periods.

    The returned value should be the smallest non-negative number with this
    property. If `approx_denom` is too small the computation can fail to satisfy
    the `reject_atol` criteria and return `None`. This is actually desirable
    behavior, since otherwise the code would e.g. return a nonsense value when
    asked to compute the common period of `np.e` and `np.pi`.

    Args:
        periods: The result must be an approximate integer multiple of each of
            these.
        approx_denom: Determines how the floating point values are rounded into
            rational values (so that integer methods such as lcm can be used).
            Each floating point value f_k will be rounded to a rational number
            of the form n_k / approx_denom. If you want to recognize rational
            periods of the form i/d then d should divide `approx_denom`.
        reject_atol: If the computed approximate common period is at least this
            far from an integer multiple of any of the given periods, then it
            is discarded and `None` is returned instead.

    Returns:
        The approximate common period, or else `None` if the given
        `approx_denom` wasn't sufficient to approximate the common period to
        within the given `reject_atol`.
    """
    if not periods:
        return None
    if any(e == 0 for e in periods):
        return None
    approx_rational_periods = [
        fractions.Fraction(int(np.round(p * approx_denom)), approx_denom)
        for p in periods
    ]
    common = float(_common_rational_period(approx_rational_periods))

    for p in periods:
        if p != 0 and abs(p * np.round(common / p) - common) > reject_atol:
            return None

    return common


def _common_rational_period(rational_periods: List[fractions.Fraction]
                            ) -> fractions.Fraction:
    """Finds the least common integer multiple of some fractions.

    The solution is the smallest positive integer c such that there
    exists integers n_k satisfying p_k * n_k = c for all k.
    """
    assert rational_periods, "no well-defined solution for an empty list"
    common_denom = _lcm(p.denominator for p in rational_periods)
    int_periods = [p.numerator * common_denom // p.denominator
                   for p in rational_periods]
    int_common_period = _lcm(int_periods)
    return fractions.Fraction(int_common_period, common_denom)
