from modules.kinetic_core.AbstractDB import AbstractDB, table


@table(name="suppliers_export_template", key="template_id")
class SuppliersExportTemplateDB(AbstractDB):
    pass
