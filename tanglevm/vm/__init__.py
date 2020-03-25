from eth._utils.headers import compute_gas_limit

from typing import Any

from eth.consensus.pow import get_cache
from eth.constants import GENESIS_GAS_LIMIT
from eth.rlp.headers import BlockHeader
from eth.validation import validate_length
from eth.vm.forks import ByzantiumVM, PetersburgVM
from eth.vm.forks.homestead import compute_homestead_difficulty
from eth_typing import Hash32

from tanglevm import TanglevmBlockHeader
from tanglevm.vm.blocks import TanglevmBlock
from tanglevm.vm.state import TanglevmState


def check_pow(block_number: int,
              mining_hash: Hash32,
              mix_hash: Hash32,
              nonce: bytes,
              difficulty: int) -> None:
    validate_length(mix_hash, 32, title="Mix Hash")
    validate_length(mining_hash, 32, title="Mining Hash")
    validate_length(nonce, 8, title="POW Nonce")
#    cache = get_cache(block_number)
#    mining_output = hashimoto_light(
#        block_number, cache, mining_hash, big_endian_to_int(nonce))
#    if mining_output[b'mix digest'] != mix_hash:
#        raise ValidationError("mix hash mismatch; {0} != {1}".format(
#            encode_hex(mining_output[b'mix digest']), encode_hex(mix_hash)))
#    result = big_endian_to_int(mining_output[b'result'])
#    validate_lte(result, 2**256 // difficulty, title="POW Difficulty")


class TanglevmVM(PetersburgVM):
    # fork name
    fork = 'tanglevm'

    # classes
    block_class = TanglevmBlock
    _state_class = TanglevmState  # type: Type[BaseState]

    @classmethod
    def validate_seal(cls, header: BlockHeader) -> None:
        """
        Validate the seal on the given header.
        """
        check_pow(
            header.block_number, header.mining_hash,
            header.mix_hash, header.nonce, header.difficulty)


    @classmethod
    def create_header_from_parent(cls,
                                  parent_header: BlockHeader,
                                  **header_params: Any) -> BlockHeader:
        """
        Creates and initializes a new block header from the provided
        `parent_header`.
        """
        if 'difficulty' not in header_params:
            # Use setdefault to ensure the new header has the same timestamp we use to calculate its
            # difficulty.
            header_params.setdefault('timestamp', parent_header.timestamp + 1)
            header_params['difficulty'] = compute_homestead_difficulty(
                parent_header,
                header_params['timestamp'],
            )
        if 'gas_limit' not in header_params:
            header_params['gas_limit'] = compute_gas_limit(
                parent_header,
                gas_limit_floor=GENESIS_GAS_LIMIT,
            )

        header = TanglevmBlockHeader.from_parent(parent=parent_header, **header_params)
        return header
