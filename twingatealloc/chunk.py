import dataclasses

from twingatealloc.exceptions import InvalidWrite


@dataclasses.dataclass
class Chunk:
    offset: int
    size: int
    free: bool = True

    def fits_in(self, mem: memoryview | bytearray):
        return self.offset + self.size <= len(mem)

    def read_from(self, mem: memoryview) -> bytes:
        """
        Reads this chunk from a memory view
        :param mem: memview to read from
        :return: a bytes object containing the data pointed at by the chunk
        """
        return mem[self.offset:self.offset+self.size].tobytes()

    def write_to(self, mem: memoryview, value: bytes):
        """
        Writes a value to the memory location pointed by the chunk
        :param mem: memory view to write to
        :param value: value to writeh
        """
        if len(value) > self.size:
            raise InvalidWrite
        mem[self.offset:self.offset+self.size] = value

