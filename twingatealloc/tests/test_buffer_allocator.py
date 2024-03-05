import pytest

from twingatealloc.allocator import BufferAllocator
from twingatealloc.exceptions import OutOfMemory


def test_simple_allocation():
    # Given
    allocator = BufferAllocator(bytearray(10))

    # When
    p = allocator.alloc(5)
    data = p.read()

    # Then
    assert data == b'\x00' * 5

    # When
    p.write(b"hello")
    data = p.read()

    # Then
    assert data == b'hello'


def test_out_of_memory():
    # Given
    allocator = BufferAllocator(bytearray(10))
    p1 = allocator.alloc(5)

    # Then
    with pytest.raises(OutOfMemory):
        allocator.alloc(10)


def test_memory_freeing():
    # Given
    allocator = BufferAllocator(bytearray(10))
    p1 = allocator.alloc(5)

    # Then
    with pytest.raises(OutOfMemory):
        allocator.alloc(10)

    # When
    allocator.free(p1)
    allocator.alloc(10)

    with pytest.raises(OutOfMemory):
        allocator.alloc(1)
