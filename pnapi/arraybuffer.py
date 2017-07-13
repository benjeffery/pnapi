import numpy
import struct


def read_c_string(f):
    string = ''
    while True:
        char = f.read(1).decode("utf-8")
        if char == '\0':
            break
        else:
            string += char
    return string


def read_uint8(f):
    return struct.unpack('B', f.read(1))[0]


def read_uint32(f):
    return struct.unpack('I', f.read(4))[0]


def decode_single_array(stream):
    dtype = read_c_string(stream)
    num_dim = read_uint8(stream)
    shape = []
    for i in range(num_dim):
        shape.append(read_uint32(stream))
    array_len = read_uint32(stream)
    if 'S' in dtype:
        return [read_c_string(stream) for i in range(array_len)]
    else:
        num_bytes = int(dtype[-1])
        return numpy.reshape(numpy.fromstring(stream.read(num_bytes * array_len), dtype=dtype, count=array_len), shape)


def decode_array_set(stream):
    num_arrays = read_uint8(stream)
    result = {}
    for i in range(num_arrays):
        name = read_c_string(stream)
        result[name] = decode_single_array(stream)
    return result


def decode(stream):
    type_string = stream.read(2)
    if type_string == b'AB':
        return decode_single_array(stream)
    elif type_string == b'AS':
        return decode_array_set(stream)
    else:
        raise BufferError('type string unknown')
