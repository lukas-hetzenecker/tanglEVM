from eth._utils.address import generate_contract_address
from eth.constants import CREATE_CONTRACT_ADDRESS
from eth.typing import BaseOrSpoofTransaction
from eth.vm.forks.petersburg import PetersburgState
from eth.vm.message import Message
from eth.vm.state import BaseTransactionExecutor
#from eth_hash.auto import keccak
#from eth_typing import Address
#from iota import TryteString

#from iota.crypto.kerl import Kerl, conv

from tanglevm.db.account import TanglevmAccountDB
from tanglevm.db.mam import MamDB
from tanglevm.vm.computation import TanglevmComputation
from tanglevm.vm.message import TanglevmMessage
from tanglevm.vm.transaction_context import TanglevmTransactionContext
from eth.vm.forks.spurious_dragon.state import SpuriousDragonTransactionExecutor


# def generate_contract_address(address: Address, nonce: bytes) -> Address:
#     print("generate_contract_address", address, nonce)
#     trits = conv.trytes_to_trits(str(TryteString.from_bytes(rlp.encode([address, nonce]))))
#     kerl = Kerl()
#     kerl.absorb(trits)
#     trits_out = []
#     kerl.squeeze(trits_out)
#     trytes_out = conv.trits_to_trytes(trits_out)
#     print("address is", bytes(trytes_out, 'ascii'))
#     return bytes(trytes_out, 'ascii')

class TanglevmTransactionExecutor(SpuriousDragonTransactionExecutor):
    def build_evm_message(self, transaction: BaseOrSpoofTransaction) -> Message:

        gas_fee = transaction.gas * transaction.gas_price

        # Buy Gas
        self.vm_state.delta_balance(transaction.sender, -1 * gas_fee)

        # Increment Nonce
        self.vm_state.increment_nonce(transaction.sender)

        # Setup VM Message
        message_gas = transaction.gas - transaction.intrinsic_gas

        if transaction.to == CREATE_CONTRACT_ADDRESS:
            contract_address = generate_contract_address(
                transaction.sender,
                self.vm_state.get_nonce(transaction.sender) - 1,
            )
            print("contract address is", contract_address)
            data = b''
            code = transaction.data
        else:
            contract_address = None
            data = transaction.data
            code = self.vm_state.get_code(transaction.to)

        #self.vm_state.logger.trace(
        #    (
        #        "TRANSACTION: sender: %s | to: %s | value: %s | gas: %s | "
        #        "gas-price: %s | s: %s | r: %s | v: %s | data-hash: %s"
        #    ),
        #    encode_hex(transaction.sender),
        #    encode_hex(transaction.to),
        #    transaction.value,
        #    transaction.gas,
        #    transaction.gas_price,
        #    transaction.s,
        #    transaction.r,
        #    transaction.v,
        #    encode_hex(keccak(transaction.data)),
        #)

        message = TanglevmMessage(
            gas=message_gas,
            to=transaction.to,
            sender=transaction.sender,
            value=transaction.value,
            data=data,
            code=code,
            create_address=contract_address,
        )
        return message


class TanglevmState(PetersburgState):
    account_db_class = TanglevmAccountDB
    mam_state_db_class = MamDB  # type: Type[BaseMamDB]
    transaction_executor = TanglevmTransactionExecutor
    transaction_context_class = TanglevmTransactionContext  # type: Type[BaseTransactionContext]
    computation_class = TanglevmComputation

    def validate_transaction(self, transaction: BaseOrSpoofTransaction) -> None:
        return None

    def get_transaction_executor(self) -> 'BaseTransactionExecutor':
        return self.transaction_executor(self)

    def execute_transaction(self, transaction: BaseOrSpoofTransaction) -> BaseTransactionExecutor:
        executor = self.get_transaction_executor()
        return executor(transaction)

    # def set_root(self, address: Address, root: Address) -> None:
    #     self._account_db.set_root(address, root)
    #
    # def set_next_root(self, current_root: Address, next_root: Address, root: Address) -> None:
    #     self._account_db.set_root(next_root, root)
    #     self._account_db.set_prev_root(next_root, current_root)
