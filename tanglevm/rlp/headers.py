import time
from typing import (
    Optional,
    Tuple,
    Union,
    overload,
)

import rlp
from eth.rlp.headers import BlockHeader
from eth.rlp.sedes import hash32, trie_root, uint256, address
from rlp.sedes import (
    big_endian_int,
    Binary,
    binary,
)

from eth_typing import (
    Address,
    Hash32,
)

from eth_hash.auto import keccak

from eth_utils import (
    encode_hex,
)

from eth.constants import (
    ZERO_HASH32,
    EMPTY_UNCLE_HASH,
    GENESIS_NONCE,
    GENESIS_PARENT_HASH,
    BLANK_ROOT_HASH,
    ZERO_ADDRESS)

from eth.vm.execution_context import (
    ExecutionContext,
)

#from .sedes import address

#ZERO_ADDRESS = Address(b'9' * 81)

class TanglevmBlockHeader(BlockHeader):
    fields = [
        ('parent_hash', hash32),
        ('uncles_hash', hash32),
        ('coinbase', address),
        ('state_root', trie_root),
        ('transaction_root', trie_root),
        ('receipt_root', trie_root),
        ('bloom', uint256),
        ('difficulty', big_endian_int),
        ('block_number', big_endian_int),
        ('gas_limit', big_endian_int),
        ('gas_used', big_endian_int),
        ('timestamp', big_endian_int),
        ('extra_data', binary),
        ('mix_hash', binary),
        ('nonce', Binary(8, allow_empty=True))
    ]

    @overload  # noqa: F811
    def __init__(self,
                 difficulty: int,
                 block_number: int,
                 gas_limit: int,
                 timestamp: int=None,
                 coinbase: Address=ZERO_ADDRESS,
                 parent_hash: Hash32=ZERO_HASH32,
                 uncles_hash: Hash32=EMPTY_UNCLE_HASH,
                 state_root: Hash32=BLANK_ROOT_HASH,
                 transaction_root: Hash32=BLANK_ROOT_HASH,
                 receipt_root: Hash32=BLANK_ROOT_HASH,
                 bloom: int=0,
                 gas_used: int=0,
                 extra_data: bytes=b'',
                 mix_hash: Hash32=ZERO_HASH32,
                 nonce: bytes=GENESIS_NONCE) -> None:
        ...

    def __init__(self,              # type: ignore  # noqa: F811
                 difficulty: int,
                 block_number: int,
                 gas_limit: int,
                 timestamp: int=None,
                 coinbase: Address=ZERO_ADDRESS,
                 parent_hash: Hash32=ZERO_HASH32,
                 uncles_hash: Hash32=EMPTY_UNCLE_HASH,
                 state_root: Hash32=BLANK_ROOT_HASH,
                 transaction_root: Hash32=BLANK_ROOT_HASH,
                 receipt_root: Hash32=BLANK_ROOT_HASH,
                 bloom: int=0,
                 gas_used: int=0,
                 extra_data: bytes=b'',
                 mix_hash: Hash32=ZERO_HASH32,
                 nonce: bytes=GENESIS_NONCE) -> None:
        if timestamp is None:
            timestamp = int(time.time())
        super().__init__(
            parent_hash=parent_hash,
            uncles_hash=uncles_hash,
            coinbase=coinbase,
            state_root=state_root,
            transaction_root=transaction_root,
            receipt_root=receipt_root,
            bloom=bloom,
            difficulty=difficulty,
            block_number=block_number,
            gas_limit=gas_limit,
            gas_used=gas_used,
            timestamp=timestamp,
            extra_data=extra_data,
            mix_hash=mix_hash,
            nonce=nonce,
        )

    @classmethod
    def from_parent(cls,
                    parent: 'BlockHeader',
                    gas_limit: int,
                    difficulty: int,
                    timestamp: int,
                    coinbase: Address=ZERO_ADDRESS,
                    nonce: bytes=None,
                    extra_data: bytes=None,
                    transaction_root: bytes=None,
                    receipt_root: bytes=None) -> 'BlockHeader':
        """
        Initialize a new block header with the `parent` header as the block's
        parent hash.
        """
        header_kwargs = {
            'parent_hash': parent.hash,
            'coinbase': coinbase,
            'state_root': parent.state_root,
            'gas_limit': gas_limit,
            'difficulty': difficulty,
            'block_number': parent.block_number + 1,
            'timestamp': timestamp,
        }
        if nonce is not None:
            header_kwargs['nonce'] = nonce
        if extra_data is not None:
            header_kwargs['extra_data'] = extra_data
        if transaction_root is not None:
            header_kwargs['transaction_root'] = transaction_root
        if receipt_root is not None:
            header_kwargs['receipt_root'] = receipt_root

        header = cls(**header_kwargs)
        return header
