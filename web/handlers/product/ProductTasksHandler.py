# region import
import tornado.web
import json
from web.handlers.BaseHandler import *
from dataclerk.NewProductTaskClient import NewProductTaskClient
from operations.TitleExecutorClient import TitleExecutorClient
from warehouse.ProductsExecutorClient import ProductsExecutorClient
# endregion


class ProductTasksHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self):
        new_product_task = NewProductTaskClient()
        offset = int(self.get_argument("o", default=0))
        supplier_tasks = await new_product_task.group_tasks()

        self.render("product/task_list.html",
                    waiting_upload_count=1, supplier_tasks=supplier_tasks)
