from modules.kinetic_core.AbstractDB import AbstractDB, table


@table(name="pharmex_seller", key="seller_id")
class SellerDB(AbstractDB):
    pass
