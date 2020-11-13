# region import
import os  # NOQA: E402
import sys  # NOQA: E402

import uvloop  # NOQA: E402


uvloop.install()  # NOQA: E402
os.environ['VITA_CONFIG'] = '/var/www/config.py'  # NOQA: E402

# Add the ptdraft folder path to the sys.path list
sys.path.append(os.path.abspath(__file__ + "/../../"))  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../../modules/business"))  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../../modules/pharmex"))  # NOQA: E402

from modules.kinetic_core.AbstractExecutor import executor
from modules.kinetic_core.QueueListener import QueueListener
from modules.kinetic_core.UpdateExecutor import UpdateExecutor

from modules.business.profiles.auth.SMSVerificationClient import SMSVerificationClient

from web.handlers.procurement.ProcurementBasketHandler import ProcurementBasketHandler
from web.handlers.procurement.ProcurementHandler import ProcurementHandler
from web.handlers.procurement.ProcurementSearchHandler import ProcurementSearchHandler
from web.handlers.auth.SMSCodeRequestHandler import SMSCodeRequestHandler

from web.handlers.utils.WebhookHandler import WebhookHandler

from web.handlers.product.AutoCompleteQueryHandler import AutoCompleteQueryHandler
from web.handlers.product.AutoCompleteTextHandler import AutoCompleteTextHandler
from web.handlers.product.ProductAutoCompleteQueryHandler import ProductAutoCompleteQueryHandler
from web.handlers.offers.OffersHandler import OffersHandler
from web.handlers.dashboard.DashboardHandler import DashboardHandler
from web.handlers.prices.PriceViewHandler import PriceViewHandler
from web.handlers.prices.PricesListJSONHandler import PricesListJSONHandler
from web.handlers.product.ProductFilteredListJSONHandler import ProductFilteredListJSONHandler
from web.handlers.product.ProductTasksHandler import ProductTasksHandler
from web.handlers.product.ProductTasksViewBySupplierHandler import ProductTasksViewBySupplierHandler
from web.handlers.product.ProductFilteringHandler import ProductFilteringHandler
from web.handlers.product.ProductsDublicatesFindHandler import ProductsDublicatesFindHandler
from web.handlers.product.ProductsHandler import ProductsHandler
from web.handlers.BaseHandler import BaseHandler
from web.handlers.product.ProductViewHandler import ProductViewHandler
from web.handlers.product.ProductListJSONHandler import ProductListJSONHandler
from web.handlers.export.SuggestProductNameHandler import SuggestProductNameHandler
from web.handlers.product.title.ProductSynonymLoadHandler import ProductSynonymLoadHandler

from web.handlers.procurement.ProcurementBasketMatrixJSONHandler import ProcurementBasketMatrixJSONHandler
from web.handlers.procurement.ProcurementBasketAddItemHandler import ProcurementBasketAddItemHandler
from web.handlers.procurement.ProcurementBasketModifyProvisionQuantityHandler import \
    ProcurementBasketModifyProvisionQuantityHandler
from web.handlers.procurement.ProcurementBasketRemoveItemHandler import ProcurementBasketRemoveItemHandler
from web.handlers.procurement.ProcurementBasketMIVSResponseHandler import ProcurementBasketMIVSResponseHandler
from web.handlers.procurement.ProcurementBasketMIVSResponseHandler_test import ProcurementBasketMIVSResponseHandler_test
from web.handlers.procurement.CartContentsLoaderJSONHandler import CartContentsLoaderJSONHandler
from web.handlers.procurement.ProcurementBasketClearHandler import ProcurementBasketClearHandler

from web.handlers.procurement.SuppliersPreferenceJSONHandler import SuppliersPreferenceJSONHandler
from web.handlers.procurement.SaveSupplierPreferenceHandler import SaveSupplierPreferenceHandler

from web.handlers.prices.MinimalSupplierCostHandler import MinimalSupplierCostHandler

from modules.kinetic_core import Logger
from web import ui_methods
import tornado.httpclient
import tornado.platform.asyncio
import tornado.web
import tornado.locks
import tornado.ioloop
import tornado.concurrent
import logging
import json
import asyncio


# from modules.kinetic_core.util.TracePrints import *
# endregion

loop = asyncio.get_event_loop()

# Инициируем логгирование
Logger.init(logging.DEBUG)


