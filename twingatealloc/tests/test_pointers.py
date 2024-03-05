import pytest

from twingatealloc.chunk import Chunk
from twingatealloc.exceptions import InvalidPointer
from twingatealloc.pointer import Pointer


def test_write():
    # Given
    mem = bytearray(10)
    pointer = Pointer(memoryview(mem), Chunk(0, 2, False))

    # When
    pointer.write(b'ab')

    # Then
    assert mem[0:2] == b'ab'


def test_read():
    # Given
    mem = bytearray(b"bananas")
    pointer = Pointer(memoryview(mem), Chunk(4, 3, False))

    # When
    read = pointer.read()

    # Then
    assert read == b'nas'


def test_invalid_size():
    # Given
    mem = bytearray(b"bananas")
    view = memoryview(mem)

    # Then
    with pytest.raises(InvalidPointer):
        Pointer(view, Chunk(10, 0, False))

    with pytest.raises(InvalidPointer):
        Pointer(view, Chunk(0, 10, False))

    with pytest.raises(InvalidPointer):
        Pointer(view, Chunk(5, 3, False))
