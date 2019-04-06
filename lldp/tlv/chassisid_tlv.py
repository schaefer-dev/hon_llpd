from enum import IntEnum
from ipaddress import ip_address, IPv4Address, IPv6Address

from lldp.tlv import TLV


# TODO: implement support for most significant length byte that is contained the first data-byte. Currently this bit is still ignored in all methods

class ChassisIdTLV(TLV):
    """Chassis ID TLV

    The chassis ID TLV identifies the chassis (i.e. device) running the LLDP agent.

    The chassis ID TLV is mandatory and MUST be the first TLV in the LLDPDU.
    Each LLDPDU MUST contain one, and only one, Chassis ID TLV.


    Attributes:
        type (TLV.Type): The type of the TLV
        subtype (ChassisIdTLV.Subtype): The chassis ID subtype
        value (str, bytes or ip_address): The chassis ID.
            The type of this attribute depends on the subtype
                MAC Address -> bytes,
                Network Address -> ip_address,
                Otherwise -> str

    TLV Format:

         0                   1                   2
         0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+...+-+-+-+
        |             |                 |               |               |
        |      1      |      Length     |    Subtype    |   Chassis ID  |
        |             |                 |               |               |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+...+-+-+-+

                                                           1 - 255 byte

    Subtypes:

        A chassis may be identified in several ways, e.g. by its IP address, MAC address or a name specified by an
        administrator. The type of identification is determined by the subtype value.

        | Subtype | ID Basis          | Example                    |
        | ------- | ----------------- | -------------------------- |
        | 0       | Reserved          |                            |
        | 1       | Chassis Component | cl-SJ17-3-006:rack1:rtr-U3 |
        | 2       | Interface Alias   | office net                 |
        | 3       | Port Component    | backplane1                 |
        | 4       | MAC Address       | 02:04:df:88:a2:b4          |
        | 5       | Network Address*  | 134.96.86.110              |
        | 6       | Interface Name    | eth0                       |
        | 7       | Locally Assigned  | Frank's Computer           |
        | 8 - 255 | Reserved          |                            |

        Depending on the subtype the value is to be interpreted in a certain way.

        With the exception of subtypes 4 (MAC Address) and 5 (Network Address), as far as the LLDP agent is concerned,
        the value is a string. A distinction between these subtypes is only made by a human observer.

    MAC Address Subtype:

        MAC addresses are represented as raw bytes, e.g. the MAC address 02:04:df:88:a2:b4 corresponds to a value of
        b"\x02\x04\xDF\x88\xA2\xB4".

    Network Address Subtype:

        Network addresses are represented as raw bytes.

        In practice there are many different network protocols, each with their own address format with e.g. a different
        length.

        To determine the type of network protocol and the appropriate length of the network address transmitted in the
        Chassis ID TLV, network addresses are prefixed with an extra byte identifying the address family.

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
        CHASSIS_COMPONENT = 1
        INTERFACE_ALIAS = 2
        PORT_COMPONENT = 3
        MAC_ADDRESS = 4
        NETWORK_ADDRESS = 5
        INTERFACE_NAME = 6
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
        # TODO: Implement Done

        # TODO: check for validity of network address, mac adress here
        self.type = TLV.Type.CHASSIS_ID
        self.subtype = subtype
        self.value = id

        # Mac address case
        if self.subtype == 4:
            if len(self.value) != 6:
                raise ValueError()

        # ip address case
        elif self.subtype == 5:
            if self.value.version == 4:
                # ipv4 case
                return
            elif self.value.version == 6:
                # ipv6 case
                return
            else:
                raise ValueError()

        # all other cases:
        else:
            return

    def __bytes__(self):
        """Return the byte representation of the TLV.

        This method must return bytes. Returning a bytearray will raise a TypeError.
        See `TLV.__bytes__()` for more information.
        """
        # TODO: Implement Done
        # Mac address case
        if self.subtype == 4:
            return bytes([self.type * 2, 1 + 6, self.subtype]) + self.value
        # ip address case
        elif self.subtype == 5:
            if self.value.version == 4:
                # ipv4 case
                return bytes([self.type * 2, 1 + 5, self.subtype ,1]) + self.value.packed
            else:
                # ipv6 case
                return bytes([self.type * 2, 1 + 17, self.subtype, 2]) + self.value.packed

        #all other cases:
        else:
            if len(self.value) > 255:
                return bytes([(self.type * 2) + 1, len(self.value) - 256], self.subtype) + bytes(self.value, 'utf-8')
            else:
                return bytes([self.type * 2, len(self.value) + 1], self.subtype) + bytes(self.value,'utf-8')


    def __len__(self):
        """Return the length of the TLV value.

        This method must return an int. Returning anything else will raise a TypeError.
        See `TLV.__len__()` for more information.
        """
        # TODO: Implement DONE
        # Mac address case
        if self.subtype == 4:
            return 7
        # ip address case
        elif self.subtype == 5:
            if self.value.version == 4:
                # ipv4 case
                return 6
            else:
                # ipv6 case
                return 18

        # all other cases:
        else:
            return len(self.value) + 1

    def __repr__(self):
        """Return a printable representation of the TLV object.

        See `TLV.__repr__()` for more information.
        """
        # TODO: Implement DONE
        return "Chassis-ID subtype:" + str(self.subtype) + " with value: " + str(self.value)

    @staticmethod
    def from_bytes(data: TLV.ByteType):
        """Create a TLV instance from raw bytes.

        Args:
            data (bytes or bytearray): The packed TLV

        Raises a `ValueError` if the provided TLV contains errors (e.g. has the wrong type).
        """
        # TODO: more error cases have to implemented here, illegal ip etc
        if len(data) < 3:
            raise ValueError()

        type_shifted = data[0]
        if type_shifted != TLV.Type.CHASSIS_ID * 2:
            raise ValueError()

        length = data[1]

        if data[0] % 2 != 0:
            length += 256

        if length < 2:
            raise ValueError()

        # length does not match with expected length
        if length != len(data) - 2:
            raise ValueError()

        subtype = data[2]

        # Mac address case
        if subtype == 4:
            if length != 7:
                raise ValueError()
            return ChassisIdTLV(subtype, data[3:])
        # ip address case
        elif subtype == 5:
            if data[3] == 1:
                if length != 6:
                    raise ValueError()
                return ChassisIdTLV(subtype, IPv4Address(data[4:]))
                # ipv4 case
                return
            if data[3] == 2:
                # ipv6 case
                if length != 18:
                    raise ValueError()
                return ChassisIdTLV(subtype, IPv6Address(data[4:]))
            else:
                # Ip address with not prefix 1 or 2
                raise ValueError()

        # all other cases:
        else:
            return ChassisIdTLV(subtype, data[3:].decode("utf-8"))