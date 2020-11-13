from modules.pharmex.utils.exception_handler import *
from pricelists.PriceListClient import PriceListClient
import tornado.web

from modules.kinetic_core.DateTimeEncoder import DateTimeEncoderCompact
import asyncio
from web.handlers.BaseHandler import *
from modules.pharmex.basket.BasketExecutorClient_ph import BasketExecutorClient_ph
import json
import pandas as pd
import datetime
from modules.kinetic_core.Connector import db
import math


class ProcurementBasketMIVSResponseHandler(BaseHandler):

    @throws_handler()
    @allowedRole(Role.PHARMA_CLIENT)
    async def post(self):

        # MOCK
        #product_ids = [8119, 9034, 5837]
        # MOCK
        #provisions_products_quantities = {8119: 1, 9034: 1, 5837: 3}


        params = json.loads(self.get_argument('values'))

        matrix_supplier_ids = params.get('matrix_supplier_ids', None)

        provision_ids = params.get('ids', None)
        selected_supplier_ids = params.get('supplier_ids', None)
        urgent_procurement = int(params.get("urgent_procurement", 0))
        pharmacy = int(params.get("pharmacy", 0))

        procurement_type = params.get("procurement_type", 'standard')
        price_type = params.get("price_type", 'wire100')


        provisions = await db.list(
            "select provision_id, product_id, quantity, cost, total_cost, current_timestamp from ph_provision where provision_id = any($1::int[])",
            (provision_ids,))
        print(provisions)

        mivs_provisions = {int(p_id): 1 for p_id in provision_ids}

        user_id = self.get_current_user()["user_id"]


        basket_executor = BasketExecutorClient_ph()

        print('calling mivs')

        mivs_result = await basket_executor.calc_by_mivs(data={"provisions": mivs_provisions,
                                                               "procurement_type": procurement_type,
                                                               "price_type": price_type,
                                                               "matrix_supplier_ids": matrix_supplier_ids,
                                                               "user_id": user_id})

        #if mivs_result["status"] == "OPTIMAL":
        #    mivs_result = mivs_result[""]

        print('mivs request complete')
        l = list()

        # MOCK
        """
        mivs_result = {'351': {
                            'prices': {'wire100': {'8119': 1, '9034': 1},
                                       'wire50': {},
                                       'wire25': {},
                                       'cash_cost': {}
                                       },
                            'total_price': 154571, 'cash_price': 0, 'prepayment_price': 12345, 'discount': 0},

                       '117': {
                            'prices': {'wire100': {},
                                       'wire50': {'5837': 3},
                                       'wire25': {},
                                       'cash_cost': {}
                                       },
                            'total_price': 100500, 'cash_price': 0, 'prepayment_price': 14253, 'discount': 0},

                        'status': 'OPTIMAL', 'status_code': 4}
        """
        data = {}

        if mivs_result != None:

            data["status"] = mivs_result["status"]

            if mivs_result["status"] == 'OPTIMAL':

                data["message"] = 'OK'

                mivs_filtered = {k: v for k, v in mivs_result.items() if not k.startswith('status')}

                mivs_sup_ids = [int(m) for m in mivs_filtered]
                basket = await basket_executor.get_by_user_id(data={"user_id": user_id})

                from modules.pharmex.procurement.ProcurementExecutorClient_ph import ProcurementExecutorClient_ph
                procurement_client = ProcurementExecutorClient_ph()
                procurements = []
                for procurement_id in list(basket["procurements"].values()):
                    procurement = await procurement_client.get_one(data={"procurement_id": procurement_id})
                    procurements.append(procurement)

                suppliers = await db.list(
                    "select company_name, pharmex_supplier_id, min_sum, pharmacy, urgent_procurement, current_timestamp from supplier where pharmex_supplier_id = any($1::int[])",
                    (mivs_sup_ids,))
                row_suppliers = {supplier["pharmex_supplier_id"]: supplier["company_name"] for supplier in suppliers}

                product_ids = [provision["product_id"] for provision in provisions]
                #print("p ids: ", product_ids)

                products = await db.list(
                    "select product_id, name, current_timestamp from products where product_id = any($1::int[])",
                    (product_ids,))

                row_products = {p["product_id"]: p["name"] for p in products}

                keys_localized = {"prices": "Товары", "wire100": "Перечислением 100%", "wire50": "Перечислением 50%", "wire25": "Перечислением 25%",
                                  "cash_cost": "Наличными", "total_price": "Общая сумма", "cash_price": "Сумма наличными",
                                  "prepayment_price": "Сумма предоплаты", "discount": "Скидка"}

                #print("products: ", products)

                data["mivs_result"] = mivs_filtered
                data["suppliers"] = row_suppliers
                data["products"] = row_products
                data["keys_localized"] = keys_localized

            else:
                data["status"] = "ERROR"
                data["message"] = mivs_result["message"]

        else:
            data["status"] = "ERROR"
            data["message"] = "Во время вычислений произошла ошибка. Пожалуйста, попробуйте позже."

        self.write(data)
        self.finish()
