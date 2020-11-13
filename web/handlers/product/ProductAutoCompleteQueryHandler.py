# region import
# endregion
import json

from elasticsearch_async import AsyncElasticsearch

from web.handlers.BaseHandler import *


es = AsyncElasticsearch(hosts=['52.19.43.93'],
                        http_auth=('vita', 'g6t7y7h98hyg67'), port=8080)


class ProductAutoCompleteQueryHandler(BaseHandler):

    @allowedRole(Role.PHARMA_CLIENT)
    async def get(self):
        q = self.get_argument("query", default=None)
        body = {
            "query": {
                "match_phrase_prefix": {
                    "name": q
                }
            }
        }
        res = await es.search(index="productsexecutor-index", body={
            "query": {
                "multi_match": {
                    "query": q,
                    "type": "phrase_prefix",
                    "fields": ["company_name", "name"]
                }
            },
            "size": 20
        })
        result = res['hits']
        suggestion = []
        for r in result["hits"]:
            index = r["_index"]
            name = r["_source"]["name"]
            manufacturer = r["_source"]["manufacturer"]
            manufacturer_id = r["_source"]["manufacturer_id"]
            search_id = r["_source"]["product_id"]
            suggestion.append({"value": name,
                               "data": {"id": search_id,
                                        "manufacturer": manufacturer,
                                        "manufacturer_id": manufacturer_id}})
        d = {
            "query": q,
            "suggestions": suggestion
        }
        self.write(json.dumps(d,
                              ensure_ascii=False, ).encode('utf8'))
        self.finish()
