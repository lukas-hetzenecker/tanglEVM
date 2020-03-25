from demo import get_chaindb, get_chain, send_and_recv_tx
from parser.tx import empty_mam_state

from tanglevm.db.mam import MamDB

import sys
import logging
import eth.tools.logging
from eth_utils import decode_hex, encode_hex
from eth.constants import CREATE_CONTRACT_ADDRESS, ZERO_ADDRESS

from iota.types import Tag
from tanglevm.vm.transactions import TanglevmUnsignedTransaction

logging.getLogger('eth.db.account.AccountDB').setLevel(eth.tools.logging.DEBUG2_LEVEL_NUM)

logger = logging.getLogger()
logger.setLevel(eth.tools.logging.DEBUG2_LEVEL_NUM)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(eth.tools.logging.DEBUG2_LEVEL_NUM)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

_LOGGER = logging.getLogger(__name__)


# Iota Tag we are listening to

TAG = Tag(b'TANGLEVMTESTAAAA')

# Configure "sidechain"

chaindb = get_chaindb()
chain = get_chain(chaindb)
vm = chain.get_vm()
mam_state_db = MamDB(chaindb)


# MAM State for Account A

seed = b'BCRPJHFFYZCPXNDGOVKKOXCMOUNRJXAYBEWRDLOOEBRZXSLHQCRAUCZ9JHJNUGTIBS99VCSSMEXYKAAAC'
state = empty_mam_state(seed)


# Send create transaction for SuperToken contract

tx = TanglevmUnsignedTransaction(
    nonce=0,
    gas_price=0,
    gas=5000000,
    to=CREATE_CONTRACT_ADDRESS,
    value=0,
    data=decode_hex(open('contracts/SuperToken/SuperToken.bin', 'r').read()),
)

state = send_and_recv_tx(tx, TAG, chain, mam_state_db, state)
_LOGGER.info("state after send: %s", state)

# Send transfer contract call

# contract_address = generate_contract_address(b'@\x94\xd4\xc32\xe4g\x87[\xeby_8\xc8!{\x88\xd33\xda', 0)
contract_address = b'X\xc91\x10\x15\xcd\xeb\xe3\xce\xec@3\xc2\x8f\x0c\t\xa1\xa6\xc1\x07'
tx = TanglevmUnsignedTransaction(
    nonce=1,
    gas_price=0,
    gas=5000000,
    to=contract_address,
    value=0,
    data=decode_hex('a9059cbb000000000000000000000000' +  # function selector transfer
                    'ada5547578a08c7d991811c83616b7f3ed33b795' +  # param1 to: ada...
                    '0000000000000000000000000000000000000000000000000000000000001337'  # param2 amount: 4919
                    ),
)

state = send_and_recv_tx(tx, TAG, chain, mam_state_db, state)

# mine block
block = vm.finalize_block(chain.get_block())
block = chain.mine_block(coinbase=ZERO_ADDRESS)
print(str(block))
print(repr(block))
for tx in block.transactions:
    print("TX: ", tx.__dict__)


# Verify contract was deployed correctly

tx = TanglevmUnsignedTransaction(
    nonce=2,
    gas_price=0,
    gas=5000000,
    to=contract_address,
    value=0,
    data=decode_hex('70a08231' + # function selector balanceOf
                    '000000000000000000000000ada5547578a08c7d991811c83616b7f3ed33b795' # param1 address: ada...
                    ),
)
signed_tx = tx.as_signed_transaction(b'\x12\x1f\xc7\x96D\x14\xcf<$q\xad\xc4\xbaj\xaa\xf0Q&\t\x01')

balanceAda = chain.get_transaction_result(signed_tx, chain.get_canonical_head())
print("raw balanceOf ada", balanceAda)

balanceAda = int(encode_hex(balanceAda), 16)
print("balanceOf ada", balanceAda)


tx = TanglevmUnsignedTransaction(
    nonce=2,
    gas_price=0,
    gas=5000000,
    to=contract_address,
    value=0,
    data=decode_hex('18160ddd' # function selector totalSupply
                    ),
)
signed_tx = tx.as_signed_transaction(b'\x12\x1f\xc7\x96D\x14\xcf<$q\xad\xc4\xbaj\xaa\xf0Q&\t\x01')

totalSupply = chain.get_transaction_result(signed_tx, chain.get_canonical_head())
print("raw totalSupply", totalSupply)

totalSupply = int(encode_hex(totalSupply), 16)
print("totalSupply", totalSupply)
