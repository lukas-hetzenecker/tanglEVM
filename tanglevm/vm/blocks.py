from eth.vm.forks.petersburg import PetersburgBlock
from rlp.sedes import CountableList

from tanglevm.rlp.headers import TanglevmBlockHeader
from tanglevm.vm.transactions import TanglevmTransaction


class TanglevmBlock(PetersburgBlock):
    transaction_class = TanglevmTransaction
    fields = [
        ('header', TanglevmBlockHeader),
        ('transactions', CountableList(transaction_class)),
        ('uncles', CountableList(TanglevmBlockHeader))
    ]

