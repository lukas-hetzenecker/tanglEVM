import rlp
from rlp.sedes import (
    big_endian_int,
)

from eth.constants import (
    EMPTY_SHA3,
    BLANK_ROOT_HASH,
    ZERO_ADDRESS)

from eth.rlp.sedes import (
    trie_root,
    hash32,
    address)

#from .sedes import (
#    address
#)

from eth_typing import (
    Address
)

from typing import Any


#ZERO_ADDRESS = Address(b'9' * 81)
ZERO_IOTA_ADDRESS = Address(b'9' * 81)

class Account(rlp.Serializable):
    """
    RLP object for accounts.
    """
    fields = [
#        ('root', address),
#        ('prev_root', address),
        ('nonce', big_endian_int),
        ('balance', big_endian_int),
        ('storage_root', trie_root),
        ('code_hash', hash32)
    ]

    def __init__(self,
                 #root: Address=ZERO_ADDRESS,
                 #prev_root: Address=ZERO_ADDRESS,
                 nonce: int=0,
                 balance: int = 0,
                 storage_root: bytes=BLANK_ROOT_HASH,
                 code_hash: bytes=EMPTY_SHA3,
                 **kwargs: Any) -> None:
        #super().__init__(root, prev_root, nonce, balance, storage_root, code_hash, **kwargs)
        super().__init__(nonce, balance, storage_root, code_hash, **kwargs)
