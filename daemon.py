from parser.tx import recv_tx
from tanglevm.db.mam import MamDB

import zmq.asyncio

import sys
import logging
import eth.tools.logging

from tanglevm.chains.base import TanglevmChain
from tanglevm.vm import TanglevmVM

from pathlib import Path

from eth.db.atomic import AtomicDB
from eth.db.backends.level import LevelDB
from eth import constants

import os

import asyncio
import zmq
import zmq.asyncio
from iota import Transaction
from iota.types import Tag

logging.getLogger('eth.db.account.AccountDB').setLevel(eth.tools.logging.DEBUG2_LEVEL_NUM)

logger = logging.getLogger()
logger.setLevel(eth.tools.logging.DEBUG2_LEVEL_NUM)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(eth.tools.logging.DEBUG2_LEVEL_NUM)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

_LOGGER = logging.getLogger(__name__)

IOTA_HOST = os.environ.get('IOTA_HOST', 'localhost')
IOTA_ZMQ_PORT = int(os.environ.get('ZMQ_PORT', '5556'))
TAG = Tag(os.environ.get('TAG', 'TANGLEVMTESTAAAA').encode('ascii'))

zmq_ctx = zmq.asyncio.Context()

GENESIS_PARAMS = {
    'parent_hash': constants.GENESIS_PARENT_HASH,
    'uncles_hash': constants.EMPTY_UNCLE_HASH,
    'coinbase': constants.ZERO_ADDRESS,
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
   __name__='TanglevmChain',
    vm_configuration=(
        (constants.GENESIS_BLOCK_NUMBER, TanglevmVM),
    ))

chaindb = AtomicDB(LevelDB(Path('chain.leveldb')))
chain = klass.from_genesis(chaindb, GENESIS_PARAMS)

vm = chain.get_vm()

mam_state_db = MamDB(chaindb)


async def zmq_iota_recv():
    print("Connecting to ZMQ...")
    s = zmq_ctx.socket(zmq.SUB)
    s.connect('tcp://%s:%s' % (IOTA_HOST, IOTA_ZMQ_PORT))
    print("Subscribing to tx_trytes...")
    s.subscribe(b"tx_trytes")

    # TODO: clean up incomplete bundles
    while True:
        msg = await s.recv()
        #print('received', msg)
        topic, data, hash_ = msg.split(b' ')

        iota_tx = Transaction.from_tryte_string(data, hash_)

        if iota_tx.tag != TAG:
            continue

        print(iota_tx)

        recv_tx(iota_tx, chain, mam_state_db)


async def mine_block():
    while True:
        print("MINE BLOCK")

        block = vm.finalize_block(chain.get_block())
        block = chain.mine_block(coinbase=constants.ZERO_ADDRESS)
        print(str(block))
        print(repr(block))
        for tx in block.transactions:
            print("TX: ", tx.__dict__)

        await asyncio.sleep(20)

loop = asyncio.get_event_loop()
asyncio.ensure_future(zmq_iota_recv())
asyncio.ensure_future(mine_block())

loop.run_forever()
loop.close()
