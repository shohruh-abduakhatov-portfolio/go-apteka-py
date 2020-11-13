#region import
import tornado.web
from web.handlers.BaseHandler import *
from modules.kinetic_core.Connector import db
#endregion

class ProductFilteringHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self):
        self.render("product/filtering.html")

    @allowedRole(Role.PHARMA_CLIENT)
    async def post(self):
        column = self.get_argument("column", "")
        if column in ["description", "category", "manufacturer", "manufacturer_country", "manufacturer_id"]:
            products = await db.list('select * from products where ' + column + ' is null')
            self.write({"data": products})
            self.finish()
        else:
            self.clear()
            self.set_status(400)
            self.finish("<html><body>Invalid input</body></html>")

