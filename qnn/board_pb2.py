# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: board.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0b\x62oard.proto\x12\x05proto\"k\n\x0c\x42oardRequest\x12\r\n\x05\x62oard\x18\x01 \x03(\t\x12\x0c\n\x04size\x18\x02 \x01(\x05\x12\x17\n\x0f\x62lack_prisoners\x18\x03 \x01(\x05\x12\x17\n\x0fwhite_prisoners\x18\x04 \x01(\x05\x12\x0c\n\x04komi\x18\x05 \x01(\x02\"F\n\nScoreReply\x12\x13\n\x0b\x62lack_score\x18\x01 \x01(\x02\x12\x13\n\x0bwhite_score\x18\x02 \x01(\x02\x12\x0e\n\x06winner\x18\x03 \x01(\t2E\n\x0c\x42oardService\x12\x35\n\tSendBoard\x12\x13.proto.BoardRequest\x1a\x11.proto.ScoreReply\"\x00\x42\x03Z\x01.b\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'board_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z\001.'
  _globals['_BOARDREQUEST']._serialized_start=22
  _globals['_BOARDREQUEST']._serialized_end=129
  _globals['_SCOREREPLY']._serialized_start=131
  _globals['_SCOREREPLY']._serialized_end=201
  _globals['_BOARDSERVICE']._serialized_start=203
  _globals['_BOARDSERVICE']._serialized_end=272
# @@protoc_insertion_point(module_scope)