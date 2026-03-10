import typing as tp
import heapq

def get_int(input_stream: tp.IO[bytes]) -> int | None:
    s = input_stream.readline()
    if s == b'' or s == b'\n':
        return None
    return int(s.decode('utf-8')) # todo: check

def merge(input_streams: tp.Sequence[tp.IO[bytes]], output_stream: tp.IO[bytes]) -> None:
    """
    Merge input_streams in output_stream
    :param input_streams: list of input streams. Contains byte-strings separated by "\n". Nonempty stream ends with "\n"
    :param output_stream: output stream. Contains byte-strings separated by "\n". Nonempty stream ends with "\n"
    :return: None  #  for val in answer:
  #      output_stream.write(bytes(val))
        #output_stream.write(b'\n')
    """
    heap = []
    for pos in range(len(input_streams)):
        temp = get_int(input_streams[pos])
        if temp is not None:
            heapq.heappush(heap, (temp, pos))

   # answer = []
    while heap:
        val, pos = heapq.heappop(heap)
        output_stream.write((str(val) + '\n').encode('utf-8'))
        temp = get_int(input_streams[pos])
        if temp is not None:
            heapq.heappush(heap, (temp, pos))
