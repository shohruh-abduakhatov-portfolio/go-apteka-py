#region import
import tornado.web
from web.handlers.BaseHandler import *
#endregion

class AutoCompleteTextHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self):
        self.render("product/autocomplete.html")
