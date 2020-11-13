# region import
import tornado.web
from web.handlers.BaseHandler import *
from pricelists.PriceListClient import PriceListClient
# endregion
import json

from elasticsearch_async import AsyncElasticsearch

es = AsyncElasticsearch(hosts=['52.19.43.93'],
                        http_auth=('vita', 'g6t7y7h98hyg67'), port=8080)


class AutoCompleteQueryHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self):
        q = self.get_argument("query", default=None)

        res = await es.search(index="agentexecutor-index,productsexecutor-index", body={
            "query": {
                "multi_match": {
                    "query": q,
                    "type": "phrase_prefix",
                    "fields": ["company_name", "name"]
                }
            },
            "size": 10
        })
        result = res['hits']
        suggestion = []
        for r in result["hits"]:
            index = r["_index"]
            if index == "productsexecutor-index":
                name = r["_source"]["name"] + " (" + r["_source"]["manufacturer"] + ") "
                category = "товары"
                #link = "/products/" + \
                #    str(r["_source"]["product_id"]) + "/view/"
                search_id = r["_source"]["product_id"]



            else:
                name = r["_source"]["company_name"]
                category = "агенты"
                #link = "/agents/" + str(r["_source"]["agent_id"]) + "/view/"
                search_id = r["_source"]["agent_id"]
            suggestion.append({"value": name,
                               "category": category,
                               "data": {"id": search_id,
                                        "category": category,
                                        #"link": link
                                        }})

        price_client = PriceListClient()
        p_ids = [s["data"]["id"] for s in suggestion]
        prices = await price_client.get_prices_for(ids=p_ids)

        available_products = []

        for sup_id, p_details in prices.items():
            for prod_id in list(p_details.keys()):
                if int(prod_id) not in available_products:
                    available_products.append(int(prod_id))

        for s in suggestion:
            if s["data"]["id"] in available_products:
                s["available"] = 1
            else:
                s["available"] = 0

        d = {
            "query": q,
            "suggestions": suggestion
        }

        self.write(json.dumps(d))
        self.finish()
