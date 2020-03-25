from rlp.sedes import Binary

iota_address = Binary.fixed_length(81, allow_empty=True)