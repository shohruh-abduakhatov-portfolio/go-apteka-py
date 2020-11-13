#region import
import requests
import tornado.web
from modules.pharmex.basket.BasketExecutorClient_ph import BasketExecutorClient_ph
from modules.pharmex.procurement.ProcurementExecutorClient_ph import ProcurementExecutorClient_ph
from modules.pharmex.provision.ProvisionExecutorClient_ph import ProvisionExecutorClient_ph
from modules.pharmex.utils.exception_handler import *
from web.handlers.BaseHandler import *
from modules.pharmex.agent_users.AgentUserExecutorClient_ph import AgentUserExecutorClient_ph
from modules.kinetic_core.Connector import db
import json
#endregion

class ProcurementBasketHandler(BaseHandler):

    @throws_handler()
    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self):
        # if validate_recapture(self.get_argument("g-recaptcha-response", default=None)): return "You are robot!"
        basket_executor_client = BasketExecutorClient_ph()
        agent_user_ex = AgentUserExecutorClient_ph()

        current_user = self.get_current_user()
        user_id = current_user["user_id"]
        agent_id = current_user["agent_id"]

        agent_user = await agent_user_ex.get_one(data={"user_id": user_id})
        basket = await basket_executor_client.get_by_user_id(data={"user_id": user_id})

        # await basket_executor_client.clear_basket(data={'basket_id': 15})

        if "inclusive_suppliers" in agent_user:
            preferred_suppliers = [int(i) for i in agent_user["inclusive_suppliers"]]
        else:
            preferred_suppliers = []

        selected_for_matrix = []

        for prov_id, i in basket["provision_ids"].items():
            selected_for_matrix.append(int(prov_id))

        procurement_client = ProcurementExecutorClient_ph()
        procurements = []
        for procurement_id in basket["procurement_ids"]:
            p = await procurement_client.get_one(data={"procurement_id": procurement_id})
            procurements.append(p)

        provision_client = ProvisionExecutorClient_ph()

        procurement_plan = {}

        product_ids = []
        provision_ids = []

        if len(procurements) > 0:
            for procurement in procurements:

                entity_details ={}

                priced_entry = {}

                for prov_id in list(procurement["provisions"].keys()):

                    provision = await provision_client.get_one(data={"provision_id": prov_id})
                    product_id = provision["product_id"]
                    quantity = provision["quantity"]

                    provision_ids.append(prov_id)
                    product_ids.append(product_id)

                    priced_entry[product_id] = quantity

                    entity_details["prices"] = {str(procurement["price_type"]): priced_entry}

                    # TODO: CHANGE IN FUTURE TO ACTUAL TOTAL COST ( IT CAN VARY DUE TO PAYMENT TYPE )
                    entity_details["total_price"] = procurement["prepayment_cost"]
                    entity_details["prepayment_price"] = procurement["prepayment_cost"]

                supplier_id = procurement["supplier_id"]
                procurement_plan[str(supplier_id)] = entity_details

        data = {}

        proc_sup_keys = list(procurement_plan.keys())
        proc_sup_ids = [int(i) for i in proc_sup_keys]


        suppliers = await db.list(
            "select company_name, pharmex_supplier_id, min_sum, pharmacy, urgent_procurement, current_timestamp from supplier where pharmex_supplier_id = any($1::int[]) and pharmacy=0",
            (proc_sup_ids ,))
        row_suppliers = {supplier["pharmex_supplier_id"]: supplier["company_name"] for supplier in suppliers}

        #print("p ids: ", product_ids)

        products = await db.list(
            "select product_id, name, current_timestamp from products where product_id = any($1::int[])",
            (product_ids,))

        row_products = {p["product_id"]: p["name"] for p in products}

        keys_localized = {"prices": "Товары", "wire100": "Перечислением 100%", "wire50": "Перечислением 50%",
                          "wire25": "Перечислением 25%",
                          "cash_cost": "Наличными", "total_price": "Общая сумма", "cash_price": "Сумма наличными",
                          "prepayment_price": "Сумма предоплаты", "discount": "Скидка"}

        data["mivs_result"] = procurement_plan
        data["suppliers"] = row_suppliers
        data["products"] = row_products
        data["keys_localized"] = keys_localized
        data["provision_ids"] = provision_ids

        data["status"] = "OK"
        data["message"] = "OK"

        self.render("procurement/basket.html", selected_for_matrix=selected_for_matrix, basket=basket,
                    agent_id=agent_id, preferred_suppliers=preferred_suppliers, procurement_plan=json.dumps(data))


def validate_recapture(recaptcha_response):
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': "6LfgoLMUAAAAAGbpl0B-5xmvsXceiuHdLpXu2Zai",
        'response': recaptcha_response
    }
    verify_rs = requests.get(url, params=values, verify=True)
    verify_rs = verify_rs.json()
    status = verify_rs.get("success", False)
    return status
