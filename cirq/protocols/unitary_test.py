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

import numpy as np
import pytest

import cirq


def test_unitary():
    m = np.array([[0, 1], [1, 0]])
    d = np.array([])

    class NoMethod:
        pass

    class ReturnsNotImplemented:
        def _unitary_(self):
            return NotImplemented

    class ReturnsMatrix:
        def _unitary_(self):
            return m

    with pytest.raises(TypeError, match='no _unitary_ method'):
        _ = cirq.unitary(NoMethod())
    with pytest.raises(TypeError, match='returned NotImplemented'):
        _ = cirq.unitary(ReturnsNotImplemented())
    assert cirq.unitary(ReturnsMatrix()) is m

    assert cirq.unitary(NoMethod(), None) is None
    assert cirq.unitary(ReturnsNotImplemented(), None) is None
    assert cirq.unitary(ReturnsMatrix(), None) is m

    assert cirq.unitary(NoMethod(), NotImplemented) is NotImplemented
    assert cirq.unitary(ReturnsNotImplemented(),
                        NotImplemented) is NotImplemented
    assert cirq.unitary(ReturnsMatrix(), NotImplemented) is m

    assert cirq.unitary(NoMethod(), 1) == 1
    assert cirq.unitary(ReturnsNotImplemented(), 1) == 1
    assert cirq.unitary(ReturnsMatrix(), 1) is m

    assert cirq.unitary(NoMethod(), d) is d
    assert cirq.unitary(ReturnsNotImplemented(), d) is d
    assert cirq.unitary(ReturnsMatrix(), d) is m


def test_compatibility_shim():
    m = np.array([[0, 1], [1, 0]])

    class Known(cirq.KnownMatrix):
        def matrix(self):
            return m

    class PotentiallyKnown(cirq.PotentialImplementation):
        def try_cast_to(self, desired_type, extensions):
            if desired_type is cirq.KnownMatrix:
                return Known()

    class PotentiallyUnknown(cirq.PotentialImplementation):
        def try_cast_to(self, desired_type, extensions):
            return None

    assert cirq.unitary(Known()) is m
    assert cirq.unitary(PotentiallyKnown()) is m
    assert cirq.unitary(PotentiallyUnknown(), None) is None

    # Works with existing gate.
    np.testing.assert_allclose(cirq.unitary(cirq.X), m)
    assert cirq.unitary(cirq.X**cirq.Symbol('a'), None) is None
