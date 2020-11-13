from modules.kinetic_core.AbstractDB import AbstractDB, table


@table(name="pharmex_pricelist_revision", key="key", primary=False)
class PriceListRevisionDB(AbstractDB):
    pass
