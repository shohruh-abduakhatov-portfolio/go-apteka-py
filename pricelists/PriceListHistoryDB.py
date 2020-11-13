from modules.kinetic_core.AbstractDB import AbstractDB, table


@table(name="pharmex_pricelists_history", key="history_id")
class PriceListHistoryDB(AbstractDB):
    pass
