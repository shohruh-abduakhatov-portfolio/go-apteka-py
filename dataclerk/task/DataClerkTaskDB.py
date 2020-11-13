from modules.kinetic_core.AbstractDB import AbstractDB, table


@table(name="dataclerk_tasks", key="task_id")
class DataClerkTaskDB(AbstractDB):
    pass
