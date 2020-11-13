#region import
import tornado.web
from web.handlers.BaseHandler import *
from modules.business.warehouse.ProductsExecutorClient import ProductsExecutorClient
from suppliers.aliases.AgentProductAliasesClient import AgentProductAliasesClient
#endregion

class ProductViewHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self, product_id):
        product_id = int(product_id)
        product_client = ProductsExecutorClient()
        product = await product_client.get_one(product_id=product_id)

        alias_client = AgentProductAliasesClient()
        aliases = await alias_client.list_by_product_id(product_id=product_id)
        self.render(
            "product/view.html", 
            product=product,
            aliases=aliases)
