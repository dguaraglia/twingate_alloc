import pytest

from twingatealloc.memorymanager import BufferMemoryManager
from twingatealloc.exceptions import OutOfMemory


def test_simple_allocation():
    # Given
    allocator = BufferMemoryManager(bytearray(10))

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
    allocator = BufferMemoryManager(bytearray(10))
    p1 = allocator.alloc(5)

    # Then
    with pytest.raises(OutOfMemory):
        allocator.alloc(10)

    # Given
    allocator = BufferMemoryManager(bytearray(b''))

    # Then
    with pytest.raises(OutOfMemory):
        allocator.alloc(1)


def test_memory_freeing():
    # Given
    allocator = BufferMemoryManager(bytearray(10))
    p1 = allocator.alloc(5)

    # Then
    with pytest.raises(OutOfMemory):
        allocator.alloc(10)

    # When
    allocator.free(p1)
    allocator.alloc(10)

    with pytest.raises(OutOfMemory):
        allocator.alloc(1)


def test_fragmentation():
    # Given
    allocator = BufferMemoryManager(bytearray(10))

    pointers = []
    for i in range(10):
        pointers.append(allocator.alloc(1))

    # When we free every other pointer
    for i in range(len(pointers)):
        if i % 2 == 1:
            allocator.free(pointers[i])

    # Then, if we try to allocate a 2 byte object we should fail
    with pytest.raises(OutOfMemory):
        allocator.alloc(2)