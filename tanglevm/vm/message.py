from eth.constants import CREATE_CONTRACT_ADDRESS
from eth.validation import validate_uint256, validate_gte, validate_is_integer, \
    validate_is_bytes, validate_is_boolean, validate_canonical_address
from eth.vm.message import Message
from eth_typing import Address

#from tanglevm.validation import validate_canonical_address

class TanglevmMessage(Message):
    def __init__(self,
                 gas: int,
                 to: Address,
                 sender: Address,
                 value: int,
                 data: bytes,
                 code: bytes,
                 depth: int=0,
                 create_address: Address=None,
                 code_address: Address=None,
                 should_transfer_value: bool=True,
                 is_static: bool=False) -> None:
        validate_uint256(gas, title="Message.gas")
        self.gas = gas  # type: int

        if to != CREATE_CONTRACT_ADDRESS:
            validate_canonical_address(to, title="Message.to")
        self.to = to

        validate_canonical_address(sender, title="Message.sender")
        self.sender = sender

        validate_uint256(value, title="Message.value")
        self.value = value

        validate_is_bytes(data, title="Message.data")
        self.data = data

        validate_is_integer(depth, title="Message.depth")
        validate_gte(depth, minimum=0, title="Message.depth")
        self.depth = depth

        validate_is_bytes(code, title="Message.code")
        self.code = code

        if create_address is not None:
            validate_canonical_address(create_address, title="Message.storage_address")
        self.storage_address = create_address

        if code_address is not None:
            validate_canonical_address(code_address, title="Message.code_address")
        self.code_address = code_address

        validate_is_boolean(should_transfer_value, title="Message.should_transfer_value")
        self.should_transfer_value = should_transfer_value

        validate_is_boolean(is_static, title="Message.is_static")
        self.is_static = is_static
