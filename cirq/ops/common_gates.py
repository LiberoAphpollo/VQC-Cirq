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

"""Quantum gates that are commonly used in the literature."""
import math
from typing import Union, Tuple, Optional

import numpy as np

from cirq.ops import gate_features
from cirq.ops.partial_reflection_gate import PartialReflectionGate
from cirq.ops.raw_types import InterchangeableQubitsGate
from cirq.value import Symbol


class Rot11Gate(PartialReflectionGate,
                gate_features.TwoQubitGate,
                InterchangeableQubitsGate):
    """Phases the |11> state of two adjacent qubits by a fixed amount.

    A ParameterizedCZGate guaranteed to not be using the parameter key field.
    """

    def _with_half_turns(self,
                         half_turns: Union[Symbol, float] = 1.0
                         ) -> 'Rot11Gate':
        return Rot11Gate(half_turns=half_turns)

    def text_diagram_wire_symbols(self,
                                  qubit_count=None,
                                  use_unicode_characters=True,
                                  precision=3):
        return '@', 'Z'

    def _reflection_matrix(self):
        """See base class."""
        return np.diag([1, 1, 1, -1])

    def __str__(self):
        base = 'CZ'
        if self.half_turns == 1:
            return base
        return '{}**{}'.format(base, repr(self.half_turns))

    def __repr__(self) -> str:
        return self.__str__()


class RotXGate(PartialReflectionGate, gate_features.SingleQubitGate):
    """Fixed rotation around the X axis of the Bloch sphere."""

    def _with_half_turns(self,
                         half_turns: Union[Symbol, float] = 1.0
                         ) -> 'RotXGate':
        return RotXGate(half_turns=half_turns)

    def text_diagram_wire_symbols(self,
                                  qubit_count=None,
                                  use_unicode_characters=True,
                                  precision=3):
        return 'X',

    def _reflection_matrix(self):
        return np.array([[0, 1], [1, 0]])

    def __repr__(self) -> str:
        return self.__str__()


class RotYGate(PartialReflectionGate, gate_features.SingleQubitGate):
    """Fixed rotation around the Y axis of the Bloch sphere."""

    def _with_half_turns(self,
                         half_turns: Union[Symbol, float] = 1.0
                         ) -> 'RotYGate':
        return RotYGate(half_turns=half_turns)

    def text_diagram_wire_symbols(self,
                                  qubit_count=None,
                                  use_unicode_characters=True,
                                  precision=3):
        return 'Y',

    def _reflection_matrix(self):
        return np.array([[0, -1j], [1j, 0]])

    def __repr__(self) -> str:
        return self.__str__()


class RotZGate(PartialReflectionGate, gate_features.SingleQubitGate):
    """Fixed rotation around the Z axis of the Bloch sphere."""

    def _with_half_turns(self,
                         half_turns: Union[Symbol, float] = 1.0
                         ) -> 'RotZGate':
        return RotZGate(half_turns=half_turns)

    def text_diagram_wire_symbols(self,
                                  qubit_count=None,
                                  use_unicode_characters=True,
                                  precision=3):
        return 'Z',

    def phase_by(self, phase_turns, qubit_index):
        return self

    def _reflection_matrix(self):
        return np.diag([1, -1])

    def __repr__(self) -> str:
        return self.__str__()


class MeasurementGate(gate_features.TextDiagrammableGate):
    """Indicates that qubits should be measured plus a key to identify results.

    Params:
        key: The string key of the measurement.
        invert_mask: A list of Truthy or Falsey values indicating whether
        the corresponding qubits should be flipped. None indicates no
        inverting should be done.
    """

    def __init__(self,
                 key: str = '',
                 invert_mask: Optional[Tuple[bool, ...]] = None) -> None:
        self.key = key
        self.invert_mask = invert_mask

    def text_diagram_wire_symbols(self,
                                  qubit_count=None,
                                  use_unicode_characters=True,
                                  precision=3):
        return 'M',

    def __repr__(self):
        return 'MeasurementGate({}, {})'.format(repr(self.key),
                                                repr(self.invert_mask))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.key == other.key and self.invert_mask == other.invert_mask

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((MeasurementGate, self.key, self.invert_mask))


X = RotXGate()  # Pauli X gate.
Y = RotYGate()  # Pauli Y gate.
Z = RotZGate()  # Pauli Z gate.
CZ = Rot11Gate()  # Negates the amplitude of the |11> state.

S = Z**0.5
T = Z**0.25


class HGate(gate_features.TextDiagrammableGate,
            gate_features.CompositeGate,
            gate_features.SelfInverseGate,
            gate_features.KnownMatrixGate,
            gate_features.SingleQubitGate):
    """180 degree rotation around the X+Z axis of the Bloch sphere."""

    def text_diagram_wire_symbols(self,
                                  qubit_count=None,
                                  use_unicode_characters=True,
                                  precision=3):
        return 'H',

    def default_decompose(self, qubits):
        q = qubits[0]
        yield Y(q)**0.5
        yield X(q)

    def matrix(self):
        """See base class."""
        s = math.sqrt(0.5)
        return np.array([[s, s], [s, -s]])

    def __repr__(self):
        return 'H'


H = HGate()  # Hadamard gate.


class CNotGate(gate_features.TextDiagrammableGate,
               gate_features.CompositeGate,
               gate_features.KnownMatrixGate,
               gate_features.SelfInverseGate,
               gate_features.TwoQubitGate):
    """A controlled-NOT. Toggle the second qubit when the first qubit is on."""

    def matrix(self):
        """See base class."""
        return np.array([[1, 0, 0, 0],
                         [0, 1, 0, 0],
                         [0, 0, 0, 1],
                         [0, 0, 1, 0]])

    def text_diagram_wire_symbols(self,
                                  qubit_count=None,
                                  use_unicode_characters=True,
                                  precision=3):
        return '@', 'X'

    def default_decompose(self, qubits):
        """See base class."""
        c, t = qubits
        yield Y(t)**-0.5
        yield CZ(c, t)
        yield Y(t)**0.5

    def __repr__(self):
        return 'CNOT'


CNOT = CNotGate()  # Controlled Not Gate.


class SwapGate(gate_features.TextDiagrammableGate,
               gate_features.CompositeGate,
               gate_features.SelfInverseGate,
               gate_features.KnownMatrixGate,
               gate_features.TwoQubitGate,
               InterchangeableQubitsGate):
    """Swaps two qubits."""

    def matrix(self):
        """See base class."""
        return np.array([[1, 0, 0, 0],
                         [0, 0, 1, 0],
                         [0, 1, 0, 0],
                         [0, 0, 0, 1]])

    def default_decompose(self, qubits):
        """See base class."""
        a, b = qubits
        yield CNOT(a, b)
        yield CNOT(b, a)
        yield CNOT(a, b)

    def __repr__(self):
        return 'SWAP'

    def text_diagram_wire_symbols(self,
                                  qubit_count=None,
                                  use_unicode_characters=True,
                                  precision=3):
        if not use_unicode_characters:
            return 'swap', 'swap'
        return '×', '×'


SWAP = SwapGate()  # Exchanges two qubits' states.
