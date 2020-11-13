from pricelists.PriceListClient import PriceListClient
import tornado.web

from modules.kinetic_core.DateTimeEncoder import DateTimeEncoderCompact
import asyncio
from web.handlers.BaseHandler import *
from modules.pharmex.utils.exception_handler import *
from pricelists.PriceListClient import PriceListClient
from modules.pharmex.agent_users.AgentUserExecutorClient_ph import AgentUserExecutorClient_ph
from modules.pharmex.basket.BasketExecutorClient_ph import BasketExecutorClient_ph
import json
import pandas as pd
import datetime
from modules.kinetic_core.Connector import db


class ProcurementBasketMatrixJSONHandler(BaseHandler):

    @throws_handler()
    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self):

        params = json.loads(self.get_argument('values'))
        provision_ids = params.get('ids', None)

        provisions = await db.list(
            "select provision_id, product_id, quantity, cost, total_cost, current_timestamp from ph_provision where provision_id = any($1::int[])",
            (provision_ids,))

        #print(provisions)

        product_ids = [provision["product_id"] for provision in provisions]
        #print("p ids: ", product_ids)

        provisions_products_quantities = {provision["product_id"]: provision["quantity"] for provision in provisions}
        #print(provisions_products_quantities)

        urgent_procurement = int(params.get("urgent_procurement", 0))
        pharmacy = int(params.get("pharmacy", 0))

        pricelist_client = PriceListClient()
        result = await pricelist_client.get_prices_for(ids=product_ids)

        l = list()

        current_user = self.get_current_user()
        current_agent_id = current_user["agent_id"]

        df = pd.DataFrame(result)
        initial_df_in_dict = df.T.to_dict()

        column_ids = sorted(list(df.columns))

        products = await db.list(
            "select product_id, name, current_timestamp from products where product_id = any($1::int[])",
            (product_ids,))

        product_provisions = {}

        for product in products:
            for provision in provisions:
                if product["product_id"] == provision["product_id"]:
                    product_provisions[product["name"]] = provision["provision_id"]

        #print(product_provisions)

        data = {
                "draw": self.get_argument("draw", default=1),
                "recordsTotal": len(result),
                "recordsFiltered": len(result),
            }

        l = list()

        column_ids = [int(col_id) for col_id in column_ids]

        if int(current_agent_id) in column_ids:
            column_ids.remove(int(current_agent_id))

        if urgent_procurement != 0 and pharmacy != 0:
            suppliers = await db.list(
                "select company_name, pharmex_supplier_id, min_sum, pharmacy, urgent_procurement, current_timestamp from supplier where pharmex_supplier_id = any($1::int[]) and urgent_procurement=$2 and pharmacy=$3",
                (column_ids, urgent_procurement, pharmacy,))

        elif urgent_procurement != 0:
            suppliers = await db.list(
                "select company_name, pharmex_supplier_id, min_sum, pharmacy, urgent_procurement, current_timestamp from supplier where pharmex_supplier_id = any($1::int[]) and urgent_procurement=$2",
                (column_ids, urgent_procurement,))

        elif pharmacy != 0:
            suppliers = await db.list(
                "select company_name, pharmex_supplier_id, min_sum, pharmacy, urgent_procurement, current_timestamp from supplier where pharmex_supplier_id = any($1::int[]) and pharmacy=$2",
                (column_ids, pharmacy,))

        else:
            suppliers = await db.list(
                "select company_name, pharmex_supplier_id, min_sum, pharmacy, urgent_procurement, current_timestamp from supplier where pharmex_supplier_id = any($1::int[]) and pharmacy=0",
                (column_ids,))

        db_supplier_ids = [supplier["pharmex_supplier_id"] for supplier in suppliers]

        for c_id in column_ids:
            if c_id not in db_supplier_ids:
                column_ids.remove(c_id)

        # alert
        column_ids = db_supplier_ids

        df_in_dict = initial_df_in_dict

        for p_id, p in initial_df_in_dict.items():
            for sup_id in list(p.keys()):
                if int(sup_id) not in column_ids:
                    del df_in_dict[p_id][sup_id]

        del initial_df_in_dict

        column_ids = [str(col_id) for col_id in column_ids]

        prices_quantities = []

        for product_id in product_ids:

            small_l = []
            small_l.append(provisions_products_quantities[product_id])
            small_l.append(product_id)

            prices_q = 0

            if product_id in df_in_dict:
                for i in df_in_dict[product_id].values():
                    if isinstance(i, dict):
                        prices_q += 1

            prices_quantities.append(prices_q)

            for s_id in column_ids:

                if product_id in list(df_in_dict.keys()):
                    prices_l = {}
                    if isinstance(df_in_dict[product_id][s_id], dict):
                        if 'wire100' in df_in_dict[product_id][s_id]:
                            prices_l["wire100"] = df_in_dict[product_id][s_id]['wire100']

                        if 'wire50' in df_in_dict[product_id][s_id]:
                            prices_l["wire50"] = df_in_dict[product_id][s_id]['wire50']

                        if 'wire25' in df_in_dict[product_id][s_id]:
                            prices_l["wire25"] = df_in_dict[product_id][s_id]['wire25']

                        if 'cash' in df_in_dict[product_id][s_id]:
                            prices_l["cash"] = df_in_dict[product_id][s_id]['cash']

                        if len(prices_l) > 0:
                            small_l.append(prices_l)
                        else:
                            small_l.append(0)
                    else:

                        small_l.append(None)

                else:
                    small_l.append(None)

            l.append(small_l)

        column_ids = [int(col_id) for col_id in column_ids]
        column_names = []

        excluded_titles = ["OOO", "ИП", "ООО", "ЧП"]

        for index, item in enumerate(column_ids):
            for supplier in suppliers:
                if supplier["pharmex_supplier_id"] == item:

                    company_name = supplier["company_name"]

                    for x in excluded_titles:
                        if x in company_name[:3]:
                            company_name = company_name[len(x):]
                            break

                    column_names.append(company_name)

        user_client = AgentUserExecutorClient_ph()
        user = await user_client.get_one(data={"user_id": current_user["user_id"]})

        user_suppliers = user["inclusive_suppliers"] if "inclusive_suppliers" in user else {}
        print(user_suppliers)

        min_costs = []

        for supplier in suppliers:
            sup_id = supplier["pharmex_supplier_id"]

            try:
                min_sum = user_suppliers[str(sup_id)]
            except KeyError:
                min_sum = 300000

            min_costs.append(min_sum)

        for l_index, l_item in enumerate(l):
            for p in products:
                if p["product_id"] == l_item[1]:
                    l[l_index][1] = p["name"]

        wire_100_sums = []
        wire_50_sums = []
        wire_25_sums = []
        cash_sums = []

        for i in range(0, len(suppliers)):
            wire_100_sums.append(0)
            wire_50_sums.append(0)
            wire_25_sums.append(0)
            cash_sums.append(0)

        for index, item in enumerate(l):
            for sub_index, sub_item in enumerate(item[2:]):
                sum_100 = 0
                sum_50 = 0
                sum_25 = 0
                sum_cash = 0

                if isinstance(sub_item, dict):
                    if 'wire100' in sub_item:
                        sum_100 += sub_item['wire100'] * item[0]
                    if 'wire50' in sub_item:
                        sum_50 += sub_item['wire50'] * item[0]
                    if 'wire25' in sub_item:
                        sum_25 += sub_item['wire25'] * item[0]
                    if 'cash' in sub_item:
                        sum_cash += sub_item['cash'] * item[0]

                wire_100_sums[sub_index] += sum_100
                wire_50_sums[sub_index] += sum_50
                wire_25_sums[sub_index] += sum_25
                cash_sums[sub_index] += sum_cash

        data["data"] = l
        data["columns"] = column_names
        data["min_costs"] = min_costs

        data["wire_100_sums"] = wire_100_sums
        data["wire_50_sums"] = wire_50_sums
        data["wire_25_sums"] = wire_25_sums
        data["cash_sums"] = cash_sums
        data["supplier_ids"] = column_ids

        data["prices_quantities"] = prices_quantities
        data["product_provisions"] = [product_provisions]

        self.write(json.dumps(data, cls=DateTimeEncoderCompact))
        self.finish()
