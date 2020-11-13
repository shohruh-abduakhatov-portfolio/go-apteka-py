# region import
import tornado.web
import json
from web.handlers.BaseHandler import *
from dataclerk.NewProductTaskClient import NewProductTaskClient
from operations.TitleExecutorClient import TitleExecutorClient
from warehouse.ProductsExecutorClient import ProductsExecutorClient
# endregion


class ProductTasksViewBySupplierHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self, supplier_id):
        supplier_id = int(supplier_id)
        new_product_task = NewProductTaskClient()
        offset = int(self.get_argument("o", default=0))
        uncompleted = await new_product_task.get_uncompleted(offset=offset, supplier_id=supplier_id)
        to_analyze = []
        for incomplete in uncompleted:
            to_analyze.append(
                {"title": incomplete["name"],
                 "manufacturer": incomplete["manufacturer"],
                 "get_alternatives": 1})

        titex = TitleExecutorClient()
        p = await titex.find_match_many(data=to_analyze)
        product_client = ProductsExecutorClient()
        for u in p:
            if u["result"]["type"] == "ambiguous":
                for product_id, alt in u["result"]["alternatives"].items():
                    if type(alt["marker2"]) is str:
                        alt["marker2"] = json.loads(alt["marker2"])
                    alt["product"] = await product_client.get_one(product_id=product_id)

            if u["result"]["type"] == "ok":
                main_product_id = u["result"]["result"]["product_id"]
                alternatives = {}
                selected = {}
                selected_product_id = None
                for product_id, alt in u["result"]["alternatives"].items():
                    if str(product_id) == str(main_product_id):

                        if type(alt["marker2"]) is str:
                            alt["marker2"] = json.loads(alt["marker2"])
                        alt["product"] = await product_client.get_one(product_id=product_id)
                        selected = alt
                        selected_product_id = product_id
                        break
                alternatives[selected_product_id] = selected

                for product_id, alt in u["result"]["alternatives"].items():
                    if type(alt["marker2"]) is str:
                        alt["marker2"] = json.loads(alt["marker2"])
                    alt["product"] = await product_client.get_one(product_id=product_id)
                    if str(product_id) != str(main_product_id):
                        alternatives[product_id] = alt

                u["result"]["alternatives"] = alternatives

        self.render("product/task.html",
                    waiting_upload_count=len(uncompleted), uncompleted=p, offset=offset + 50, supplier_id=supplier_id)
