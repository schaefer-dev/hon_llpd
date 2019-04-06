from lldp.tlv import TLV


class LLDPDU:
    """LLDP Data Unit

    The LLDP Data Unit contains an ordered sequence of TLVs, three mandatory TLVs followed by zero or more optional TLVs
    plus an End Of LLDPDU TLV.

    Optional TLVs may be inserted in any order.

    An LLDPDU has to fit inside one Ethernet frame and cannot be split.

    LLDPDU Format:

        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-...-+-+-+-+-+-+-+-+
        |                 |                 |                 |                                 |
        | Chassis ID TLV  |   Port ID TLV   |     TTL TLV     |         (Optional TLVs)         |
        |                 |                 |                 |                                 |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-...-+-+-+-+-+-+-+-+
    """
    def __init__(self, *tlvs):
        self.__tlvs = []
        """List of included TLVs"""

        if len(tlvs) > 0:
            for tlv in tlvs:
                self.append(tlv)

    def __len__(self) -> int:
        """Get the number of TLVs in the LLDPDU"""
        return len(self.__tlvs)

    def __bytes__(self) -> bytes:
        """Get the byte representation of the LLDPDU"""
        res = b""
        for tlv in self.__tlvs:
            res += bytes(tlv)
        return res

    def __getitem__(self, item: int) -> TLV:
        """Get the TLV at position `item`"""
        return self.__tlvs[item]

    def __repr__(self):
        """Return a representation of the LLDPDU"""
        return "{}({})".format(self.__class__.__name__, repr(self.__tlvs))

    def __str__(self):
        """Return a printable representation of the LLDPDU"""
        return repr(self)

    def append(self, tlv: TLV):
        """Append `tlv` to the LLDPDU

        This method adds the given tlv to the LLDPDU.

        If adding the TLV makes the LLDPDU invalid (e.g. by adding a TLV after an EndOfLLDPDU TLV) it should raise a
        `ValueError`. Conditions for specific TLVs are detailed in each TLV's class description.
        """


        # TODO: BIG IMPORTANT: Implement error checks that are explained in the TLVs class description
        if len(self.__tlvs) == 0:
            if tlv.type != TLV.Type.CHASSIS_ID:
                raise ValueError()
            else:
                self.__tlvs.append(tlv)
        elif len(self.__tlvs) == 1:
            if tlv.type != TLV.Type.PORT_ID:
                raise ValueError()
            else:
                self.__tlvs.append(tlv)
        elif len(self.__tlvs) == 2:
            if tlv.type != TLV.Type.TTL:
                raise ValueError()
            else:
                self.__tlvs.append(tlv)
        # case for last element is already end of lldpu
        elif self.__tlvs[len(self.__tlvs)-1].type == TLV.Type.END_OF_LLDPDU:
            raise ValueError()
        else:
            self.__tlvs.append(tlv)
            if len(self.__bytes__()) > 1500:
                raise ValueError()



    def complete(self):
        """Check if LLDPDU is complete.

        An LLDPDU is complete when it includes at least the mandatory TLVs (Chassis ID, Port ID, TTL).
        """
        if len(self.__tlvs) < 3:
            return False
        if self.__tlvs[0].type == TLV.Type.CHASSIS_ID and self.__tlvs[1].type == TLV.Type.PORT_ID and self.__tlvs[2].type == TLV.Type.TTL:
            return True
        else:
            return False

    @staticmethod
    def from_bytes(data: bytes):
        """Create an LLDPDU instance from raw bytes.

        Args:
            data (bytes or bytearray): The packed LLDPDU

        Raises a value error if the provided TLV is of unknown type. Apart from that validity checks are left to the
        subclass.
        """
        # TODO: Implement
        return NotImplemented
