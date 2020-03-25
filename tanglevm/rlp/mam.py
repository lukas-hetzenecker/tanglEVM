from typing import Any

import rlp
from eth_typing import Address

#from tanglevm.rlp.accounts import ZERO_ADDRESS
from tanglevm.rlp.accounts import ZERO_IOTA_ADDRESS
from tanglevm.rlp.sedes import iota_address

class MamState(rlp.Serializable):
    """
    RLP object for accounts.
    """
    fields = [
        ('root', iota_address),
        ('prev_root', iota_address),
    ]

    def __init__(self,
                 root: Address=ZERO_IOTA_ADDRESS,
                 prev_root: Address=ZERO_IOTA_ADDRESS,
                 **kwargs: Any) -> None:
        super().__init__(root, prev_root, **kwargs)
