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

from typing import Optional

import numpy as np

from cirq import ops, decompositions, extension
from cirq.circuits.circuit import Circuit
from cirq.circuits.optimization_pass import (
    PointOptimizationSummary,
    PointOptimizer,
)
from cirq.contrib.paulistring.pauli_string_phasor import PauliStringPhasor


class ConvertToPauliStringPhasors(PointOptimizer):
    """Attempts to convert single-qubit gates into single-qubit
    PauliStringPhasor operations.

    Checks if the given extensions are able to cast the operation into a
        KnownMatrix. If so, and the gate is a 1-qubit gate, then decomposes it
        into x, y, or z rotations and creates a PauliStringPhasor for each.
    """

    def __init__(self,
                 ignore_failures: bool = False,
                 tolerance: float = 0,
                 extensions: extension.Extensions = None) -> None:
        """
        Args:
            ignore_failures: If set, gates that fail to convert are forwarded
                unchanged. If not set, conversion failures raise a TypeError.
            tolerance: Maximum absolute error tolerance. The optimization is
                permitted to round angles with a threshold determined by this
                tolerance.
            extensions: The extensions instance to use when trying to
                cast gates to known types.
        """
        self.extensions = extensions or extension.Extensions()
        self.ignore_failures = ignore_failures
        self.tolerance = tolerance

    def _matrix_to_pauli_string_phasors(self,
                                        mat: np.ndarray,
                                        qubit: ops.QubitId) -> ops.OP_TREE:
        rotations = decompositions.single_qubit_matrix_to_pauli_rotations(
                                       mat, self.tolerance)
        for pauli, half_turns in rotations:
            pauli_string = ops.PauliString.from_single(qubit, pauli)
            yield PauliStringPhasor(pauli_string, half_turns=half_turns)

    def _convert_one(self, op: ops.Operation) -> ops.OP_TREE:
        # Don't change if it's already a PauliStringPhasor
        if isinstance(op, PauliStringPhasor):
            return op

        # Single qubit gate with known matrix?
        mat = self.extensions.try_cast(ops.KnownMatrix, op)
        if mat is not None and len(op.qubits) == 1:
            return self._matrix_to_pauli_string_phasors(
                            mat.matrix(), op.qubits[0])

        # Just let it be?
        if self.ignore_failures:
            return op

        raise TypeError("Don't know how to work with {!r}. "
                        "It isn't a 1-qubit KnownMatrix.".format(op))

    def convert(self, op: ops.Operation) -> ops.OP_TREE:
        converted = self._convert_one(op)
        if converted is op:
            return converted
        return [self.convert(e) for e in ops.flatten_op_tree(converted)]

    def optimization_at(self, circuit: Circuit, index: int, op: ops.Operation
                        ) -> Optional[PointOptimizationSummary]:
        converted = self.convert(op)
        if converted is op:
            return None

        return PointOptimizationSummary(
            clear_span=1,
            new_operations=converted,
            clear_qubits=op.qubits)
