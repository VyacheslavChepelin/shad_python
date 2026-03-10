import sys
import typing as tp
from pathlib import Path

BUF_SIZE = 1

def tail(filename: Path, lines_amount: int = 10, output: tp.IO[bytes] | None = None) -> None:
    """
    :param filename: file to read lines from (the file can be very large)
    :param lines_amount: number of lines to read
    :param output: stream to write requested amount of last lines from file
                   (if nothing specified stdout will be used)
    """
    if output is None:
        output = sys.stdout.buffer
    with open(filename, "rb") as file:
        file.seek(0,2)
        file_size = file.tell()
        pos = file_size
        total_lines = 0
        buffer = bytearray(BUF_SIZE)
        while pos > 0:
            read_size = min(BUF_SIZE, pos)
            file.seek(pos - read_size, 0)
            file.readinto(buffer)
            chunk = buffer[:read_size]
            cur_lines = chunk.count(b'\n')
            if cur_lines + total_lines > lines_amount:
                for ind in range(read_size):
                    if chunk[ind] == b'\n':
                        cur_lines -= 1
                    if cur_lines + total_lines == lines_amount:
                        pos = pos - read_size + ind + 1
                        break
                break
            total_lines += cur_lines
            pos -= read_size
        file.seek(pos, 0)
        read = 1 if lines_amount != 0 else 0
        while read != 0:
            read = file.readinto(buffer)
            output.write(buffer[:read])
