import copy

from eth.vm.opcode import as_opcode
from eth_utils.toolz import (
    merge
)

from eth import (
    constants
)
from eth.vm.forks.petersburg.opcodes import PETERSBURG_OPCODES
from tanglevm.vm import opcode_values, mnemonics
from tanglevm.vm.logic import curl

UPDATED_OPCODES = {
    opcode_values.CURL: as_opcode(
        logic_fn=curl.curl,
        mnemonic=mnemonics.CURL,
        gas_cost=constants.GAS_SHA3,
    ),
}

TANGLEVM_OPCODES = merge(
    copy.deepcopy(PETERSBURG_OPCODES),
    UPDATED_OPCODES,
)
