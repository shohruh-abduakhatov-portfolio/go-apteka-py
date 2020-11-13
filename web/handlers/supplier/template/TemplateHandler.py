#region import
import json
import tornado.web
from web.handlers.BaseHandler import *
from suppliers.SuppliersExportTemplateClient import SuppliersExportTemplateClient
#endregion

class TemplateHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self, key=None):
        data = None
        client = SuppliersExportTemplateClient()
        template = await client.get_one()
        self.write(json.dumps({"template": template},
                              ignore_nan=True,
                              ensure_ascii=False,
                              separators=(',', ':')))
        self.finish()
