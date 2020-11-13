import tornado.web

from web.handlers.BaseHandler import *
from modules.pharmex.utils.exception_handler import *
from modules.pharmex.basket.BasketExecutorClient_ph import BasketExecutorClient_ph


class ProcurementBasketClearHandler(BaseHandler):

    @throws_handler()
    @allowedRole(Role.PHARMA_CLIENT)
    async def post(self):

        basket_client = BasketExecutorClient_ph()

        current_user = self.get_current_user()
        user_id = current_user["user_id"]
        basket = await basket_client.get_by_user_id(data={"user_id": user_id})
        basket_id = int(basket["basket_id"])

        await basket_client.clear_basket(data={"basket_id": basket_id})

        response = {"status": "success", "message": 'Корзина очищена'}

        self.write(response)
        self.finish()
