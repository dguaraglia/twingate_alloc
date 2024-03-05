# Twingate Memory Manager

Implements a simple memory allocator with some stronger guarantees than C's [`free`](https://en.cppreference.com/w/c/memory/free).


## Interface and use

To create a new memory manager, just create a `BufferMemoryManager` object
and provide a buffer to use as backing memory:

```python
from twingatealloc.memorymanager import BufferMemoryManager

mem_manager = BufferMemoryManager(bytearray(100))
```

The allocator provides a very simple interface:

* The `alloc(size: int) -> Pointer` method returns an object of type `Pointer` if there is 
enough contiguous free memory to serve the request, otherwise it raises an `OutOfMemory` exception.
* The `free(pointer: Pointer)` method frees the memory pointed at by the pointer. 
If the pointer is invalid (it has been freed before) an `InvalidPointer` exception is raised.

The `Pointer` object provides the following methods:
* `write(value: bytes)` writes the passed byte array into the backing memory
* `read() -> bytes` returns the value stored in the pointer

## Implementation details

### Considerations

The `BufferMemoryManager` class is implemented with the following considerations:

* Thread safety is not guaranteed
* No attempt is made to automatically defragment memory
* No attempt is made to clean up the buffer passed. The pointers will be created in
buffer as-is, which could lead to some unexpected behavior if one were to `read` from
a pointer before a known value is stored
* Freeing memory causes a somewhat expensive defragmentation
of free blocks to be performed, so freeing a lot of pointers sequentially will
result in a lot of duplicated work


### Implementation
The `BufferMemoryManager` keeps track of what memory is free and occupied by keeping
a list of `Chunks` objects. Each chunk consists of an `offset` into the buffer, a `size`
of the chunk of memory and a `free` flag that tells the allocator whether this space
is free or is referenced to by a pointer.

The list of chunks is initialized to a single _free_ chunk with size equal to the size of the buffer.

#### Allocation
Whenever an `alloc` call is done, the manager will look for a free chunk that can accommodate
the request, and if one is found it'll split it into two chunks:

* One 'occupied' chunk of the request size
* One 'free' chunk for the remainder of the memory in the existing chunk

> **NOTE**: if the amount of memory requested is exactly the same as the existing free chunk,
> then we simply mark this existing chunk as occupied.

If no free chunk is big enough to accommodate the request, an `OutOfMemory` exception is raised.


#### Freeing
Freeing memory is mostly a mirror process to allocation:

* We iterate over the existing chunks and find the one matching the pointer in location and size
* We mark this chunk as 'free'
* We then trigger the free chunk defragmentation

The defragmentation works as follows:
1. We identify all groups of consecutive chunks that are marked as free
2. For each one of the groups:
   1. We extend the size of the first chunk to be the sum total
   of all chunks in the group; this obviates the need for all subsequent chunks in the group
   2. We append each of the unneeded chunks to a list of chunks to be deleted
3. We delete the chunks in reverse order

> **NOTE**: the reason we delete the chunks in reverse order is to ensure that the indices into
> the chunk list remain stable during the operation. An example might help: assuming we have a list with
> 5 chunks `[c0, c1, c2, c3, c4]` and we need to delete chunks `[c1, c3]`, if we were to delete `c1` first,
> then the index number for `c3` would change from underneath us.