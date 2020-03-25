import functools

import rlp

from eth.db.backends.base import BaseDB
from eth.db.header import HeaderDB
from eth.exceptions import HeaderNotFound
from eth.rlp.headers import BlockHeader
from eth.validation import validate_word
from eth_typing import Hash32
from eth_utils import encode_hex

from tanglevm.rlp.headers import TanglevmBlockHeader


class TanglevmHeaderDB(HeaderDB):
    @staticmethod
    def _get_block_header_by_hash(db: BaseDB, block_hash: Hash32) -> BlockHeader:
        """
        Returns the requested block header as specified by block hash.

        Raises BlockNotFound if it is not present in the db.
        """
        validate_word(block_hash, title="Block Hash")
        try:
            header_rlp = db[block_hash]
        except KeyError:
            raise HeaderNotFound("No header with hash {0} found".format(
                encode_hex(block_hash)))
        return _decode_block_header(header_rlp)

# When performing a chain sync (either fast or regular modes), we'll very often need to look
# up recent block headers to validate the chain, and decoding their RLP representation is
# relatively expensive so we cache that here, but use a small cache because we *should* only
# be looking up recent blocks.
@functools.lru_cache(128)
def _decode_block_header(header_rlp: bytes) -> TanglevmBlockHeader:
    return rlp.decode(header_rlp, sedes=TanglevmBlockHeader)
