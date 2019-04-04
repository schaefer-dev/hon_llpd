from enum import IntEnum
from ipaddress import ip_address, IPv4Address, IPv6Address

from lldp.tlv import TLV


class PortIdTLV(TLV):
    """Port ID TLV

    The port ID TLV identifies the sending port used by the LLDP agent.

    The port ID TLV is mandatory and MUST be the second TLV in the LLDPDU.
    Each LLDPDU MUST contain one, and only one, Port ID TLV.


    Attributes:
        type (TLV.Type): The type of the TLV
        subtype (PortIdTLV.Subtype): The port ID subtype
        value: The port ID.
            The type of this attribute depends on the subtype
                    MAC Address -> bytes,
                    Network Address -> ip_address,
                    Otherwise -> str


    TLV Format:

         0               1               2               3
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-...-+-+-+-+
        |             |                 |               |               |
        |      2      |      Length     |    Subtype    |    Port ID    |
        |             |                 |               |               |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-...-+-+-+-+

                                                            1 - 255 byte

    There are several ways in which a port may be identified.
    A port ID subtype is used to indicate how the port is being referenced in the Port ID field.

        | Subtype | ID Basis          | Example                    |
        | ------- | ----------------- | -------------------------- |
        | 0       | Reserved          |                            |
        | 1       | Interface Alias   | Ethernet Interface         |
        | 2       | Port Component    | backplane1                 |
        | 3       | MAC Address       | 02:04:df:88:a2:b4          |
        | 4       | Network Address   | 134.96.86.110              |
        | 5       | Interface Name    | eth0                       |
        | 6       | Agent Circuit ID  |                            |
        | 7       | Locally Assigned  | Frank's Computer           |
        | 8 - 255 | Reserved          |                            |

    With the exception of subtypes 3 (MAC Address) and 4 (Network Address) the subtype is a string
    as far as the LLDP agent is concerned. A distinction between these types is only made by a human observer.

    MAC Address Subtype:

        MAC addresses are represented as raw bytes, e.g. the MAC address 02:04:df:88:a2:b4 corresponds to a value of
        b"\x02\x04\xDF\x88\xA2\xB4".

    Network Address Subtype:

        Network addresses are represented as raw bytes.

        In practice there are many different network protocols, each with their own address format with e.g. a different
        length.

        To determine the type of network protocol and the appropriate length of the network address transmitted in the
        port ID TLV, network addresses are prefixed with an extra byte identifying the address family.

        For this implementation we only consider IPv4 and IPv6.

        | Protocol | Family Number |
        | -------- | ------------- |
        |   IPv4   |             1 |
        |   IPv6   |             2 |

        Examples (Address -> Bytes -> Prefixed Bytes):
            134.96.86.110  ->  b"\x86\x60\x56\x6E"  -> b"\x01\x86\x60\x56\x6E"

            20db::1        ->  b"\x20\xdb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01"
                           ->  b"\x02\x20\xdb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01"

        The full list of registered protocol families is available at:
            https://www.iana.org/assignments/address-family-numbers/address-family-numbers.xhtml

    """

    class Subtype(IntEnum):
        INTERFACE_ALIAS = 1
        PORT_COMPONENT = 2
        MAC_ADDRESS = 3
        NETWORK_ADDRESS = 4
        INTERFACE_NAME = 5
        CIRCUIT_ID = 6
        LOCAL = 7

        def __repr__(self):
            return repr(self.value)

    def __init__(self, subtype: Subtype, id):
        """ Constructor

        Args:
            subtype (ChassisIdTLV.Subtype): The ID subtype
            id (str, bytes or ip_address): The type of this attribute depends on the subtype
                MAC Address     -> bytes
                Network Address -> ip_address
                Otherwise       -> str
        """
        # TODO: Implement
        self.type = NotImplemented
        self.subtype = NotImplemented
        self.value = NotImplemented

    def __bytes__(self):
        """Return the byte representation of the TLV.

        This method must return bytes. Returning a bytearray will raise a TypeError.
        See `TLV.__bytes__()` for more information.
        """
        # TODO: Implement
        return NotImplemented

    def __len__(self):
        """Return the length of the TLV value.

        This method must return an int. Returning anything else will raise a TypeError.
        See `TLV.__len__()` for more information.
        """
        # TODO: Implement
        return NotImplemented

    def __repr__(self):
        """Return a printable representation of the TLV object.

        See `TLV.__repr__()` for more information.
        """
        # TODO: Implement
        return NotImplemented

    @staticmethod
    def from_bytes(data: TLV.ByteType):
        """Create a TLV instance from raw bytes.

        Args:
            data (bytes or bytearray): The packed TLV

        Raises a `ValueError` if the provided TLV contains errors (e.g. has the wrong type).
        """
        # TODO: Implement
        return NotImplemented
