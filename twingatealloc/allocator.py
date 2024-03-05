import dataclasses
from abc import ABC, abstractmethod

from twingatealloc.exceptions import OutOfMemory, InvalidPointer
from twingatealloc.pointer import Pointer


class Allocator(ABC):
    @abstractmethod
    def alloc(self, size: int) -> Pointer:
        """
        Allocate a chunk of memory from the available memory buffer.
        :param size: size of the chunk we want to allocate
        :return: a Pointer object wrapping the allocated memory
        """
        pass

    @abstractmethod
    def free(self, pointer: Pointer) -> None:
        """
        Frees an allocated chunk of memory.
        :param pointer: pointer to the allocated memory
        """
        pass


@dataclasses.dataclass
class Chunk:
    offset: int
    size: int
    free: bool


class BufferAllocator(Allocator):
    """
    Allocator implementation that takes an initial byte buffer as our allocator's arena.
    """
    buffer: bytearray
    chunks: list[Chunk]

    def __init__(self, buffer: bytearray) -> None:
        self.buffer = buffer

        # We initialize the allocator with a single free block
        self.chunks = [Chunk(0, len(buffer), free=True)]

    def _find_free_chunk(self, size: int) -> Chunk:
        """
        Finds a block of free memory where we might be able to allocate some data.
        :return: a Chunk object if any memory is available, None otherwise
        """
        for i in range(len(self.chunks)):
            chunk = self.chunks[i]

            # Ignored chunks that are already used or too small
            if not chunk.free or chunk.size < size:
                continue

            # If this chunk fits the size exactly, then just mark it allocated and return it
            if chunk.size == size:
                chunk.free = False
                return chunk
            else:
                # This chunk is bigger than we need, so we need to split it
                new_free_chunk = Chunk(
                    chunk.offset + size,
                    chunk.size - size,
                    free=True
                )
                self.chunks.insert(i + 1, new_free_chunk)

                # Modify existing chunk
                chunk.size = size
                chunk.free = False
                return chunk

        # If we got here, it means we never found a chunk
        raise OutOfMemory

    def alloc(self, size: int) -> Pointer:
        chunk = self._find_free_chunk(size)
        return Pointer(
            view=memoryview(self.buffer),
            loc=chunk.offset,
            size=size
        )

    def _join_free_chunks(self):
        """
        This will defragment contiguous free chunks of memory into single, bigger chunks.
        """
        free_groups = self._find_free_chunk_groups()

        # This will hold the list of all chunks that need to be deleted
        marked_for_deletion: list[int] = []

        # Dump all groups into the first element of the group
        for group in free_groups:
            # We can't really group a single block
            if len(group) == 1:
                continue

            chunk = self.chunks[group[0]]
            for chunk_index in group[1:]:
                marked_for_deletion.append(chunk_index)
                chunk.size += self.chunks[chunk_index].size

        # Finally, delete all the chunks that are no longer needed
        for chunk_index in reversed(marked_for_deletion):
            del self.chunks[chunk_index]

    def _find_free_chunk_groups(self) -> list[list[int]]:
        """
        Returns a list of all the groups of free chunks, by index and sorted from lower to higher index.
        """
        free_groups = []
        group = [] if self.chunks[0].free else None
        for i in range(len(self.chunks)):
            cur = self.chunks[i]
            if cur.free:
                if group is not None:
                    group.append(i)
                else:
                    group = []
            else:
                if group is not None:
                    free_groups.append(group)
                    group = None

        # Check if we have to add a new group at the end
        if group is not None:
            free_groups.append(group)

        return free_groups

    def free(self, pointer: Pointer):
        for i in range(len(self.chunks)):
            chunk = self.chunks[i]
            if chunk.offset == pointer.loc and chunk.size == pointer.size:
                pointer.view.release()
                chunk.free = True
                self._join_free_chunks()
                return

        # If we got here, we were trying to free a pointer that doesn't exist
        raise InvalidPointer