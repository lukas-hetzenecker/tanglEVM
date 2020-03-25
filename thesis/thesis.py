import binascii
import rlp
from eth_keys.datatypes import PrivateKey
from eth_utils import decode_hex, to_normalized_address
from eth_utils import (
    to_canonical_address,
)


# ADDRESSES
from eth._utils.address import generate_contract_address

ada_addr = '0xAda5547578a08C7d991811c83616b7F3eD33B795'
ada_privkey = '0x93d40de6b5146f6c2535344261dd011fb250e4c22d4c2290fdb3e0d9739c4534'

becca_addr = '0xBecca0DaD3F3a8095e450d1DE9cDD7f18cF077Af'
becca_privkey = '0xc50de8a23afb2dd1fd05b5a79cf19d67c4949bc7857e965c2b9ef32794e14388'

from eth.vm.forks.istanbul.transactions import IstanbulUnsignedTransaction

private_key = PrivateKey(
        decode_hex(becca_privkey)
    )

public_key = private_key.public_key

canoncial_address = public_key.to_canonical_address()
address = public_key.to_address()
checksum_address = public_key.to_checksum_address()

data = ("a9059cbb" # transfer
"000000000000000000000000Ada5547578a08C7d991811c83616b7F3eD33B795"  # to
"0000000000000000000000000000000000000000000000000000000000001337")  # 3 (18 decimals)
#hex 1337
#dec 4919

contract_address = to_normalized_address(generate_contract_address(canoncial_address, 3))

unsigned_tx = IstanbulUnsignedTransaction(
    nonce=4,
    gas_price=13,
    gas=5000000,
    to=to_canonical_address('0x5643f85c81eececd195d4cc29c9b9877337a1550'),
    value=0,
    data=decode_hex(data),
)

signed_tx = unsigned_tx.as_signed_transaction(private_key, chain_id=1908)

print("contract_address: %s" % contract_address)
print("private key: %s" % private_key)
print("public key: %s" % public_key)
print("canoncial address: %s" % canoncial_address)
print("address: %s" % address)
print("checksum address: %s" % checksum_address)
print("unsigned tx: %s" % binascii.hexlify(rlp.encode(unsigned_tx)))
print("signed tx: %s" % binascii.hexlify(rlp.encode(signed_tx)))