class LoginHandler(BaseHandler):

    async def get(self):
        self.render("auth/login_m.html")


    @asyncio.coroutine
    async def post(self):
        from authorization.CpUserDB import CpUserDB
        db = CpUserDB()

        phone = self.get_argument('phone-number', default=None)
        code = self.get_argument('code', default=None)

        if phone != None:
            phone = '998' + phone

        sms_client = SMSVerificationClient()
        verify = await sms_client.verify(phone=phone, code=code, device_id='')

        from modules.pharmex.agent_users.AgentUserExecutorClient_ph import AgentUserExecutorClient_ph
        agent_ex_client = AgentUserExecutorClient_ph()
        has = await agent_ex_client.get_by_phone(data={"phone": phone})

        if has != None:
            has = {"user_id": has["user_id"], "agent_id": has["agent_id"], "role_id": has["role_id"],
                   "first_name": has["first_name"], "last_name": has["last_name"]}

        if verify and has:
            result = {"status": "success", "data": has}
        else:
            result = None
        if result["status"] == "success":
            self.set_current_user(user=result["data"], remember_me=True)
            self.redirect("/")
            self.finish()
        else:
            self.write(json.dumps(result))


class LogoutHandler(BaseHandler):
    @asyncio.coroutine
    async def get(self):
        self.clear_cookie(self.settings["cookie_user_session"])
        self.redirect("/login")
        self.finish()


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/sms", SMSCodeRequestHandler),
            (r"/autocomplete/", AutoCompleteTextHandler),
            (r"/autocomplete/query/", AutoCompleteQueryHandler),
            (r"/product/autocomplete/query/", ProductAutoCompleteQueryHandler),
            (r"/", ProcurementSearchHandler),
            (r"/offers/", OffersHandler),  # прозвон

            # Procurement
            # (r"/procurement/", ProcurementHandler),
            # (r"/procurement/search", ProcurementSearchHandler),
            (r"/procurement/basket", ProcurementBasketHandler),
            (r"/procurement/basket/sp_matrix/data.json", ProcurementBasketMatrixJSONHandler),
            (r"/procurement/basket/modify_quantity", ProcurementBasketModifyProvisionQuantityHandler),
            (r"/procurement/basket/add_item", ProcurementBasketAddItemHandler),
            (r"/procurement/basket/remove_item", ProcurementBasketRemoveItemHandler),
            (r"/procurement/basket/call_mivs", ProcurementBasketMIVSResponseHandler),
            (r"/procurement/basket/call_mivs_test", ProcurementBasketMIVSResponseHandler_test),

            (r"/procurement/basket/clear_basket", ProcurementBasketClearHandler),

            (r"/procurement/basket/suppliers/data.json", SuppliersPreferenceJSONHandler),
            (r"/procurement/basket/save_suppliers", SaveSupplierPreferenceHandler),
            (r"/procurement/cart_items/data.json", CartContentsLoaderJSONHandler),

            # Products
            (r"/products/", ProductsHandler),

            (r"/products/find-dublicates/", ProductsDublicatesFindHandler),
            (r"/products/filtering/", ProductFilteringHandler),
            (r"/products/tasks/", ProductTasksHandler),  # --------
            (r"/products/tasks/(?P<supplier_id>[^\/]+)/view/", ProductTasksViewBySupplierHandler),  # --------
            (r"/products/(?P<product_id>[^\/]+)/view/", ProductViewHandler),
            (r"/products/data.json", ProductListJSONHandler),
            (r"/products/filter/data.json", ProductFilteredListJSONHandler),

            # Pricelist
            (r"/prices/data.json", PricesListJSONHandler),
            (r"/prices/(?P<price_list_id>[^\/]+)/view/", PriceViewHandler),

            (r"/edit_min_cost", MinimalSupplierCostHandler),

            # Products
            (r"/product/suggest/(.*)", SuggestProductNameHandler),
            (r"/products/(?P<product_id>[^\/]+)/synonym/", ProductSynonymLoadHandler),

            (r"/webhook", WebhookHandler),
        ]
        settings = dict(
            blog_title=u"Pharmex Client",
            # template_whitespace="oneline",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            ui_methods=ui_methods,
            cookie_user_session="user",
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            login_url="/login",
            debug=False,
        )
        super(Application, self).__init__(handlers, **settings)


def make_server(app, io_loop=None):
    server = tornado.httpserver.HTTPServer(
        app, decompress_request=True)
    return server


async def main():
    app = Application()
    server = make_server(app)
    print("started at: 8899")
    server.bind(8899)
    server.start()
    shutdown_event = tornado.locks.Event()
    await shutdown_event.wait()


if __name__ == "__main__":
    print("run sync")
    tornado.ioloop.IOLoop.current().run_sync(main)
print(__name__)
