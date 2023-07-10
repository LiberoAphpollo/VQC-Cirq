# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: cirq_google/api/v2/result.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from cirq_google.api.v2 import program_pb2 as cirq__google_dot_api_dot_v2_dot_program__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1f\x63irq_google/api/v2/result.proto\x12\x12\x63irq.google.api.v2\x1a cirq_google/api/v2/program.proto\"@\n\x06Result\x12\x36\n\rsweep_results\x18\x01 \x03(\x0b\x32\x1f.cirq.google.api.v2.SweepResult\"j\n\x0bSweepResult\x12\x13\n\x0brepetitions\x18\x01 \x01(\x05\x12\x46\n\x15parameterized_results\x18\x02 \x03(\x0b\x32\'.cirq.google.api.v2.ParameterizedResult\"\x8c\x01\n\x13ParameterizedResult\x12\x31\n\x06params\x18\x01 \x01(\x0b\x32!.cirq.google.api.v2.ParameterDict\x12\x42\n\x13measurement_results\x18\x02 \x03(\x0b\x32%.cirq.google.api.v2.MeasurementResult\"\x82\x01\n\x11MeasurementResult\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x11\n\tinstances\x18\x03 \x01(\x05\x12M\n\x19qubit_measurement_results\x18\x02 \x03(\x0b\x32*.cirq.google.api.v2.QubitMeasurementResult\"S\n\x16QubitMeasurementResult\x12(\n\x05qubit\x18\x01 \x01(\x0b\x32\x19.cirq.google.api.v2.Qubit\x12\x0f\n\x07results\x18\x02 \x01(\x0c\"\x8c\x01\n\rParameterDict\x12G\n\x0b\x61ssignments\x18\x01 \x03(\x0b\x32\x32.cirq.google.api.v2.ParameterDict.AssignmentsEntry\x1a\x32\n\x10\x41ssignmentsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x02:\x02\x38\x01\x42.\n\x1d\x63om.google.cirq.google.api.v2B\x0bResultProtoP\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'cirq_google.api.v2.result_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\035com.google.cirq.google.api.v2B\013ResultProtoP\001'
  _PARAMETERDICT_ASSIGNMENTSENTRY._options = None
  _PARAMETERDICT_ASSIGNMENTSENTRY._serialized_options = b'8\001'
  _globals['_RESULT']._serialized_start=89
  _globals['_RESULT']._serialized_end=153
  _globals['_SWEEPRESULT']._serialized_start=155
  _globals['_SWEEPRESULT']._serialized_end=261
  _globals['_PARAMETERIZEDRESULT']._serialized_start=264
  _globals['_PARAMETERIZEDRESULT']._serialized_end=404
  _globals['_MEASUREMENTRESULT']._serialized_start=407
  _globals['_MEASUREMENTRESULT']._serialized_end=537
  _globals['_QUBITMEASUREMENTRESULT']._serialized_start=539
  _globals['_QUBITMEASUREMENTRESULT']._serialized_end=622
  _globals['_PARAMETERDICT']._serialized_start=625
  _globals['_PARAMETERDICT']._serialized_end=765
  _globals['_PARAMETERDICT_ASSIGNMENTSENTRY']._serialized_start=715
  _globals['_PARAMETERDICT_ASSIGNMENTSENTRY']._serialized_end=765
# @@protoc_insertion_point(module_scope)
