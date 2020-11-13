#region import
import tornado.web
from web.handlers.BaseHandler import *
from modules.kinetic_core.Connector import db
#endregion

class ProductsDublicatesFindHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self):
        dublicates = await db.list(
                    'select * from products ou where (select count(*) from products inr where inr.name = ou.name) > 1 order by name desc' 
                )
        self.render("product/dublicates.html", dublicates=dublicates)
