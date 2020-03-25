import itertools
from eth.validation import validate_uint256, validate_canonical_address
from eth.vm.transaction_context import BaseTransactionContext
from eth_typing import Address

#from tanglevm.validation import validate_canonical_address

class TanglevmTransactionContext(BaseTransactionContext):
    def __init__(self, gas_price: int, origin: Address) -> None:
        validate_uint256(gas_price, title="TransactionContext.gas_price")
        self._gas_price = gas_price
        validate_canonical_address(origin, title="TransactionContext.origin")
        self._origin = origin
        self._log_counter = itertools.count()
