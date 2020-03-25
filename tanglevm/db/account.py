import logging


from eth.tools.logging import ExtendedDebugLogger

from eth.db.account import AccountDB
from tanglevm.rlp.accounts import Account
from typing import cast, Set, Tuple  # noqa: F401

from eth_typing import (
    Address,
    Hash32
)

import rlp

from eth_utils import (
    encode_hex,
)

#from tanglevm.validation import validate_canonical_address


class TanglevmAccountDB(AccountDB):

    logger = cast(ExtendedDebugLogger, logging.getLogger('tanglevm.db.TanglevmAccountDB'))

    # #
    # # Root
    # #
    # def get_root(self, address: Address) -> int:
    #     validate_canonical_address(address, title="Storage Address")
    #
    #     account = self._get_account(address)
    #     return account.root
    #
    # def set_root(self, address: Address, root: Address) -> None:
    #     validate_canonical_address(address, title="Storage Address")
    #     validate_canonical_address(root, title="Root Address")
    #
    #     account = self._get_account(address)
    #     self._set_account(address, account.copy(root=root))
    #
    # #
    # # Previous Root
    # #
    # def get_prev_root(self, address: Address) -> int:
    #     validate_canonical_address(address, title="Storage Address")
    #
    #     account = self._get_account(address)
    #     return account.prev_root
    #
    # def set_prev_root(self, address: Address, prev_root: Address) -> None:
    #     validate_canonical_address(address, title="Storage Address")
    #     validate_canonical_address(prev_root, title="Previous Root Address")
    #
    #     account = self._get_account(address)
    #     self._set_account(address, account.copy(prev_root=prev_root))

    #
    # Internal
    #
    def _get_account(self, address: Address, from_journal: bool=True) -> Account:
        if from_journal and address in self._account_cache:
            return self._account_cache[address]

        rlp_account = self._get_encoded_account(address, from_journal)
        if rlp_account:
            account = rlp.decode(rlp_account, sedes=Account)
        else:
            account = Account()


        if from_journal:
            self._account_cache[address] = account
        return account

    def _set_account(self, address: Address, account: Account) -> None:
        self._account_cache[address] = account
        rlp_account = rlp.encode(account, sedes=Account)
        self._journaltrie[address] = rlp_account

