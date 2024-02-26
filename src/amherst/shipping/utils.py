from __future__ import annotations

from shipr import express as el


def address_as_str(pf_address: el.types.AddressPF) -> str:
    lines = [pf_address.address_line1, pf_address.address_line2, pf_address.address_line3]
    ls = ' '.join(line for line in lines if line)

    return ls
