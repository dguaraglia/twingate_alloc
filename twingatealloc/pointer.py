from twingatealloc.exceptions import InvalidPointer, InvalidWrite


class Pointer:
    """
    Interface to interact with chunks of memory allocated inside the Memory Manager
    """
    size: int
    loc: int
    view: memoryview

    def write(self, value: bytes):
        """
        Write a value to the memory pointed at by this pointer.
        :param value: bytes to write
        :return: None
        """
        if len(value) > self.size:
            raise InvalidWrite
        self.view[self.loc:self.loc+self.size] = value

    def read(self) -> bytes:
        """
        Returns the memory pointed at by this pointer.
        :return:
        """
        return self.view[self.loc:self.loc+self.size].tobytes()

    def __init__(self, view: memoryview, loc: int, size: int) -> None:
        if len(view) < loc + size:
            raise InvalidPointer
        self.view = view
        self.loc = loc
        self.size = size
