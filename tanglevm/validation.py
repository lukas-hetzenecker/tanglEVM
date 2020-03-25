from eth_utils import ValidationError
from eth_typing import Address

from iota.types import Address as IotaAddress


def validate_iota_canonical_address(value: Address, title: str="Value") -> None:
    if not isinstance(value, bytes) or not len(value) == IotaAddress.LEN:
        raise ValidationError(
            "{title} {0} is not a valid canonical address".format(value, title=title)
        )
