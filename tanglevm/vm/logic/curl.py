from iota.crypto.kerl import conv, Kerl
from iota.crypto import Curl

from eth import constants
from eth._utils.numeric import (
    ceil32,
)
from eth.vm.computation import BaseComputation
from tanglevm.helper import decodeTryteStringFromBytes, encodeTryteStringAsBytes


def curl(computation: BaseComputation) -> None:
    start_position, size = computation.stack_pop_ints(2)

    computation.extend_memory(start_position, size)

    curl_bytes = computation.memory_read_bytes(start_position, size)
    word_count = ceil32(len(curl_bytes)) // 32

    gas_cost = constants.GAS_SHA3WORD * word_count
    computation.consume_gas(gas_cost, reason="CURL: word gas cost")

    print("curl_bytes", curl_bytes)
    trytes = decodeTryteStringFromBytes(curl_bytes)
    trits = conv.trytes_to_trits(trytes)
    kerl = Kerl()
    kerl.absorb(trits)
    trits_out = []
    kerl.squeeze(trits_out)
    trytes_out = conv.trits_to_trytes(trits_out)
    bytes_result = encodeTryteStringAsBytes(trytes_out)
    print("bytes_result", bytes_result)
    computation.stack_push_bytes(bytes_result[18:])
    computation.stack_push_bytes(b'\x00' * 14 + bytes_result[:18])
