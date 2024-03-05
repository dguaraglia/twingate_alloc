
class OutOfMemory(Exception):
    """
    Raised when an allocator has run out of memory.
    """
    pass


class InvalidPointer(Exception):
    """
    Raised when trying to free a pointer that doesn't exist
    """
    pass


class InvalidWrite(Exception):
    """
    Raised when trying to write more data than the pointer points to.
    """
    pass
