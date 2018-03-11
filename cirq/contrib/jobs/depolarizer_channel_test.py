# Copyright 2017 Google LLC
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

from cirq import circuits
from cirq import ops
from cirq.api.google.v1.params_pb2 import ParameterSweep
from cirq.contrib.jobs import DepolarizerChannel
from cirq.contrib.jobs import Job
from cirq.google import xmon_gates
from cirq.study.parameterized_value import ParameterizedValue


def test_depolarizer_no_errors():
    q1 = ops.QubitId()
    q2 = ops.QubitId()
    cnot = Job(circuits.Circuit([
        circuits.Moment([ops.CNOT(q1, q2)]),
        ]))
    noerrors = DepolarizerChannel(probability=0.0)

    assert noerrors.transform_job(cnot) == cnot


def test_depolarizer_all_errors():
    q1 = ops.QubitId()
    q2 = ops.QubitId()
    cnot = Job(circuits.Circuit([
        circuits.Moment([ops.CNOT(q1, q2)]),
        ]))
    allerrors = DepolarizerChannel(probability=1.0)
    p0 = ParameterizedValue(DepolarizerChannel._parameter_name + '0')
    p1 = ParameterizedValue(DepolarizerChannel._parameter_name + '1')

    sweep = ParameterSweep()
    sweep.repetitions = 1
    sweep.sweep.factors.add()
    sweep.sweep.factors[0].sweeps.add()
    sweep.sweep.factors[0].sweeps.add()
    sweep.sweep.factors[0].sweeps[0].parameter_name = p0.key
    sweep.sweep.factors[0].sweeps[0].sweep_points.points.append(1.0)
    sweep.sweep.factors[0].sweeps[1].parameter_name = p1.key
    sweep.sweep.factors[0].sweeps[1].sweep_points.points.append(1.0)

    cnot_then_z = Job(circuits.Circuit([
        circuits.Moment([ops.CNOT(q1, q2)]),
        circuits.Moment([xmon_gates.ExpZGate(half_turns=p0).on(q1),
                         xmon_gates.ExpZGate(half_turns=p1).on(q2)])]),
                      sweep)

    assert allerrors.transform_job(cnot) == cnot_then_z


def test_depolarizer_multiple_repetitions():
    q1 = ops.QubitId()
    q2 = ops.QubitId()
    cnot = Job(circuits.Circuit([
        circuits.Moment([ops.CNOT(q1, q2)]),
        ]))
    allerrors3 = DepolarizerChannel(probability=1.0, repetitions=3)
    p0 = ParameterizedValue(DepolarizerChannel._parameter_name + '0')
    p1 = ParameterizedValue(DepolarizerChannel._parameter_name + '1')

    sweep = ParameterSweep()
    sweep.repetitions = 1
    sweep.sweep.factors.add()
    sweep.sweep.factors[0].sweeps.add()
    sweep.sweep.factors[0].sweeps.add()
    sweep.sweep.factors[0].sweeps[0].parameter_name = p0.key
    sweep.sweep.factors[0].sweeps[0].sweep_points.points.append(1.0)
    sweep.sweep.factors[0].sweeps[1].parameter_name = p1.key
    sweep.sweep.factors[0].sweeps[1].sweep_points.points.append(1.0)
    sweep.sweep.factors[0].sweeps[0].sweep_points.points.append(1.0)
    sweep.sweep.factors[0].sweeps[0].sweep_points.points.append(1.0)
    sweep.sweep.factors[0].sweeps[1].sweep_points.points.append(1.0)
    sweep.sweep.factors[0].sweeps[1].sweep_points.points.append(1.0)
    cnot_then_z3 = Job(circuits.Circuit([
        circuits.Moment([ops.CNOT(q1, q2)]),
        circuits.Moment([xmon_gates.ExpZGate(half_turns=p0).on(q1),
                         xmon_gates.ExpZGate(half_turns=p1).on(q2)])]),
                       sweep)
    assert allerrors3.transform_job(cnot) == cnot_then_z3


def test_depolarizer_parameterized_gates():
    q1 = ops.QubitId()
    q2 = ops.QubitId()
    cnot_param = ParameterizedValue('cnot_turns')
    cnot_gate = xmon_gates.Exp11Gate(half_turns=cnot_param).on(q1, q2)
    job_sweep = ParameterSweep()
    job_sweep.repetitions = 2
    job_sweep.sweep.factors.add()
    job_sweep.sweep.factors[0].sweeps.add()
    job_sweep.sweep.factors[0].sweeps[0].parameter_name = 'cnot_turns'
    job_sweep.sweep.factors[0].sweeps[0].sweep_points.points.append(0.5)

    cnot = Job(circuits.Circuit([circuits.Moment([cnot_gate])]), job_sweep)
    allerrors = DepolarizerChannel(probability=1.0)
    p0 = ParameterizedValue(DepolarizerChannel._parameter_name + '0')
    p1 = ParameterizedValue(DepolarizerChannel._parameter_name + '1')

    new_sweep = ParameterSweep()
    new_sweep.repetitions = 2
    new_sweep.sweep.factors.add()
    new_sweep.sweep.factors[0].sweeps.add()
    new_sweep.sweep.factors[0].sweeps[0].parameter_name = 'cnot_turns'
    new_sweep.sweep.factors[0].sweeps[0].sweep_points.points.append(0.5)
    new_sweep.sweep.factors.add()
    new_sweep.sweep.factors[1].sweeps.add()
    new_sweep.sweep.factors[1].sweeps.add()
    new_sweep.sweep.factors[1].sweeps[0].parameter_name = p0.key
    new_sweep.sweep.factors[1].sweeps[0].sweep_points.points.append(1.0)
    new_sweep.sweep.factors[1].sweeps[1].parameter_name = p1.key
    new_sweep.sweep.factors[1].sweeps[1].sweep_points.points.append(1.0)
    cnot_then_z = Job(circuits.Circuit([
        circuits.Moment([cnot_gate]),
        circuits.Moment([xmon_gates.ExpZGate(half_turns=p0).on(q1),
                         xmon_gates.ExpZGate(half_turns=p1).on(q2)])]),
                      new_sweep)
    assert allerrors.transform_job(cnot) == cnot_then_z

test_depolarizer_parameterized_gates()
