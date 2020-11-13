#region import
import tornado.web
from web.handlers.BaseHandler import *
#endregion

class OffersHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self):
        self.render("offers/index.html")
