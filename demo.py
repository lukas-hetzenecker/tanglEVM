# Helper class to configure chain and initialize MAM state

from eth.db.backends.memory import MemoryDB

from eth.constants import ZERO_ADDRESS
from parser.tx import send_tx, recv_tx

from tanglevm.chains.base import TanglevmChain
from tanglevm.vm import TanglevmVM

from eth.db.atomic import AtomicDB
from eth import constants


def get_chaindb():
    return AtomicDB(MemoryDB())


def get_chain(chaindb):
    GENESIS_PARAMS = {
        'parent_hash': constants.GENESIS_PARENT_HASH,
        'uncles_hash': constants.EMPTY_UNCLE_HASH,
        'coinbase': ZERO_ADDRESS,
        'transaction_root': constants.BLANK_ROOT_HASH,
        'receipt_root': constants.BLANK_ROOT_HASH,
        'difficulty': 1,
        'block_number': constants.GENESIS_BLOCK_NUMBER,
        'gas_limit': 10000000,
        'timestamp': 1514764800,
        'extra_data': constants.GENESIS_EXTRA_DATA,
        'nonce': constants.GENESIS_NONCE
    }

    klass = TanglevmChain.configure(
        __name__='TanglEVMChain',
        vm_configuration=(
            (constants.GENESIS_BLOCK_NUMBER, TanglevmVM),
        ))

    chain = klass.from_genesis(chaindb, GENESIS_PARAMS)

    return chain


# For the demo, we assume a published transaction is immediately received

def send_and_recv_tx(tx, tag, chain, mam_state_db, state):
    _state, pb = send_tx(state, tx, tag)
    for _tx in pb:
        recv_tx(_tx, chain, mam_state_db)
    return _state
