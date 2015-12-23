"""
.. note:: This section is based on `MODBUS Application Protocol Specification
    V1.1b3`_

The Protocol Data Unit (PDU) is the request or response message and is
indepedent of the underlying communication layer. This module only implements
requests PDU's.

A request PDU contains two parts: a function code and request data. A response
PDU contains the function code from the request and response data. The general
structure is listed in table below:

+---------------+-----------------+
| **Field**     | **Size** (bytes)|
+---------------+-----------------+
| Function code | 1               |
+---------------+-----------------+
| data          | N               |
+---------------+-----------------+

Below you see the request PDU with function code 1, requesting status of 3
coils, starting from coil 100::

    >>> req_pdu = b'\x01\x00d\x00\x03'
    >>> function_code = req_pdu[:1]
    >>> function_code
    b'\x01'
    >>> starting_address = req_pdu[1:3]
    >>> starting_address
    b'\x00d'
    >>> quantity = req_pdu[3:]
    >>> quantity
    b'\x00\x03'

A response PDU could look like this::

    >>> resp_pdu = b'\x01\x01\x06'
    >>> function_code = resp_pdu[:1]
    >>> function_code
    b'\x01'
    >>> byte_count = resp[1:2]
    >>> byte_count
    b'\x01'
    >>> coil_status = resp[2:]
    'b\x06'

.. _MODBUS Application Protocol Specification V1.1b3: http://modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf
"""
import struct

try:
    from functools import reduce
except ImportError:
    pass


def read_coils(starting_address, quantity):
    """ Return PDU for Modbus function code 01: Read Coils.

    :param starting_address: Number with address of first coil.
    :param quantity: Number with amount of coils to read.
    :return: Byte array with PDU.
    """
    return struct.pack('>BHH', 1, starting_address, quantity)


def read_discrete_inputs(starting_address, quantity):
    """ Return PDU for Modbus function code 02: Read Discret Inputs.

    :param starting_address: Number with address of first discrete input.
    :param quantity: Number with amount of discrete inputs to read.
    :return: Byte array with PDU.
    """
    return struct.pack('>BHH', 2, starting_address, quantity)


def read_holding_registers(starting_address, quantity):
    """ Return PDU for Modbus function code 03: Read Input Registers.

    :param starting_address: Number with address of first holding register.
    :param quantity: Number with amount of holding registers to read.
    :return: Byte array with PDU.
    """
    return struct.pack('>BHH', 3, starting_address, quantity)


def read_input_registers(starting_address, quantity):
    """ Return PDU for Modbus function code 04: Read Input Registers.

    :param starting_address: Number with address of first input register.
    :param quantity: Number with amount of input registers to read.
    :return: Byte array with PDU.
    """
    return struct.pack('>BHH', 4, starting_address, quantity)


def write_single_coil(address, value):
    """ Return PDU for Modbus function code 05: Write Single Coil.

    :param address: Address of coil you want to write to.
    :param value: Boolean indicating status of coil.
    :return: Byte array with PDU.
    """
    status = 0xFFFF if value else 0x0000
    return struct.pack('>BHH', 5, address, status)


def write_single_register(address, value):
    """ Return PDU for Modbus function code 06: Write Single Register.

    :param address: Address of register you want to write to.
    :param value: Value of register.
    :return: Byte array with PDU.
    """
    return struct.pack('>BHH', 6, address, value)


def write_multiple_coils(starting_address, values):
    """ Return PDU for Modbus function code 15: Write Multiple Coils.

    :param address: Address of first coil you want to write to.
    :param value: Boolean indicating status of coil.
    :return: Byte array with PDU.
    """
    # Amount of bytes required to store status of all coils. 1 byte can store
    # statusses of 8 coils.
    bytes_required = (len(values) // 8) + 1
    bytes_ = []

    for i in range(0, len(values), 8):
        # A list with values of 1 byte.
        eight_bits = values[i:i+8]
        eight_bits.reverse()

        # Magic. Reduce a list like [1, 0, 1, 1] to its decimal representation,
        # in this particular case it's 11.
        bytes_.append(reduce(lambda value, bit: (value << 1) ^ bit,
                             eight_bits, 0))

    fmt = '>BHHB' + ('B' * bytes_required)
    return struct.pack(fmt, 15, starting_address, len(values), bytes_required,
                       *bytes_)


def write_multiple_registers(starting_address, values):
    """ Return PDU for Modbus function code 16: Write Multiple Registers.

    :param address: Address of first register you want to write to.
    :param value: List of values you want to write.
    :return: Byte array with PDU.
    """
    fmt = '>BHHB' + ('H' * len(values))
    return struct.pack(fmt, 16, starting_address, len(values),
                       2 * len(values),  *values)