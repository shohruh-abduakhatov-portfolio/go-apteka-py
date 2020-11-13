#region import
import tornado.web
from web.handlers.BaseHandler import *
#endregion

class ProductsHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self):
        self.render("product/index.html", waiting_upload_count=1)
