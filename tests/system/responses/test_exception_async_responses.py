import pytest
import struct
from functools import partial

from ..validators import validate_response_mbap, validate_response_error
from umodbus.client import tcp


pytestmark = pytest.mark.asyncio


async def req_rep(adu, reader, writer):
    writer.write(adu)
    await writer.drain()
    return await reader.read(1024)


@pytest.mark.parametrize('function_code, quantity', [
    (1, 0),
    (2, 0),
    (3, 0),
    (4, 0),
    (1, 0x07D0 + 1),
    (2, 0x07D0 + 1),
    (3, 0x007D + 1),
    (4, 0x007D + 1),
])
async def test_request_returning_invalid_data_value_error(async_tcp_streams, mbap, function_code,
                                                          quantity):
    """ Validate response PDU of request returning exception response with
    error code 3.
    """
    starting_address = 0
    adu = mbap + struct.pack('>BHH', function_code, starting_address, quantity)

    resp = await req_rep(adu, *async_tcp_streams)

    validate_response_mbap(mbap, resp)
    validate_response_error(resp, function_code, 3)


@pytest.mark.parametrize('function', [
    (partial(tcp.read_coils, 1, 9, 2)),
    (partial(tcp.read_discrete_inputs, 1, 9, 2)),
    (partial(tcp.read_holding_registers, 1, 9, 2)),
    (partial(tcp.read_input_registers, 1, 9, 2)),
    (partial(tcp.write_single_coil, 1, 11, 0)),
    (partial(tcp.write_single_register, 1, 11, 1337)),
    (partial(tcp.write_multiple_coils, 1, 9, [1, 1])),
    (partial(tcp.write_multiple_registers, 1, 9, [1337, 15])),
])
async def test_request_returning_invalid_data_address_error(async_tcp_streams, function):
    """ Validate response PDU of request returning exception response with
    error code 2.
    """
    adu = function()

    mbap = adu[:7]
    function_code = struct.unpack('>B', adu[7:8])[0]

    resp = await req_rep(adu, *async_tcp_streams)

    validate_response_mbap(mbap, resp)
    validate_response_error(resp, function_code, 2)


@pytest.mark.parametrize('function', [
    (partial(tcp.read_coils, 1, 666, 1)),
    (partial(tcp.read_discrete_inputs, 1, 666, 1)),
    (partial(tcp.read_holding_registers, 1, 666, 1)),
    (partial(tcp.read_input_registers, 1, 666, 1)),
    (partial(tcp.write_single_coil, 1, 666, 0)),
    (partial(tcp.write_single_register, 1, 666, 1337)),
    (partial(tcp.write_multiple_coils, 1, 666, [1])),
    (partial(tcp.write_multiple_registers, 1, 666, [1337])),
])
async def test_request_returning_server_device_failure_error(async_tcp_streams, function):
    """ Validate response PDU of request returning exception response with
    error code 4.
    """
    adu = function()

    mbap = adu[:7]
    function_code = struct.unpack('>B', adu[7:8])[0]

    resp = await req_rep(adu, *async_tcp_streams)

    validate_response_mbap(mbap, resp)
    validate_response_error(resp, function_code, 4)