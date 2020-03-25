from eth.vm.spoof import SpoofTransaction
from iota.crypto.kerl import conv, Kerl

from demo import get_chain, get_chaindb, send_and_recv_tx
from parser.tx import empty_mam_state

from tanglevm.db.mam import MamDB

import sys
import logging
import eth.tools.logging
from eth_utils import decode_hex
from eth.constants import CREATE_CONTRACT_ADDRESS, ZERO_ADDRESS

from iota.types import Tag

from tanglevm.helper import decodeTryteStringFromBytes
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


# Send create transaction for Hash contract

tx = TanglevmUnsignedTransaction(
    nonce=0,
    gas_price=0,
    gas=5000000,
    to=CREATE_CONTRACT_ADDRESS,
    value=0,
    data=decode_hex(open('contracts/TwoValues_curl/Hash.bin', 'r').read().strip()),
)

state = send_and_recv_tx(tx, TAG, chain, mam_state_db, state)

# mine block
block = vm.finalize_block(chain.get_block())
block = chain.mine_block(coinbase=ZERO_ADDRESS)
print(str(block))
print(repr(block))
for tx in block.transactions:
    print("TX: ", tx.__dict__)

# Call myhash (no TX on blockchain)

# contract_address = generate_contract_address(b'@\x94\xd4\xc32\xe4g\x87[\xeby_8\xc8!{\x88\xd33\xda', 0)
contract_address = b'X\xc91\x10\x15\xcd\xeb\xe3\xce\xec@3\xc2\x8f\x0c\t\xa1\xa6\xc1\x07'


input = 'EMIDYNHBWMBCXVDEFOFWINXTERALUKYYPPHKP9JJFGJEIUY9MUDVNFZHMMWZUYUSWAIOWEVTHNWMHANBH'

tx = SpoofTransaction(
    TanglevmUnsignedTransaction(
        nonce=1,
        gas_price=0,
        gas=5000000,
        to=contract_address,
        value=0,
        data=decode_hex('7dc4a9ec' +  # hexlify(keccak(b'myhash(bytes)'))[:8]
                        '00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000032716de2e6a87c53992ba72dd190eb332d246ad6834dc8525dc3c052d253c1702cec74caf1d292d501d0344cbcd3e5a51608f40000000000000000000000000000')  # encodeTryteStringAsBytes(input)
    ),
    from_=ZERO_ADDRESS  # sender does not matter for myhash function
)

result = chain.get_transaction_result(tx, chain.get_canonical_head())
print("result", result)

# strip first 14 bytes padding
result = result[14:]

actual_result = decodeTryteStringFromBytes(result)
print("actual result:   ", actual_result)

# Calculate expected result

trits = conv.trytes_to_trits(input)
kerl = Kerl()
kerl.absorb(trits)
trits_out = []
kerl.squeeze(trits_out, length=243)
expected_result = conv.trits_to_trytes(trits_out)
print("expected result: ", expected_result)
