from eth.db.schema import BaseSchema


class TanglevmSchema(BaseSchema):
    @staticmethod
    def make_mam_state(address) -> bytes:
        return b'si:mam:%s' % address

