import pytest

from twingatealloc.exceptions import InvalidPointer
from twingatealloc.pointer import Pointer


def test_write():
    # Given
    mem = bytearray(10)
    pointer = Pointer(memoryview(mem), 0, 2)

    # When
    pointer.write(b'ab')

    # Then
    assert mem[0:2] == b'ab'


def test_read():
    # Given
    mem = bytearray(b"bananas")
    pointer = Pointer(memoryview(mem), 4, 3)

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
        Pointer(view, 10, 0)

    with pytest.raises(InvalidPointer):
        Pointer(view, 0, 10)

    with pytest.raises(InvalidPointer):
        Pointer(view, 5, 3)
