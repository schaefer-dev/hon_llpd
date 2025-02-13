from lldp.tlv import TLV


class OrganizationallySpecificTLV(TLV):
    """Organizationally Specific TLV

    This TLV type is provided to allow organizations, software developers and equipment vendors to define TLVs
    to advertise information to remote devices which can not be included in other TLV types.

    It is an optional TLV and as such may be included in an LLDPDU zero or more times between the TTL TLV and the
    End of LLDPDU TLV.

    Attributes:
        type    (TLV.Type): The type of the TLV
        oui     (bytes or bytearray): Organizationally unique identifier
        subtype (bytes or bytearray): Organizationally defined subtype
        value   (bytes or bytearray): Organizationally defined information


    TLV Format:

         0               1               2               5               6
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-...-+-+-+-+-+-+-+-+-+-+-+-+-+-+-...-+-+-+-+-+-|
        |             |                 |    Organiz.   |    Organiz.   |   Organizationally  |
        |     127     |      Length     |   Unique ID   |    Defined    | Defined Information |
        |             |                 |     (OUI)     |    Subtype    |       (Value)       |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-...-+-+-+-+-+-+-+-+-+-+-+-+-+-+-...-+-+-+-+-+-|

                                                                             0 - 507 byte

    The OUI is a 24 bit number uniquely identifying a vendor, manufacturer or organization.

    The subtype should be a unique subtype value assigned by the defining organization.
    """

    def __init__(self, oui: TLV.ByteType, subtype: TLV.ByteType, value):
        """Constructor

        Parameters:
            oui (bytes or bytearray): The OUI. See above
            subtype (bytes or bytearray): The organizationally defined subtype
            value (any): The value
        """
        self.type = TLV.Type.ORGANIZATIONALLY_SPECIFIC
        self.oui = oui
        self.subtype = subtype
        self.value = None
        if value is not None:
            self.value = bytes(str(value), 'utf-8')

        if len(oui) != 3:
            raise ValueError
        if len(self.value) > 507:
            raise ValueError

    def __bytes__(self):
        """Return the byte representation of the TLV.

        This method must return bytes. Returning a bytearray will raise a TypeError.
        See `TLV.__bytes__()` for more information.
        """
        return bytes([self.type * 2, 4 + len(self.value)]) + self.oui + self.subtype + self.value

    def __len__(self):
        """Return the length of the TLV value.

        This method must return an int. Returning anything else will raise a TypeError.
        See `TLV.__len__()` for more information.
        """
        # TODO: Implement DONE
        return 4 + len(self.value)

    def __repr__(self):
        """Return a printable representation of the TLV object.

        See `TLV.__repr__()` for more information.
        """
        return "OrganizationallySpecificTLV(" + repr(self.oui) + ", " + repr(self.subtype) + ", " + repr(self.value) + ")"

    @staticmethod
    def from_bytes(data: TLV.ByteType):
        """Create a TLV instance from raw bytes.

        Args:
            data (bytes or bytearray): The packed TLV

        Raises a `ValueError` if the provided TLV contains errors (e.g. has the wrong type).
        """
        type = data[0] >> 1

        if type != TLV.Type.ORGANIZATIONALLY_SPECIFIC:
            raise ValueError

        length = data[1]

        if data[0] % 2 != 0:
            length += 256

        if length < 4 or length > 511:
            raise ValueError

        oui = ((data[2] << 16) + (data[3] << 8) + data[4]).to_bytes(3, 'big')

        subtype = data[5].to_bytes(1, 'big')

        value = None

        if length > 4:
            value = data[6:].decode("utf-8")

        return OrganizationallySpecificTLV(oui, subtype, value)