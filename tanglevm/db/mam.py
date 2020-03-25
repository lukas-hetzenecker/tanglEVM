import logging
from abc import (
    ABC,
    abstractmethod
)
from typing import cast

from eth.tools.logging import ExtendedDebugLogger
from eth_typing import (
    Address,
    Hash32
)
from eth.db.backends.base import (
    BaseDB,
    BaseAtomicDB,
)

import rlp

from tanglevm.db.schema import TanglevmSchema
from tanglevm.rlp.mam import MamState
from tanglevm.validation import validate_iota_canonical_address


class BaseMamDB(ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError(
            "Must be implemented by subclasses"
        )

    #
    # Root
    #
    @abstractmethod
    def get_root(self, address: Address) -> int:
        raise NotImplementedError(
            "Must be implemented by subclasses"
        )

    @abstractmethod
    def set_root(self, address: Address, root: Address) -> None:
        raise NotImplementedError(
            "Must be implemented by subclasses"
        )

    #
    # Previous Root
    #
    @abstractmethod
    def get_prev_root(self, address: Address) -> int:
        raise NotImplementedError(
            "Must be implemented by subclasses"
        )

    @abstractmethod
    def set_prev_root(self, address: Address, prev_root: Address) -> None:
        raise NotImplementedError(
            "Must be implemented by subclasses"
        )


class MamDB(BaseMamDB):

    logger = cast(ExtendedDebugLogger, logging.getLogger('eth.db.account.AccountDB'))

    def __init__(self, db: BaseAtomicDB) -> None:
        self._db = db

    #
    # Root
    #
    def get_root(self, address: Address) -> int:
        validate_iota_canonical_address(address, title="Address")

        mam_state = self._get_mam_state(address)
        return mam_state.root

    def set_root(self, address: Address, root: Address) -> None:
        validate_iota_canonical_address(address, title="Address")
        validate_iota_canonical_address(root, title="Root Address")

        mam_state = self._get_mam_state(address)
        mam_state = mam_state.copy(root=root)
        self._set_mam_state(address, mam_state)

    #
    # Previous Root
    #
    def get_prev_root(self, address: Address) -> int:
        validate_iota_canonical_address(address, title="Address")

        mam_state = self._get_mam_state(address)
        return mam_state.prev_root

    def set_prev_root(self, address: Address, prev_root: Address) -> None:
        validate_iota_canonical_address(address, title="Address")
        validate_iota_canonical_address(prev_root, title="Prev Root Address")

        mam_state = self._get_mam_state(address)
        mam_state = mam_state.copy(prev_root=prev_root)
        self._set_mam_state(address, mam_state)

    #
    # Internal
    #
    def _get_mam_state(self, address):
        mam_state = self._db.get(TanglevmSchema.make_mam_state(address))
        if mam_state:
            mam_state = rlp.decode(mam_state, MamState)
        else:
            mam_state = MamState()

        return mam_state

    def _set_mam_state(self, address, mam_state):
        rlp_mam_state = rlp.encode(mam_state, sedes=MamState)
        self._db[TanglevmSchema.make_mam_state(address)] = rlp_mam_state
