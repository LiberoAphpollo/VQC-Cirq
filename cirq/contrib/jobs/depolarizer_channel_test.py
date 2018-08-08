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

import cirq
from cirq.contrib.jobs import DepolarizerChannel, Job
from cirq.google import xmon_gates


def test_depolarizer_no_errors():
    q1 = cirq.QubitId()
    q2 = cirq.QubitId()
    cnot = Job(cirq.Circuit([
        cirq.Moment([cirq.CNOT(q1, q2)]),
        ]))
    no_errors = DepolarizerChannel(probability=0.0)

    assert no_errors.transform_job(cnot) == cnot


def test_depolarizer_all_errors():
    q1 = cirq.QubitId()
    q2 = cirq.QubitId()
    cnot = Job(cirq.Circuit([
        cirq.Moment([cirq.CNOT(q1, q2)]),
        ]))
    all_errors = DepolarizerChannel(probability=1.0)
    p0 = cirq.Symbol(DepolarizerChannel._parameter_name + '0')
    p1 = cirq.Symbol(DepolarizerChannel._parameter_name + '1')

    error_sweep = cirq.Points(p0.name, [1.0]) + cirq.Points(p1.name, [1.0])

    cnot_then_z = Job(
        cirq.Circuit([
            cirq.Moment([cirq.CNOT(q1, q2)]),
            cirq.Moment([xmon_gates.ExpZGate(half_turns=p0).on(q1),
                             xmon_gates.ExpZGate(half_turns=p1).on(q2)])
        ]),
        cnot.sweep * error_sweep)

    assert all_errors.transform_job(cnot) == cnot_then_z


def test_depolarizer_different_gate():
    q1 = cirq.QubitId()
    q2 = cirq.QubitId()
    cnot = Job(cirq.Circuit([
        cirq.Moment([cirq.CNOT(q1, q2)]),
        ]))
    allerrors = DepolarizerChannel(probability=1.0, depolarizing_gates=
                                   [xmon_gates.ExpZGate(),
                                    xmon_gates.ExpWGate()])
    p0 = cirq.Symbol(DepolarizerChannel._parameter_name + '0')
    p1 = cirq.Symbol(DepolarizerChannel._parameter_name + '1')
    p2 = cirq.Symbol(DepolarizerChannel._parameter_name + '2')
    p3 = cirq.Symbol(DepolarizerChannel._parameter_name + '3')

    error_sweep = (cirq.Points(p0.name, [1.0]) + cirq.Points(p1.name, [1.0])
                   + cirq.Points(p2.name, [1.0]) + cirq.Points(p3.name, [1.0]))

    cnot_then_z = Job(
        cirq.Circuit([
            cirq.Moment([cirq.CNOT(q1, q2)]),
            cirq.Moment([xmon_gates.ExpZGate(half_turns=p0).on(q1),
                             xmon_gates.ExpZGate(half_turns=p1).on(q2)]),
            cirq.Moment([xmon_gates.ExpWGate(half_turns=p2).on(q1),
                             xmon_gates.ExpWGate(half_turns=p3).on(q2)])
        ]),
        cnot.sweep * error_sweep)

    assert allerrors.transform_job(cnot) == cnot_then_z


def test_depolarizer_multiple_realizations():
    q1 = cirq.QubitId()
    q2 = cirq.QubitId()
    cnot = Job(cirq.Circuit([
        cirq.Moment([cirq.CNOT(q1, q2)]),
        ]))
    all_errors3 = DepolarizerChannel(probability=1.0, realizations=3)
    p0 = cirq.Symbol(DepolarizerChannel._parameter_name + '0')
    p1 = cirq.Symbol(DepolarizerChannel._parameter_name + '1')

    error_sweep = (cirq.Points(p0.name, [1.0, 1.0, 1.0]) +
                   cirq.Points(p1.name, [1.0, 1.0, 1.0]))

    cnot_then_z3 = Job(
        cirq.Circuit([
            cirq.Moment([cirq.CNOT(q1, q2)]),
            cirq.Moment([xmon_gates.ExpZGate(half_turns=p0).on(q1),
                             xmon_gates.ExpZGate(half_turns=p1).on(q2)])
        ]),
        cnot.sweep * error_sweep)
    assert all_errors3.transform_job(cnot) == cnot_then_z3


def test_depolarizer_parameterized_gates():
    q1 = cirq.QubitId()
    q2 = cirq.QubitId()
    cnot_param = cirq.Symbol('cnot_turns')
    cnot_gate = xmon_gates.Exp11Gate(half_turns=cnot_param).on(q1, q2)

    job_sweep = cirq.Points('cnot_turns', [0.5])

    cnot = Job(cirq.Circuit([cirq.Moment([cnot_gate])]), job_sweep)
    all_errors = DepolarizerChannel(probability=1.0)
    p0 = cirq.Symbol(DepolarizerChannel._parameter_name + '0')
    p1 = cirq.Symbol(DepolarizerChannel._parameter_name + '1')

    error_sweep = cirq.Points(p0.name, [1.0]) + cirq.Points(p1.name, [1.0])
    cnot_then_z = Job(
        cirq.Circuit([
            cirq.Moment([cnot_gate]),
            cirq.Moment([xmon_gates.ExpZGate(half_turns=p0).on(q1),
                             xmon_gates.ExpZGate(half_turns=p1).on(q2)])
        ]),
        job_sweep * error_sweep)
    assert all_errors.transform_job(cnot) == cnot_then_z
