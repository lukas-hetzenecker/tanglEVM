from eth.db.chain import ChainDB

from tanglevm.db.header import TanglevmHeaderDB
from tanglevm.rlp.headers import TanglevmBlockHeader


class TanglevmChainDB(TanglevmHeaderDB, ChainDB):
    pass