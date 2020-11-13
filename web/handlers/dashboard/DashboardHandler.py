#region import
import tornado.web
from web.handlers.BaseHandler import *
#endregion

class DashboardHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self):
        self.render("dashboard/index.html")
