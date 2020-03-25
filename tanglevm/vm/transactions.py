import rlp
from eth.rlp.sedes import address

from eth.rlp.transactions import BaseTransaction, BaseUnsignedTransaction
from eth_typing import Address
from rlp.sedes import big_endian_int
from rlp.sedes import binary

from eth.vm.forks.frontier.transactions import _get_frontier_intrinsic_gas

#from tanglevm.rlp.sedes import address


class TanglevmTransaction(BaseTransaction):
    fields = [
        ('nonce', big_endian_int),
        ('gas_price', big_endian_int),
        ('gas', big_endian_int),
        ('to', address),
        ('sender', address),
        #('root', address),
        #('next_root', address),
        ('value', big_endian_int),
        ('data', binary),
        ('v', big_endian_int),
        ('r', big_endian_int),
        ('s', big_endian_int),
    ]

    def validate(self) -> None:
        return True
        super().validate()

    def check_signature_validity(self) -> None:
        return

    def get_sender(self) -> Address:
        return self.sender

    #def get_root(self) -> Address:
    #    return self.root

    #def get_next_root(self) -> Address:
    #    return self.next_root

    def get_message_for_signing(self) -> bytes:
        return rlp.encode(TanglevmUnsignedTransaction(
            nonce=self.nonce,
            gas_price=self.gas_price,
            gas=self.gas,
            to=self.to,
            value=self.value,
            data=self.data,
        ))

    @classmethod
    def create_unsigned_transaction(cls,
                                    *,
                                    nonce: int,
                                    gas_price: int,
                                    gas: int,
                                    to: Address,
                                    value: int,
                                    data: bytes) -> 'TanglevmTransaction':
        return TanglevmUnsignedTransaction(nonce, gas_price, gas, to, value, data)

    def get_intrinsic_gas(self) -> int:
        return _get_frontier_intrinsic_gas(self.data)


class TanglevmUnsignedTransaction(BaseUnsignedTransaction):

    def validate(self) -> None:
        super().validate()

    #def as_signed_transaction(self, sender, root, next_root) -> TanglevmTransaction:
    def as_signed_transaction(self, sender) -> TanglevmTransaction:
        return TanglevmTransaction(
            nonce=self.nonce,
            gas_price=self.gas_price,
            gas=self.gas,
            sender=sender,
            #root=root,
            #next_root=next_root,
            to=self.to,
            value=self.value,
            data=self.data,
            v=0,
            r=0,
            s=0
        )

    def get_intrinsic_gas(self) -> int:
        return _get_frontier_intrinsic_gas(self.data)
