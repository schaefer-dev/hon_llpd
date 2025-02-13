from lldp.tlv import TLV
from lldp.tlv import ChassisIdTLV, TTLTLV, EndOfLLDPDUTLV, ManagementAddressTLV, OrganizationallySpecificTLV
from lldp.tlv import PortIdTLV, PortDescriptionTLV, SystemDescriptionTLV, SystemNameTLV, SystemCapabilitiesTLV


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

        # Chassis_ID has to be conained and the first one!
        if len(self.__tlvs) == 0:
            if tlv.type != TLV.Type.CHASSIS_ID:
                raise ValueError()
            else:
                self.__tlvs.append(tlv)
                return
        else:
            # Port_ID has to be conained and the second one!
            if len(self.__tlvs) == 1:
                if tlv.type != TLV.Type.PORT_ID:
                    raise ValueError()
                else:
                    self.__tlvs.append(tlv)
                    return
            # TTL has to be conained and the third one!
            elif len(self.__tlvs) == 2:
                if tlv.type != TLV.Type.TTL:
                    raise ValueError()
                else:
                    self.__tlvs.append(tlv)
                    return
            else:
                # forth and following TLVs can not be chassis ID, portid or ttl
                if tlv.type == TLV.Type.CHASSIS_ID or tlv.type == TLV.Type.TTL or tlv.type == TLV.Type.PORT_ID:
                    raise ValueError()

        # No TLVs after END_OF_LLDPU
        if len(self.__tlvs) != 0 and self.__tlvs[len(self.__tlvs)-1].type == TLV.Type.END_OF_LLDPDU:
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
        # check if contains mandatory first 3 TLVs
        if self.__tlvs[0].type == TLV.Type.CHASSIS_ID and self.__tlvs[1].type == TLV.Type.PORT_ID and self.__tlvs[2].type == TLV.Type.TTL:
            # IMPORTANT REMARK: the slides say that end-of-lldpdu TLV is optional, but wireshark marks such frames as malformed.
            # Online, the majority of sources claim that this TLV is mandatory at the end of the TLV list. I still decided to
            # adhere to the information on the slides, but wanted to clarify here that I knew of this before submission.

            # check if TLV ends with END_OF_LLDPDU
            #if self.__tlvs[len(self.__tlvs) - 1].type == TLV.Type.END_OF_LLDPDU:
            #    return True
            #else:
            #    return False
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
        lldpu = LLDPDU()

        current_byte = 0
        next_current_byte = 0

        while True:
            type = data[current_byte] >> 1
            if type > 8 and type != 127:
                raise ValueError()

            length = data[current_byte+1]
            if data[current_byte] % 2 == 1:
                length += 256
            next_current_byte = current_byte + 2 + length
            tlv = None
            # call TLV constructor depending on the TLV-type
            if type == TLV.Type.CHASSIS_ID:
                tlv = ChassisIdTLV.from_bytes(data[current_byte:next_current_byte])
            elif type == TLV.Type.PORT_ID:
                tlv = PortIdTLV.from_bytes(data[current_byte:next_current_byte])
            elif type == TLV.Type.TTL:
                tlv = TTLTLV.from_bytes(data[current_byte:next_current_byte])
            elif type == TLV.Type.END_OF_LLDPDU:
                tlv = EndOfLLDPDUTLV.from_bytes(data[current_byte:next_current_byte])
            if type == TLV.Type.MANAGEMENT_ADDRESS:
                tlv = ManagementAddressTLV.from_bytes(data[current_byte:next_current_byte])
            elif type == TLV.Type.ORGANIZATIONALLY_SPECIFIC:
                tlv = OrganizationallySpecificTLV.from_bytes(data[current_byte:next_current_byte])
            elif type == TLV.Type.PORT_ID:
                tlv = PortIdTLV.from_bytes(data[current_byte:next_current_byte])
            elif type == TLV.Type.SYSTEM_NAME:
                tlv = SystemNameTLV.from_bytes(data[current_byte:next_current_byte])
            if type == TLV.Type.SYSTEM_DESCRIPTION:
                tlv = SystemDescriptionTLV.from_bytes(data[current_byte:next_current_byte])
            elif type == TLV.Type.PORT_DESCRIPTION:
                tlv = PortDescriptionTLV.from_bytes(data[current_byte:next_current_byte])
            elif type == TLV.Type.SYSTEM_CAPABILITIES:
                tlv = SystemCapabilitiesTLV.from_bytes(data[current_byte:next_current_byte])

            lldpu.append(tlv)
            current_byte = next_current_byte

            if current_byte >= len(data):
                return lldpu
