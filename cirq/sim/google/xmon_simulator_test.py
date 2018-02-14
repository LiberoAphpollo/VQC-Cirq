# Copyright 2018 Google LLC
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

"""Tests for xmon_simulator."""

import numpy as np
import pytest

from cirq import circuits
from cirq import ops
from cirq.sim.google import xmon_simulator
from cirq.google import ExpWGate, ExpZGate, Exp11Gate, XmonMeasurementGate

Q1 = ops.QubitLoc(0, 0)
Q2 = ops.QubitLoc(1, 0)


def basic_circuit():
    sqrt_x = ExpWGate(half_turns=0.5, axis_half_turns=0.0)
    z = ExpZGate()
    cz = Exp11Gate()
    circuit = circuits.Circuit()
    circuit.append(
        [sqrt_x(Q1), sqrt_x(Q2),
         cz(Q1, Q2),
         sqrt_x(Q1), sqrt_x(Q2),
         z(Q1)])
    return circuit


def large_circuit():
    np.random.seed(0)
    qubits = [ops.QubitLoc(i, 0) for i in range(10)]
    sqrt_x = ExpWGate(half_turns=0.5, axis_half_turns=0.0)
    cz = Exp11Gate()
    circuit = circuits.Circuit()
    for _ in range(11):
        circuit.append(
            [sqrt_x(qubit) for qubit in qubits if np.random.random() < 0.5])
        circuit.append([cz(qubits[i], qubits[i + 1]) for i in range(9)])
    for i in range(10):
        circuit.append(
            XmonMeasurementGate(key='meas')(qubits[i]))
    return circuit


def test_xmon_options_negative_num_shards():
    with pytest.raises(AssertionError):
        xmon_simulator.Options(num_shards=-1)


def test_xmon_options_negative_min_qubits_before_shard():
    with pytest.raises(AssertionError):
        xmon_simulator.Options(min_qubits_before_shard=-1)


def test_xmon_options():
    options = xmon_simulator.Options(num_shards=3, min_qubits_before_shard=0)
    assert options.num_prefix_qubits == 1
    assert options.min_qubits_before_shard == 0


def test_run_no_results():
    simulator = xmon_simulator.Simulator()
    result = simulator.run(basic_circuit())
    assert len(result.measurements) == 0


def test_run():
    np.random.seed(0)
    circuit = basic_circuit()
    circuit.append(
        [XmonMeasurementGate(key='a')(Q1),
         XmonMeasurementGate(key='b')(Q2),])

    simulator = xmon_simulator.Simulator()
    result = simulator.run(circuit)
    assert result.measurements == {'a': [False], 'b': [False]}


def test_run_state():
    simulator = xmon_simulator.Simulator()
    result = simulator.run(basic_circuit(), qubits=[Q1, Q2])
    np.testing.assert_almost_equal(result.state(),
                                   np.array([-0.5j, 0.5, -0.5, 0.5j]))


def test_run_state_different_order_of_qubits():
    simulator = xmon_simulator.Simulator()
    result = simulator.run(basic_circuit(), qubits=[Q2, Q1])
    np.testing.assert_almost_equal(result.state(),
                                   np.array([-0.5j, -0.5, 0.5, 0.5j]))


def test_run_sharded():
    circuit = large_circuit()

    simulator = xmon_simulator.Simulator()
    result = simulator.run(circuit)
    assert result.measurements == {
        'meas': [False, False, False, True, False, False, True, False, False,
                 True]}


def test_run_no_sharding():
    circuit = large_circuit()

    simulator = xmon_simulator.Simulator()
    result = simulator.run(circuit, xmon_simulator.Options(num_shards=1))
    assert result.measurements == {
        'meas': [False, False, False, True, False, False, True, False, False,
                 True]}


def test_run_no_sharing_few_qubits():
    np.random.seed(0)
    circuit = basic_circuit()
    circuit.append(
        [XmonMeasurementGate(key='a')(Q1),
         XmonMeasurementGate(key='b')(Q2),])

    simulator = xmon_simulator.Simulator()
    options = xmon_simulator.Options(min_qubits_before_shard=0)
    result = simulator.run(circuit, options=options)
    assert result.measurements == {'a': [False], 'b': [False]}


def test_run_set_state_computational_basis():
    simulator = xmon_simulator.Simulator()
    result = simulator.run(basic_circuit(), qubits=[Q1, Q2])
    result.set_state(0)
    np.testing.assert_almost_equal(result.state(), np.array([1, 0, 0, 0]))


def test_run_set_state_nd_array_fail():
    simulator = xmon_simulator.Simulator()
    result = simulator.run(basic_circuit(), qubits=[Q1, Q2])
    with pytest.raises(ValueError):
        result.set_state(np.array([0.5, 0.5, 0.5, -0.5], dtype=np.float32))


def test_moment_steps_no_results():
    simulator = xmon_simulator.Simulator()
    for step in simulator.moment_steps(basic_circuit()):
        assert len(step.measurements) == 0


def test_moment_steps():
    np.random.seed(0)
    circuit = basic_circuit()
    circuit.append(
        [XmonMeasurementGate(key='a')(Q1),
         XmonMeasurementGate(key='b')(Q2),])

    simulator = xmon_simulator.Simulator()
    results = []
    for step in simulator.moment_steps(circuit):
        results.append(step)
    expected = [{}, {}, {}, {'b': [False]}, {'a': [False]}]
    assert len(results) == len(expected)
    assert all(a.measurements == b for a, b in zip(results, expected))


def test_moment_steps_state():
    np.random.seed(0)
    circuit = basic_circuit()

    simulator = xmon_simulator.Simulator()
    results = []
    for step in simulator.moment_steps(circuit, qubits=[Q1, Q2]):
        results.append(step.state())
    np.testing.assert_almost_equal(results,
                                   np.array([[0.5, 0.5j, 0.5j, -0.5],
                                             [0.5, 0.5j, 0.5j, 0.5],
                                             [-0.5, 0.5j, 0.5j, -0.5],
                                             [-0.5j, 0.5, -0.5, 0.5j]]))

def test_moment_steps_set_state():
    np.random.seed(0)
    circuit = basic_circuit()

    simulator = xmon_simulator.Simulator()
    step = simulator.moment_steps(circuit, qubits=[Q1, Q2])

    result = step.__next__()
    result.set_state(0)
    np.testing.assert_almost_equal(result.state(), np.array([1, 0, 0, 0]))
