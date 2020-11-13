#region import
import tornado.web
from web.handlers.BaseHandler import *
from modules.pharmex.utils.exception_handler import *
#endregion


class ProcurementHandler(BaseHandler):

    @throws_handler()
    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self):
        self.render("procurement/index.html")
