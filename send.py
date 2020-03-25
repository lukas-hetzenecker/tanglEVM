#!/usr/bin/env python3
import os
import sys
import json
import iota

from parser.tx import send_tx, empty_mam_state
from tanglevm.vm.transactions import TanglevmUnsignedTransaction

from eth.validation import validate_canonical_address
from eth_typing import Address
from eth_utils import decode_hex

from pprint import pprint


IOTA_URI = os.environ.get('IOTA_URI', 'http://localhost:14265')
min_weight_magnitude = 4

if len(sys.argv) != 7:
    print("send.py <seed> <tag> <state-file> <nonce> <to address> <data>")
    sys.exit(1)

_, seed, tag, state_file, nonce, to, data = sys.argv
seed = seed.encode('ascii')
nonce = int(nonce)
if to == '_':
    to = Address(b'')
else:
    to = decode_hex(to)  # decode_hex strips the 0x prefix (in contrast to binascii.unhexlify)
    validate_canonical_address(to)

try:
    with open(state_file, 'r') as f:
        state = json.load(f)
except FileNotFoundError:
    state = empty_mam_state(seed)

tx = TanglevmUnsignedTransaction(
    nonce=nonce,
    gas_price=0,
    gas=5000000,
    to=to,
    value=0,
    data=decode_hex(data),
)

new_state, pb = send_tx(state, tx, tag)

api = iota.Iota(IOTA_URI)
bundle = api.send_transfer(depth=3,
                           transfers=pb,
                           min_weight_magnitude=min_weight_magnitude)['bundle']
print("Generated bundle hash: %s" % bundle.hash)
print("TXs:\n")
for txn in bundle:
    pprint(vars(txn))
    print("")

with open(state_file, 'w') as f:
    json.dump(new_state, f)
