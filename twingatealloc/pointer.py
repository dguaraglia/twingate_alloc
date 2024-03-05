from twingatealloc.exceptions import InvalidPointer, InvalidWrite
from twingatealloc.chunk import Chunk


class Pointer:
    """
    Interface to interact with chunks of memory allocated inside the Memory Manager
    """
    view: memoryview
    chunk: Chunk

    def write(self, value: bytes):
        """
        Write a value to the memory pointed at by this pointer.
        :param value: bytes to write
        :return: None
        """
        self.chunk.write_to(self.view, value)

    def read(self) -> bytes:
        """
        Returns the memory pointed at by this pointer.
        :return:
        """
        return self.chunk.read_from(self.view)

    def __init__(self, view: memoryview, chunk: Chunk) -> None:
        if not chunk.fits_in(view):
            raise InvalidPointer
        self.chunk = chunk
        self.view = view
