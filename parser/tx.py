import json
import logging
import subprocess
from pprint import pprint

import iota
import rlp
from eth_utils import keccak

from tanglevm.helper import encodeBytesAsTryteString, decodeBytesFromTryteString
from tanglevm.vm.transactions import TanglevmUnsignedTransaction

_LOGGER = logging.getLogger(__name__)


ZERO_ADDRESS = iota.Address(b'9' * 81)

bundles = dict()


def recv_tx(iota_tx, chain, mam_state_db):
    bundle_hash = str(iota_tx.bundle_hash)
    if bundle_hash not in bundles:
        bundles[bundle_hash] = [None] * (iota_tx.last_index + 1)
    bundles[bundle_hash][iota_tx.current_index] = str(iota_tx.signature_message_fragment)

    if not None in bundles[bundle_hash]:
        # bundle complete
        iota_message = ''.join(bundles[bundle_hash])

        print("address", iota_tx.address)
        address = bytes(iota_tx.address)

        first_mam_root = mam_state_db.get_root(address)
        print("mam_root of first message in channel is", first_mam_root)

        out = subprocess.Popen(['node', './parser/helper/decrypt.js', iota_message, address],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        print("stdout: ", stdout)
        print("stderr: ", stderr)

        if stderr:
            _LOGGER.error('Error when decrypting message!')
            _LOGGER.error('Error: %s' % stderr)
            return

        data = stdout.decode('utf8')
        data = json.loads(data)

        mam_payload = data['payload']
        next_root = bytes(data['next_root'], "ascii")
        payload = decodeBytesFromTryteString(mam_payload)
        print("payload", payload)

        evm_tx = rlp.decode(payload, TanglevmUnsignedTransaction)
        print("evm_tx", evm_tx)

        if first_mam_root == ZERO_ADDRESS:
            # first known message in MAM state
            if evm_tx.nonce != 0:
                _LOGGER.error('Expected nonce to be 0')
                return
            first_mam_root = address

        mam_state_db.set_root(next_root, first_mam_root)
        mam_state_db.set_prev_root(next_root, address)

        root_evm_address = keccak(first_mam_root)[:20]
        print("sender address is", root_evm_address)
        signed_evm_tx = evm_tx.as_signed_transaction(root_evm_address)
        new_block, receipt, computation = chain.apply_transaction(signed_evm_tx)

        print("gas used", receipt.gas_used)

        computation.raise_if_error()

        contract_address = computation.msg.storage_address
        print("contract_address", contract_address)


def send_tx(state, tx, tag):
    trytes = encodeBytesAsTryteString(rlp.encode(tx))

    print("send tx", str(trytes))
    out = subprocess.Popen(['node', './parser/helper/create.js', json.dumps(state), str(trytes)],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()

    mam_message = stdout.decode('utf8')
    mam_message = json.loads(mam_message)
    payload = mam_message['payload']
    address = mam_message['address']

    _LOGGER.info("total message length", len(iota.TryteString(payload)))

    pt = iota.ProposedTransaction(address=iota.Address(address), # 81 trytes long address
                                  message=iota.TryteString(payload),
                                  tag=iota.Tag(tag), # Up to 27 trytes
                                  value=0)

    pb = iota.ProposedBundle(transactions=[pt])
    pb.finalize()

    # bundle is broadcasted, let's print it
    print("\nGenerated bundle hash: %s" % pb.hash)
    print("\nTail Transaction in the Bundle is a transaction #%s." % pb.tail_transaction.current_index)

    print("\nList of all transactions in the bundle:\n")
    for txn in pb:
        pprint(vars(txn))
        print("")

    return mam_message['state'], pb


def empty_mam_state(seed):
    state = {
        'seed': seed.decode(),
        'subscribed': [],
        'channel': {
            'side_key': None,
            'mode': 'public',
            'next_root': None,
            'security': 2,
            'start': 0,
            'count': 1,
            'next_count': 1,
            'index': 0
        }
    }
    return state
