from eth.vm.forks.petersburg.computation import PETERSBURG_PRECOMPILES, PetersburgComputation
from .opcodes import TANGLEVM_OPCODES

TANGLEVM_PRECOMPILES = PETERSBURG_PRECOMPILES


class TanglevmComputation(PetersburgComputation):
    """
    A class for all execution computations in the ``Constantinople`` fork.
    Inherits from :class:`~eth.vm.forks.byzantium.computation.ByzantiumComputation`
    """
    # Override
    opcodes = TANGLEVM_OPCODES
    _precompiles = TANGLEVM_PRECOMPILES
