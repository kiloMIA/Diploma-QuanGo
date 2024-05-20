from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class BoardRequest(_message.Message):
    __slots__ = ("board", "size", "black_prisoners", "white_prisoners", "komi")
    BOARD_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    BLACK_PRISONERS_FIELD_NUMBER: _ClassVar[int]
    WHITE_PRISONERS_FIELD_NUMBER: _ClassVar[int]
    KOMI_FIELD_NUMBER: _ClassVar[int]
    board: _containers.RepeatedScalarFieldContainer[str]
    size: int
    black_prisoners: int
    white_prisoners: int
    komi: float
    def __init__(self, board: _Optional[_Iterable[str]] = ..., size: _Optional[int] = ..., black_prisoners: _Optional[int] = ..., white_prisoners: _Optional[int] = ..., komi: _Optional[float] = ...) -> None: ...

class ScoreReply(_message.Message):
    __slots__ = ("black_score", "white_score", "winner")
    BLACK_SCORE_FIELD_NUMBER: _ClassVar[int]
    WHITE_SCORE_FIELD_NUMBER: _ClassVar[int]
    WINNER_FIELD_NUMBER: _ClassVar[int]
    black_score: float
    white_score: float
    winner: str
    def __init__(self, black_score: _Optional[float] = ..., white_score: _Optional[float] = ..., winner: _Optional[str] = ...) -> None: ...
