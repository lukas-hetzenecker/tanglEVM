from eth._utils.db import apply_state_dict

from typing import Dict

from eth.chains.base import MiningChain
from eth.constants import BLANK_ROOT_HASH
from eth.db import BaseAtomicDB
from eth.estimators import get_gas_estimator
from eth.rlp.headers import HeaderParams, BlockHeader
from eth.typing import AccountState, BlockNumber


from eth.validation import (
    validate_block_number,
    validate_uint256,
    validate_word,
    validate_vm_configuration,
)
from eth.vm.computation import BaseComputation
from eth.vm.state import BaseState  # noqa: F401

from eth._warnings import catch_and_ignore_import_warning

from tanglevm import TanglevmChainDB
from tanglevm.db.header import TanglevmHeaderDB

with catch_and_ignore_import_warning():
    from eth_utils import (
        to_set,
        ValidationError,
    )
    from eth_utils.toolz import (
        assoc,
        compose,
        groupby,
        iterate,
        take,
    )


from tanglevm.rlp.headers import TanglevmBlockHeader


class TanglevmChain(MiningChain):
    chaindb_class = TanglevmChainDB

    def __init__(self, base_db: BaseAtomicDB, header: BlockHeader=None) -> None:
        if not self.vm_configuration:
            raise ValueError(
                "The Chain class cannot be instantiated with an empty `vm_configuration`"
            )
        else:
            validate_vm_configuration(self.vm_configuration)

        self.chaindb = self.get_chaindb_class()(base_db)
        self.headerdb = TanglevmHeaderDB(base_db)
        if self.gas_estimator is None:
            self.gas_estimator = get_gas_estimator()
        self.header = self.ensure_header(header)


    @classmethod
    def from_genesis(cls,
                     base_db: BaseAtomicDB,
                     genesis_params: Dict[str, HeaderParams],
                     genesis_state: AccountState=None) -> 'BaseChain':
        """
        Initializes the Chain from a genesis state.
        """
        genesis_vm_class = cls.get_vm_class_for_block_number(BlockNumber(0))

        account_db = genesis_vm_class.get_state_class().get_account_db_class()(
            base_db,
            BLANK_ROOT_HASH,
        )

        if genesis_state is None:
            genesis_state = {}

        # mutation
        apply_state_dict(account_db, genesis_state)
        account_db.persist()

        if 'state_root' not in genesis_params:
            # If the genesis state_root was not specified, use the value
            # computed from the initialized state database.
            genesis_params = assoc(genesis_params, 'state_root', account_db.state_root)
        elif genesis_params['state_root'] != account_db.state_root:
            # If the genesis state_root was specified, validate that it matches
            # the computed state from the initialized state database.
            raise ValidationError(
                "The provided genesis state root does not match the computed "
                "genesis state root.  Got {0}.  Expected {1}".format(
                    account_db.state_root,
                    genesis_params['state_root'],
                )
            )

        genesis_header = TanglevmBlockHeader(**genesis_params)
        return cls.from_genesis_header(base_db, genesis_header)

    @classmethod
    def from_genesis_header(cls,
                            base_db: BaseAtomicDB,
                            genesis_header: TanglevmBlockHeader) -> 'BaseChain':
        """
        Initializes the chain from the genesis header.
        """
        chaindb = cls.get_chaindb_class()(base_db)
        chaindb.persist_header(genesis_header)
        return cls(base_db)
