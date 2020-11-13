#!/usr/local/bin/python3.6
import asyncio
import logging
import os  # NOQA: E402
os.environ['VITA_CONFIG'] = '/var/www/config.py'  # NOQA: E402

from modules.kinetic_core import Logger
from modules.kinetic_core.AbstractExecutor import executor
from modules.kinetic_core.QueueListener import QueueListener

main_loop = asyncio.get_event_loop()

#Logger.init(level=logging.DEBUG)

# Регистрируем наш слушатель - он принимает сообщения из очереди rabbitMQ


async def test():
    from forecasting.DemandExecutorClient import DemandExecutorClient
    executor = DemandExecutorClient()
    await executor.calc2()
    print("********** TEST COMPLETE **********")
async def paginate():
    from datetime import datetime
    from forecasting.DemandExecutorClient import DemandExecutorClient
    executor = DemandExecutorClient()
    # r = await executor.list_active(10, 0, 1, 5621)
    r = await executor.paginate(10, 0, 1, datetime(2018,9,1), datetime(2019,1,1))
    print(r)

async def correct_demand():
    from warehouse.ProductsExecutorClient import ProductsExecutorClient
    products_executor = ProductsExecutorClient()
    from forecasting.DemandYearlyExecutorClient import DemandYearlyExecutorClient
    dmye = DemandYearlyExecutorClient()
    all_products = await products_executor.get_all()
    for p in all_products:
        product = all_products[p]
        if product["visible"] == -1:
            print("modified", p)
            await dmye.modify(data={"product_id": product["product_id"],
                              "jan": 0.09,
                              "feb": 0.09,
                              "mar": 0.09,
                              "apr": 0.09,
                              "may": 0.07,
                              "jun": 0.07,
                              "jul": 0.07,
                              "aug": 0.07,
                              "sep": 0.09,
                              "oct": 0.09,
                              "nov": 0.09,
                              "dec": 0.09,
                              "quantity": 0
                              })

async def import_demandd():
    from warehouse.ProductsExecutorClient import ProductsExecutorClient
    products_executor = ProductsExecutorClient()
    from forecasting.DemandYearlyExecutorClient import DemandYearlyExecutorClient
    dmye = DemandYearlyExecutorClient()
    import pandas as pd
    import numpy as np
    data = pd.read_excel("/var/www/business/forecasting/distribution Muzaffar last version.xlsx")
    data = data.replace(np.nan, 0)
    # print(data)
    for row in data.iterrows():
        name = (row[1].product_name)
        standard = row[1].standard
        urgent = row[1].urgent
        visible = row[1].visible
        category = row[1].category if type(row[1].category) == str else ""
        product = await products_executor.get_one_name(data={"name": name})
        if product is not None:
            total = (row[1].quantity)
            if (total >= 12):
                jan = (row[1].jan)
                feb = (row[1].feb)
                mar = (row[1].mar)
                apr = (row[1].apr)
                may = (row[1].may)
                jun = (row[1].jun)
                jul = (row[1].jul)
                aug = (row[1].aug)
                sep = (row[1].sep)
                oct = (row[1].oct)
                nov = (row[1].nov)
                dec = (row[1].dec)
                jan_ = jan/total
                feb_ = feb/total
                mar_ = mar/total
                apr_ = apr/total
                may_ = may/total
                jun_ = jun/total
                jul_ = jul/total
                aug_ = aug/total
                sep_ = sep/total
                oct_ = oct/total
                nov_ = nov/total
                dec_ = dec/total
                await dmye.modify(data={"product_id":product["product_id"],
                                  "jan": jan_,
                                  "feb": feb_,
                                  "mar": mar_,
                                  "apr": apr_,
                                  "may": may_,
                                  "jun": jun_,
                                  "jul": jul_,
                                  "aug": aug_,
                                  "sep": sep_,
                                  "oct": oct_,
                                  "nov": nov_,
                                  "dec": dec_,
                                  "quantity": total
                                  })
                await products_executor.modify(data={"product_id": product["product_id"], "standard_procurement": standard, "urgent_procurement": urgent, "visible": visible, "category": category})
                print("mod")
            elif total >= 0:
                if (total > 0.99) & (total < 1):
                    total = 1
                await dmye.modify(data={"product_id": product["product_id"],
                                        "jan": 1/12,
                                        "feb": 1/12,
                                        "mar": 1/12,
                                        "apr": 1/12,
                                        "may": 1/12,
                                        "jun": 1/12,
                                        "jul": 1/12,
                                        "aug": 1/12,
                                        "sep": 1/12,
                                        "oct": 1/12,
                                        "nov": 1/12,
                                        "dec": 1/12,
                                        "quantity": total
                                        })
                await products_executor.modify(data={"product_id": product["product_id"], "standard_procurement": standard, "urgent_procurement": urgent, "visible": visible, "category": category})
                print("mod")
            print("done")
    print("********** TEST COMPLETE **********")


async def import_groups():
    from warehouse.ProductsExecutorClient import ProductsExecutorClient
    products_executor = ProductsExecutorClient()
    import pandas as pd
    import numpy as np
    data = pd.read_excel("/var/www/business/forecasting/groups.xlsx")
    data = data.replace(np.nan, 0)
    print(data)
    for row in data.iterrows():
        product_id = (row[1].product_id)
        procurement_group = int(row[1].procurement_group)
        procurement_group_priority = int(row[1].procurement_group_priority)
        print(procurement_group, procurement_group_priority)
        product = await products_executor.get_one(product_id=product_id)
        if product is not None:
            await products_executor.modify(data={"product_id": product["product_id"], "procurement_group": procurement_group, "procurement_group_priority": procurement_group_priority})
            print("mod")
    print("********** TEST COMPLETE **********")


async def load_data():
    from warehouse.ProductsExecutorClient import ProductsExecutorClient
    products_executor = ProductsExecutorClient()
    from forecasting.DemandYearlyExecutorClient import DemandYearlyExecutorClient
    dmye = DemandYearlyExecutorClient()
    from warehouse.manufacturer.ManufacturerClient import ManufacturerClient
    manufacturer_executor = ManufacturerClient()
    all_products = await products_executor.get_all()
    import pandas as pd
    df = pd.DataFrame(columns=["product_id","product_name","manufacturer","country","jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec","quantity","standard","urgent","visible"])
    print(df)
    for p in all_products:
        product = all_products[p]
        manufacturer = await manufacturer_executor.get_by_id(mid=product["manufacturer_id"])

        if manufacturer is None:
            manufacturer = {"name": product["manufacturer"], "country": product["manufacturer_country"]}
        manufacturer["country"] = manufacturer.get("country", "Неизвестно")
        print(product["product_id"],manufacturer)
        dy = await dmye.get_one(data={"product_id": product["product_id"]})
        if dy is None:
            print("missing dy for ", p)
            data = {
                "product_id": product["product_id"],
                "product_name": product["name"],
                "manufacturer": manufacturer["name"],
                "country": manufacturer["country"],
                "jan": 0.09,
                "feb": 0.09,
                "mar": 0.09,
                "apr": 0.09,
                "may": 0.07,
                "jun": 0.07,
                "jul": 0.07,
                "aug": 0.07,
                "sep": 0.09,
                "oct": 0.09,
                "nov": 0.09,
                "dec": 0.09,
                "quantity": None,
                "standard": -1,
                "urgent": -1,
                "visible": -1,
            }
        else:

            data = {
                "product_id": product["product_id"],
                "product_name": product["name"],
                "manufacturer": manufacturer["name"],
                "country": manufacturer["country"],
                "jan": dy["jan"],
                "feb": dy["feb"],
                "mar": dy["mar"],
                "apr": dy["apr"],
                "may": dy["may"],
                "jun": dy["jun"],
                "jul": dy["jul"],
                "aug": dy["aug"],
                "sep": dy["sep"],
                "oct": dy["oct"],
                "nov": dy["nov"],
                "dec": dy["dec"],
                "quantity": dy["quantity"],
                "standard": product["standard_procurement"],
                "urgent": product["urgent_procurement"],
                "visible": product["visible"],
            }
        df = df.append(data, ignore_index=True)
    print(df)
    writer = pd.ExcelWriter('/var/www/business/forecasting/distribution.xlsx')
    df.to_excel(writer, "Sheet1")
    writer.save()
    print("OK")

async def load_data2():
    from warehouse.ProductsExecutorClient import ProductsExecutorClient
    products_executor = ProductsExecutorClient()
    from forecasting.DemandYearlyExecutorClient import DemandYearlyExecutorClient
    dmye = DemandYearlyExecutorClient()
    from warehouse.manufacturer.ManufacturerClient import ManufacturerClient
    manufacturer_executor = ManufacturerClient()
    all_products = await products_executor.get_all()
    import pandas as pd
    df = pd.DataFrame(columns=["product_id","product_name","manufacturer","country","jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec","quantity","standard","urgent","visible", "similars"])
    print(df)
    for p in all_products:

        product = all_products[p]
        manufacturer = await manufacturer_executor.get_by_id(mid=product["manufacturer_id"])

        if manufacturer is None:
            manufacturer = {"name": product["manufacturer"], "country": product["manufacturer_country"]}
        manufacturer["country"] = manufacturer.get("country", "Неизвестно")
        print(product["product_id"],manufacturer)


        # similar = await products_executor._autocomplete(q=product["name"], limit=5)
        similars = ""
        # for s in similar:
        #     sim = "---" + str(s["_source"]["product_id"]) + ": " + str(s["_source"]["name"])
        #     similars += sim

        dy = await dmye.get_one(data={"product_id": product["product_id"]})
        if dy is None:
            print("missing dy for ", p)
            data = {
                "similars": similars,
                "product_id": product["product_id"],
                "product_name": product["name"],
                "manufacturer": manufacturer["name"],
                "country": manufacturer["country"],
                "jan": 0.09,
                "feb": 0.09,
                "mar": 0.09,
                "apr": 0.09,
                "may": 0.07,
                "jun": 0.07,
                "jul": 0.07,
                "aug": 0.07,
                "sep": 0.09,
                "oct": 0.09,
                "nov": 0.09,
                "dec": 0.09,
                "quantity": None,
                "standard": -1,
                "urgent": -1,
                "visible": -1,
            }
        else:

            data = {
                "similars": similars,
                "product_id": product["product_id"],
                "product_name": product["name"],
                "manufacturer": manufacturer["name"],
                "country": manufacturer["country"],
                "jan": dy["jan"],
                "feb": dy["feb"],
                "mar": dy["mar"],
                "apr": dy["apr"],
                "may": dy["may"],
                "jun": dy["jun"],
                "jul": dy["jul"],
                "aug": dy["aug"],
                "sep": dy["sep"],
                "oct": dy["oct"],
                "nov": dy["nov"],
                "dec": dy["dec"],
                "quantity": dy["quantity"],
                "standard": product["standard_procurement"],
                "urgent": product["urgent_procurement"],
                "visible": product["visible"],
            }
        df = df.append(data, ignore_index=True)
    print(df)
    print(df.describe())
    writer = pd.ExcelWriter('/var/www/business/forecasting/distribution.xlsx')
    df.to_excel(writer, "Sheet1")
    writer.save()
    print("OK")


async def load_data3():
    from warehouse.ProductsExecutorClient import ProductsExecutorClient
    products_executor = ProductsExecutorClient()
    from forecasting.DemandYearlyExecutorClient import DemandYearlyExecutorClient
    dmye = DemandYearlyExecutorClient()
    from warehouse.manufacturer.ManufacturerClient import ManufacturerClient
    manufacturer_executor = ManufacturerClient()
    all_products = await products_executor.get_all()
    import pandas as pd
    df = pd.DataFrame(columns=["product_id","product_name","manufacturer","country","jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec","quantity","standard","urgent","visible", "similars"])
    # print(df)
    for p in all_products:

        product = all_products[p]
        manufacturer = await manufacturer_executor.get_by_id(mid=product["manufacturer_id"])

        if manufacturer is None:
            manufacturer = {"name": product["manufacturer"], "country": product["manufacturer_country"]}
        manufacturer["country"] = manufacturer.get("country", "Неизвестно")
        print(product["product_id"],manufacturer)


        # similar = await products_executor._autocomplete(q=product["name"], limit=5)
        similars = ""
        # for s in similar:
        #     sim = "---" + str(s["_source"]["product_id"]) + ": " + str(s["_source"]["name"])
        #     similars += sim

        dy = await dmye.get_one(data={"product_id": product["product_id"]})
        if dy is None:
            print("missing dy for ", p)
            data = {
                "similars": similars,
                "product_id": product["product_id"],
                "product_name": product["name"],
                "manufacturer": manufacturer["name"],
                "country": manufacturer["country"],
                "jan": 0,
                "feb": 0,
                "mar": 0,
                "apr": 0,
                "may": 0,
                "jun": 0,
                "jul": 0,
                "aug": 0,
                "sep": 0,
                "oct": 0,
                "nov": 0,
                "dec": 0,
                "quantity": None,
                "standard": -1,
                "urgent": -1,
                "visible": -1,
            }
        else:

            data = {
                "similars": similars,
                "product_id": product["product_id"],
                "product_name": product["name"],
                "manufacturer": manufacturer["name"],
                "country": manufacturer["country"],
                "jan": dy["jan"]*dy["quantity"],
                "feb": dy["feb"]*dy["quantity"],
                "mar": dy["mar"]*dy["quantity"],
                "apr": dy["apr"]*dy["quantity"],
                "may": dy["may"]*dy["quantity"],
                "jun": dy["jun"]*dy["quantity"],
                "jul": dy["jul"]*dy["quantity"],
                "aug": dy["aug"]*dy["quantity"],
                "sep": dy["sep"]*dy["quantity"],
                "oct": dy["oct"]*dy["quantity"],
                "nov": dy["nov"]*dy["quantity"],
                "dec": dy["dec"]*dy["quantity"],
                "quantity": dy["quantity"],
                "standard": product["standard_procurement"],
                "urgent": product["urgent_procurement"],
                "visible": product["visible"],
            }
        df = df.append(data, ignore_index=True)
    # print(df)
    print(df.describe())
    writer = pd.ExcelWriter('/var/www/business/forecasting/distribution.xlsx')
    df.to_excel(writer, "Sheet1")
    writer.save()
    print("OK")

async def load_only_prducts():
    from warehouse.ProductsExecutorClient import ProductsExecutorClient
    products_executor = ProductsExecutorClient()
    from warehouse.manufacturer.ManufacturerClient import ManufacturerClient
    manufacturer_executor = ManufacturerClient()
    from warehouse.StockExecutorClient import StockExecutorClient
    sex = StockExecutorClient()
    all_products = await products_executor.get_all()
    import pandas as pd
    df = pd.DataFrame(columns=["product_id","product_name","manufacturer","country","parent_name","procurement_group","standard","urgent","visible","stock", "demand","provision","member_provision","member_stock"])

    from forecasting.DemandExecutorClient import DemandExecutorClient
    demand_executor = DemandExecutorClient()
    from datetime import datetime
    today = datetime.now()
    all_demands = await demand_executor.get_all_products_by_date_range(data=
                                                                       {"start_date": today,
                                                                        "days": 30,
                                                                        "warehouse_id": 1})

    for p in all_products:
        demand = all_demands[p]
        product = all_products[p]
        pinfo=await products_executor.get_procurement_information(data={"product_id": product["product_id"]})
        provision=0
        member_stock = 0
        member_provision = 0
        for m in pinfo:
            print(pinfo[m])
            if str(m)!=str(product["product_id"]):
                member_stock+=pinfo[m]["stock"]
                member_provision+=pinfo[m]["standard"]
            else:
                provision=pinfo[m]["standard"]

        stock = await sex.get_by_product_by_warehouse(data={"warehouse_id": 1, "product_id": product["product_id"]})

        manufacturer = await manufacturer_executor.get_by_id(mid=product["manufacturer_id"])

        if manufacturer is None:
            manufacturer = {"name": product["manufacturer"], "country": product["manufacturer_country"]}
        manufacturer["country"] = manufacturer.get("country", "Неизвестно")


        # similar = await products_executor._autocomplete(q=product["name"], limit=5)
        similars = ""
        # for s in similar:
        #     sim = "---" + str(s["_source"]["product_id"]) + ": " + str(s["_source"]["name"])
        #     similars += sim
        if product["to_delete"]!=1:
            data = {
                "product_id": product["product_id"],
                "product_name": product["name"],
                "manufacturer": manufacturer["name"],
                "country": manufacturer["country"],
                "parent_name": product["parent_name"],
                "procurement_group": product["procurement_group"],
                "standard": product["standard_procurement"],
                "urgent": product["urgent_procurement"],
                "visible": product["visible"],
                "stock": stock,
                "demand": demand,
                "provision": provision,
                "member_stock": member_stock,
                "member_provision": member_provision
            }
            df = df.append(data, ignore_index=True)
        print(data)
    # print(df)
    # print(df.describe())
    writer = pd.ExcelWriter('/var/www/business/sales/products.xlsx')
    df.to_excel(writer, "Sheet1")
    writer.save()
    print("OK")


async def duplicate_helper():
    from warehouse.ProductsExecutorClient import ProductsExecutorClient
    products_executor = ProductsExecutorClient()
    from forecasting.DemandYearlyExecutorClient import DemandYearlyExecutorClient
    dmye = DemandYearlyExecutorClient()
    from warehouse.manufacturer.ManufacturerClient import ManufacturerClient
    manufacturer_executor = ManufacturerClient()
    all_products = await products_executor.get_all()
    import pandas as pd
    df = pd.DataFrame(columns=["parent","product_id","product_name","manufacturer","country"])
    # print(df)
    for p in all_products:

        parent_product_id = p

        product = all_products[p]
        manufacturer = await manufacturer_executor.get_by_id(mid=product["manufacturer_id"])

        if manufacturer is None:
            manufacturer = {"name": product["manufacturer"], "country": product["manufacturer_country"]}
        manufacturer["country"] = manufacturer.get("country", "Неизвестно")
        print(product["product_id"],manufacturer, product["name"], "---------------------")


        similar = await products_executor._autocomplete(q=product["name"], limit=10)
        # print(similar)
        # quit()
        for s in similar:
            print(s["_score"], s["_source"])
            similar_product_id_p = "p"+str(s["_source"]["product_id"])
            try:
                similar_product = product = all_products[similar_product_id_p]
                manufacturer = await manufacturer_executor.get_by_id(mid=product["manufacturer_id"])
                if manufacturer is None:
                    manufacturer = {"name": product["manufacturer"], "country": product["manufacturer_country"]}
                manufacturer["country"] = manufacturer.get("country", "Неизвестно")
                data = {"parent": parent_product_id, "product_id": similar_product["product_id"], "product_name": similar_product["name"], "manufacturer": manufacturer["name"], "country": manufacturer["country"]}
                df = df.append(data, ignore_index=True)
            except KeyError:
                pass
    # print(df)
    # print(df.describe())
    # writer = pd.ExcelWriter('/var/www/business/forecasting/duplicate_finder.xlsx')
    # df.to_excel(writer, "Sheet1")
    # writer.save()
    print("OK")

async def get_by_product_id_by_date_range(product_id):
    from datetime import datetime
    from forecasting.DemandExecutorClient import DemandExecutorClient
    executor = DemandExecutorClient()
    q = await executor.get_by_product_id_by_date_range(data={"warehouse_id": 1, "product_id": product_id, "start_date": datetime.now(), "days": 14})
    print(q)
    print("********** TEST COMPLETE **********")

async def mod_dem_y():
    from datetime import datetime
    from forecasting.DemandYearlyExecutorClient import DemandYearlyExecutorClient
    executor = DemandYearlyExecutorClient()
    # q = await executor.modify(data={"warehouse_id": 1, "product_id": 13435,"mar":0.03})
    q = await executor.get_one(data={"warehouse_id": 1, "product_id": 13435})
    print(q)
    print("********** TEST COMPLETE **********")

async def get_yearly_demand():
    from datetime import datetime
    from forecasting.DemandYearlyExecutorClient import DemandYearlyExecutorClient
    executor = DemandYearlyExecutorClient()
    # q = await executor.modify(data={"warehouse_id": 1, "product_id": 13435,"mar":0.03})
    q = await executor.get_one(data={"warehouse_id": 1, "product_id": 5992})
    print(q)
    print("********** TEST COMPLETE **********")

async def clear_yearly_demand():
    from forecasting.DemandExecutorClient import DemandExecutorClient
    executor = DemandExecutorClient()
    q = await executor.clear_demand_yearly()

async def load_products():
    # from warehouse.ProductsExecutorClient import ProductsExecutorClient
    # products_executor = ProductsExecutorClient()
    # all_products = await products_executor.get_all()
    # print(all_products)
    import pandas as pd
    pd.set_option('display.max_rows', 3000)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    data = pd.read_excel("/Users/Mustafo/Desktop/distribution2.xlsx")
    # data = data.replace(np.nan, 0)
    data["dosage_form"] = ""
    data["dosage_size"] = 0
    data["dosage_measurement"] = ""
    data["dosage_quantity"] = 0
    def c(row):
        key = ["гель"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "гель"

        key = ["табл ", "табл.", "таб ", "таб.", "tabl", "драж","табл"," таб","таблет","тб.","тб "," тб"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "таблетки"

        key = ["капл.","капл ","капли","кап."," капл"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "капли"

        key = ["р-р", "раст ", "раст.", "раствор","амп.", "амп "," амп", "амл "," амл","амл.","%"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "раствор"

        key = ["крем"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "крем"

        key = ["мазь ","мазь"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "мазь"

        key = ["сироп"," сир "]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "сироп"

        key = ["спрей", "аэр", "спр","доз.","доз ","мкг"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "спрей"

        key = ["капс.", "капс ", "капс"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "капсулы"

        key = ["сусп.", "сусп",]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "суспензия"

        key = ["шпри"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "шприц"

        key = ["пор.", "пор ","порош","пор-","пак.","пак.","саш.","саше ","сш.","сш "]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "порошок"

        key = ["супп.", "супп ", "свеч","суппоз.рект"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "суппозиторий"

        key = ["масл"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "масло"

        key = ["бинт"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "бинт"

        key = ["шамп","шанп"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "шампунь"

        key = ["шипо"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "шиповник"

        key = ["чай"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "чай"

        key = ["трав"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "трава"

        key = ["семе"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "семена"

        key = ["трус"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "трусы"

        key = ["трубк"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "трубка"

        key = ["прокл"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "прокладки"

        key = ["тест ","тест."]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "тест"

        key = ["сывор","сыв ","сыв."]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "сыворотка"

        key = ["соль ","соль."]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "соль"

        key = ["корни", "корен"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "корень"

        key = ["скальп"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "скальпель"

        key = ["сист"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "система"

        key = ["лист"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "листья"

        key = ["семен"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "семена"

        key = ["эмул"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "эмульсия"

        key = ["салфет"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "салфетки"

        key = ["презер"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "презервативы"

        key = ["пояс"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "пояс"

        key = ["подгу"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "подгузники"

        key = ["цвет"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "цветки"

        key = ["игла"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "игла"

        key = ["паста"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "паста"

        key = ["мыло"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "мыло"

        key = ["вата","ватн"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "вата"

        key = ["вакц"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "вакцина"

        key = ["банда","бонда"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "бандаж"

        key = ["пасти"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "пастилки"

        key = ["тампо","томпо"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "тампон"

        key = ["вода"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "вода"

        key = ["лезв"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "лезвие"

        key = ["эликс", "экстр", "настой"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "эликсир"

        key = ["спирт"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "спирт"

        key = ["полотенц"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "полотенце"

        key = ["перч"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "перчатки"

        key = ["халат"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "халат"

        key = ["пласты","пластр","лейкопл"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "пластырь"

        key = ["марл"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "марля"

        key = ["маск"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "маска"

        key = ["налок"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "налокотник"

        key = ["наколе"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "наколенник"

        # key = ["кислота","к-та"]
        # for i in key:
        #     if i.upper() in str(row["product_name"]).upper():
        #         row["dosage_form"] = "кислота"

        key = ["ополас"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "ополаскиватель"

        key = ["катет"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "катетер"

        key = ["грану", "гран-","гран."]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "гранулы"

        key = ["зонд"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "зонд"

        key = ["щетк"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "щетка"

        key = ["присы"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "присыпка"


        words = str.split(str(row["product_name"]).upper())
        previous_word = None
        look_for_quantity_in_next_word = False
        quantity = None
        quantity_found = False
        quantity_found_in_word_c = None
        measurement_value = {}
        measurement_label = {}
        measurement_value_found = False
        integers = ["0","1","2","3","4","5","6","7","8","9"]
        measurements = ["Г", "МГ", "МЛ", "МЛ"]
        c = 0
        for word in words:

            c += 1
            if "№" in word:
                digits = ""
                for letter in word:
                    if letter in integers:
                        digits += letter
                if len(digits) > 0:
                    quantity = int(digits)
                    quantity_found = True
                else:
                    look_for_quantity_in_next_word = True
            if look_for_quantity_in_next_word:
                look_for_quantity_in_next_word = False
                digits = ""
                for letter in word:
                    if letter in integers:
                        digits += letter
                if len(digits) > 0:
                    quantity = int(digits)
                    quantity_found = True
                    quantity_found_in_word_c = c
            measurements_in_word = {}
            for measurement in measurements:
                if measurement in word:
                    if ("Г" in word) and ("МГ" in word):
                        measurements_in_word["МГ"] = 1
                    else:
                        measurements_in_word[measurement] = 1
                    # measurements_in_word[measurement] = 1
            # print(word,"w")
            # if ("Г" in word) and ("МГ" in word):
            #     print(word, "deleting")
            #     del measurements_in_word["Г"]

            if len(measurements_in_word) > 0:
                for k in measurements_in_word:
                    measurement_label[k] = 1
                digits = ""
                for letter in word:
                    if letter in integers:
                        digits += letter
                    elif letter in [".",","]:
                        digits += "."
                if len(digits) > 0:
                    measurement_value[digits] = 1
                    measurement_value_found = True
                if not measurement_value_found:
                    if (c-1)!=quantity_found_in_word_c:
                        previous_word = words[c-2]
                        digits = ""
                        for letter in previous_word:
                            if letter in integers:
                                digits += letter
                            elif letter in [".", ","]:
                                digits += "."
                        if len(digits) > 0:
                            measurement_value[digits] = 1
                            measurement_value_found = True
        for m in measurement_value:
            try:
                row["dosage_size"] = float(m)
            except ValueError:
                pass
        for m in measurement_label:
            row["dosage_measurement"] = m
        row["dosage_quantity"] = quantity
        # print(words)
        # print("measurements ", measurement_label)
        # print("measurements values ", measurement_value)
        # print("quantity ", quantity)
        # print("form ", row["dosage_form"])
        #
        # print("========================","========================")
        # if "БИСЕПТОЛ" in words:
        #     quit()
        #     "БИСЕПТОЛ"






        return row

    data=data.apply(lambda row: c(row), axis=1)
    # data.ix[data.product_name.str.contains("гель",case=False),"dosage_form"]="kjk"
    grouped = data.groupby('dosage_form')['dosage_form'].count()
    print(data[data["dosage_form"]==""])
    print(grouped)
    writer = pd.ExcelWriter("/Users/Mustafo/Desktop/autofill.xlsx")
    data.to_excel(writer, "Sheet1")
    writer.save()

async def parse_products():
    # from warehouse.ProductsExecutorClient import ProductsExecutorClient
    # products_executor = ProductsExecutorClient()
    # all_products = await products_executor.get_all()
    # print(all_products)
    import pandas as pd
    pd.set_option('display.max_rows', 3000)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    data = pd.read_excel("/Users/Mustafo/Desktop/distribution2.xlsx")
    # data = data.replace(np.nan, 0)
    data["dosage_form"] = ""
    data["dosage_size"] = 0
    data["dosage_measurement"] = ""
    data["dosage_quantity"] = 0
    def c(row):
        key = ["гель"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "гель"

        key = ["табл ", "табл.", "таб ", "таб.", "tabl", "драж","табл"," таб","таблет","тб.","тб "," тб"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "таблетки"

        key = ["капл.","капл ","капли","кап."," капл"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "капли"

        key = ["р-р", "раст ", "раст.", "раствор","амп.", "амп "," амп", "амл "," амл","амл.","%"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "раствор"

        key = ["крем"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "крем"

        key = ["мазь ","мазь"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "мазь"

        key = ["сироп"," сир "]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "сироп"

        key = ["спрей", "аэр", "спр","доз.","доз ","мкг"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "спрей"

        key = ["капс.", "капс ", "капс"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "капсулы"

        key = ["сусп.", "сусп",]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "суспензия"

        key = ["шпри"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "шприц"

        key = ["пор.", "пор ","порош","пор-","пак.","пак.","саш.","саше ","сш.","сш "]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "порошок"

        key = ["супп.", "супп ", "свеч","суппоз.рект"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "суппозиторий"

        key = ["масл"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "масло"

        key = ["бинт"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "бинт"

        key = ["шамп","шанп"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "шампунь"

        key = ["шипо"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "шиповник"

        key = ["чай"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "чай"

        key = ["трав"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "трава"

        key = ["семе"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "семена"

        key = ["трус"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "трусы"

        key = ["трубк"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "трубка"

        key = ["прокл"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "прокладки"

        key = ["тест ","тест."]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "тест"

        key = ["сывор","сыв ","сыв."]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "сыворотка"

        key = ["соль ","соль."]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "соль"

        key = ["корни", "корен"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "корень"

        key = ["скальп"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "скальпель"

        key = ["сист"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "система"

        key = ["лист"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "листья"

        key = ["семен"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "семена"

        key = ["эмул"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "эмульсия"

        key = ["салфет"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "салфетки"

        key = ["презер"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "презервативы"

        key = ["пояс"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "пояс"

        key = ["подгу"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "подгузники"

        key = ["цвет"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "цветки"

        key = ["игла"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "игла"

        key = ["паста"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "паста"

        key = ["мыло"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "мыло"

        key = ["вата","ватн"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "вата"

        key = ["вакц"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "вакцина"

        key = ["банда","бонда"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "бандаж"

        key = ["пасти"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "пастилки"

        key = ["тампо","томпо"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "тампон"

        key = ["вода"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "вода"

        key = ["лезв"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "лезвие"

        key = ["эликс", "экстр", "настой"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "эликсир"

        key = ["спирт"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "спирт"

        key = ["полотенц"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "полотенце"

        key = ["перч"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "перчатки"

        key = ["халат"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "халат"

        key = ["пласты","пластр","лейкопл"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "пластырь"

        key = ["марл"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "марля"

        key = ["маск"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "маска"

        key = ["налок"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "налокотник"

        key = ["наколе"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "наколенник"

        # key = ["кислота","к-та"]
        # for i in key:
        #     if i.upper() in str(row["product_name"]).upper():
        #         row["dosage_form"] = "кислота"

        key = ["ополас"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "ополаскиватель"

        key = ["катет"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "катетер"

        key = ["грану", "гран-","гран."]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "гранулы"

        key = ["зонд"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "зонд"

        key = ["щетк"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "щетка"

        key = ["присы"]
        for i in key:
            if i.upper() in str(row["product_name"]).upper():
                row["dosage_form"] = "присыпка"


        words = str.split(str(row["product_name"]).upper())
        previous_word = None
        look_for_quantity_in_next_word = False
        quantity = None
        quantity_found = False
        quantity_found_in_word_c = None
        measurement_value = {}
        measurement_label = {}
        measurement_value_found = False
        integers = ["0","1","2","3","4","5","6","7","8","9"]
        measurements = ["Г", "МГ", "МЛ", "МЛ"]
        c = 0
        for word in words:

            c += 1
            if "№" in word:
                digits = ""
                for letter in word:
                    if letter in integers:
                        digits += letter
                if len(digits) > 0:
                    quantity = int(digits)
                    quantity_found = True
                else:
                    look_for_quantity_in_next_word = True
            if look_for_quantity_in_next_word:
                look_for_quantity_in_next_word = False
                digits = ""
                for letter in word:
                    if letter in integers:
                        digits += letter
                if len(digits) > 0:
                    quantity = int(digits)
                    quantity_found = True
                    quantity_found_in_word_c = c
            measurements_in_word = {}
            for measurement in measurements:
                if measurement in word:
                    if ("Г" in word) and ("МГ" in word):
                        measurements_in_word["МГ"] = 1
                    else:
                        measurements_in_word[measurement] = 1
                    # measurements_in_word[measurement] = 1
            # print(word,"w")
            # if ("Г" in word) and ("МГ" in word):
            #     print(word, "deleting")
            #     del measurements_in_word["Г"]

            if len(measurements_in_word) > 0:
                for k in measurements_in_word:
                    measurement_label[k] = 1
                digits = ""
                for letter in word:
                    if letter in integers:
                        digits += letter
                    elif letter in [".",","]:
                        digits += "."
                if len(digits) > 0:
                    measurement_value[digits] = 1
                    measurement_value_found = True
                if not measurement_value_found:
                    if (c-1)!=quantity_found_in_word_c:
                        previous_word = words[c-2]
                        digits = ""
                        for letter in previous_word:
                            if letter in integers:
                                digits += letter
                            elif letter in [".", ","]:
                                digits += "."
                        if len(digits) > 0:
                            measurement_value[digits] = 1
                            measurement_value_found = True
        for m in measurement_value:
            try:
                row["dosage_size"] = float(m)
            except ValueError:
                pass
        for m in measurement_label:
            row["dosage_measurement"] = m
        row["dosage_quantity"] = quantity
        # print(words)
        # print("measurements ", measurement_label)
        # print("measurements values ", measurement_value)
        # print("quantity ", quantity)
        # print("form ", row["dosage_form"])
        #
        # print("========================","========================")
        # if "БИСЕПТОЛ" in words:
        #     quit()
        #     "БИСЕПТОЛ"






        return row

    data=data.apply(lambda row: c(row), axis=1)
    # data.ix[data.product_name.str.contains("гель",case=False),"dosage_form"]="kjk"
    grouped = data.groupby('dosage_form')['dosage_form'].count()
    print(data[data["dosage_form"]==""])
    print(grouped)
    writer = pd.ExcelWriter("/Users/Mustafo/Desktop/autofill.xlsx")
    data.to_excel(writer, "Sheet1")
    writer.save()


async def add():
    from operations.TitleExecutorClient import TitleExecutorClient
    titex = TitleExecutorClient()
    seed = {
        "product_id": 5934,
        "name": {"АЛЛЕРЦЕТИН":0, "АЛЛЕРЦЕТИН РИНО":0, "АЛЛЕРЦЕТИН-РИНО":0},
        "name_req": 1,
        "dosage_form": {"спрей":0,"спр":0},
        "dosage_form_req": 1,
        "marker": {},
        "marker_req": 0,
        "dosage_size_1": {"0.03%":0},
        "dosage_size_1_req": 1,
        "dosage_size_2": {},
        "dosage_size_2_req": 0,
        "dosage_size_3": {},
        "dosage_size_3_req": 0,
        "dosage_size_unique": {},
        "dosage_size_unique_req": 0,
        "per_dosage_size": {},
        "per_dosage_size_req": 0,
        "volume": {"10мл":0},
        "volume_req": 0,
        "quantity": {"№1":0},
        "quantity_req": 0



    }
    await titex.add(data=seed)
    print("********** TEST COMPLETE **********")

async def import_title_dataold():
    import pandas as pd
    pd.set_option('display.max_rows', 3000)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    data = pd.read_excel("/var/www/business/title recognition data check.xlsx")

    from warehouse.ProductsExecutorClient import ProductsExecutorClient
    pex = ProductsExecutorClient()
    from operations.TitleExecutorClient import TitleExecutorClient
    titex = TitleExecutorClient()

    print(data.head(40))


    # quit()
    c=0
    for row in data.iterrows():
        # print(row[1][1], row[1][3],row[1][0])
        undefined = 1 if (row[1][26]) == 1 else 0

        product_id = (row[1][0])
        # if undefined==1:
        #     print("undefined",product_id)
        #     quit()
            # continue
        name_ = (row[1][2]).split(";")
        name = {}
        for n in name_:
            name[n]=0
        name_req=1
        manufacturer_ = (row[1][3]).split(";")
        manufacturer = {}
        for m in manufacturer_:
            manufacturer[m]=0
        manufacturer_req = 1 if (row[1][4])==1 else 0
        dosage_form_ = (row[1][5])
        if dosage_form_=="спрей":
            dosage_form = {"спрей":0}
        elif dosage_form_=="таблетки":
            dosage_form = {"табл":0,"тб":0,"таб":0}
        elif dosage_form_=="капсулы":
            dosage_form = {"капс":0}
        elif dosage_form_=="суспензия":
            dosage_form = {"сус":0}
        elif dosage_form_=="раствор":
            dosage_form = {"р-р":0,"раст":0,"амп":0,"амл":0,"д/инф":0,"д/ инф":0,"д / инф":0,"д /инф":0,"д.инф":0,"д. инф":0,"я инф":0}
        elif dosage_form_=="порошок":
            dosage_form = {"пор":0,"пак":0,"саш":0,"сш":0}
        elif dosage_form_=="гель":
            dosage_form = {"гель":0}
        elif dosage_form_=="крем":
            dosage_form = {"крем":0}
        elif dosage_form_ == "мазь":
            dosage_form = {"мазь": 0}
        elif dosage_form_ == "суппозиторий":
            dosage_form = {"супп": 0}
        elif dosage_form_ == "пастилки":
            dosage_form = {"пастил": 0}
        elif dosage_form_ == "сироп":
            dosage_form = {"сироп": 0}
        elif dosage_form_ == "капли":
            dosage_form = {"капл": 0,"гл.":0,"г.кап.":0}
        elif dosage_form_ == "эмульсия":
            dosage_form = {"эмул": 0}
        elif dosage_form_ == "линимент":
            dosage_form = {"линим": 0}
        else:
            dosage_form = {}
        dosage_form_req = 1 if (row[1][6]) == 1 else 0
        dosage_size_1_ = (row[1][7])
        dosage_size_1_meas_ = (row[1][8])
        print(dosage_size_1_,dosage_size_1_meas_,1111111111111)
        if dosage_size_1_meas_ == "МГ":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_1 = {str(dosage_size_1_)+"МГ": 0,str(dosage_size_1_)+" МГ": 0,str(dosage_size_1_/1000)+"Г":0,str(dosage_size_1_/1000)+" Г":0, str(round(dosage_size_1_*1000,1))+"МКГ":0,str(round(dosage_size_1_*1000,1))+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_1 = {str(dosage_size_1_/1000)+"Г": 0,str(dosage_size_1_/1000)+" Г": 0,str(dosage_size_1_)+"МГ": 0,str(dosage_size_1_)+" МГ": 0,str(round(dosage_size_1_/1000*100,1))+"%":0,str(round(dosage_size_1_/1000*100,1))+" %":0,str(round(dosage_size_1_*1000,1))+"МКГ":0,str(round(dosage_size_1_*1000,1))+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_1 = {str(dosage_size_1_/1000)+"Г": 0,str(dosage_size_1_/1000)+" Г": 0,str(dosage_size_1_)+"МГ": 0,str(dosage_size_1_)+" МГ": 0,str(round(dosage_size_1_/1000*100,1))+"%":0,str(round(dosage_size_1_/1000*100,1))+" %":0}
            else:
                dosage_size_1 = {}
        elif dosage_size_1_meas_ == "Г":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_1 = {str(round(dosage_size_1_*1000,1))+"МГ": 0,str(round(dosage_size_1_*1000,1))+" МГ": 0,str(dosage_size_1_)+"Г":0,str(dosage_size_1_)+" Г":0, str(round(dosage_size_1_*1000000,1))+"МКГ":0,str(round(dosage_size_1_*1000000,1))+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_1 = {str(dosage_size_1_)+"Г": 0,str(dosage_size_1_)+" Г": 0, str(round(dosage_size_1_*1000,1))+"МГ": 0,str(round(dosage_size_1_*1000,1))+" МГ": 0,str(round(dosage_size_1_*100,1))+"%":0,str(round(dosage_size_1_*100,1))+" %":0,str(round(dosage_size_1_*1000000,1))+"МКГ":0,str(round(dosage_size_1_*1000000,1))+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_1 = {str(dosage_size_1_)+"Г": 0,str(dosage_size_1_)+" Г": 0, str(round(dosage_size_1_*1000,1))+"МГ": 0,str(round(dosage_size_1_*1000,1))+" МГ": 0,str(round(dosage_size_1_*100,1))+"%":0,str(round(dosage_size_1_*100,1))+" %":0}
            else:
                dosage_size_1 = {}
        elif dosage_size_1_meas_ == "МКГ":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_1 = {str(dosage_size_1_/1000)+"МГ": 0,str(dosage_size_1_/1000)+" МГ": 0,str(dosage_size_1_/1000000)+"Г":0,str(dosage_size_1_/1000000)+" Г":0, str(dosage_size_1_)+"МКГ":0,str(dosage_size_1_)+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_1 = {str(dosage_size_1_/1000000)+"Г": 0,str(dosage_size_1_/1000000)+" Г": 0, str(dosage_size_1_/1000)+"МГ": 0,str(dosage_size_1_/1000)+" МГ": 0,str(dosage_size_1_/10000)+"%":0,str(dosage_size_1_/10000)+" %":0,str(dosage_size_1_)+"МКГ":0,str(dosage_size_1_)+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_1 = {str(dosage_size_1_/1000000)+"Г": 0,str(dosage_size_1_/1000000)+" Г": 0, str(dosage_size_1_/1000)+"МГ": 0,str(dosage_size_1_/1000)+" МГ": 0,str(dosage_size_1_/10000)+"%":0,str(dosage_size_1_/10000)+" %":0}
            else:
                dosage_size_1 = {}
        elif dosage_size_1_meas_ == "%":
            dosage_size_1 = {str(dosage_size_1_)+"%": 0,str(dosage_size_1_)+" %": 0,str(round(dosage_size_1_*10,1))+"МГ":0,str(round(dosage_size_1_*10,1))+" МГ":0, str(dosage_size_1_/100)+"Г":0,str(dosage_size_1_/100)+" Г":0}
        elif dosage_size_1_meas_ in ["АТЕ","ДТ","ЕД","ЛЕ","МЕ","МО"]:
            dosage_size_1 = {str(dosage_size_1_)+dosage_size_1_meas_: 0,str(dosage_size_1_)+" "+dosage_size_1_meas_: 0}
        else:
            dosage_size_1 = {}


        for k in dosage_size_1.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                dosage_size_1[k2] = 0
                if (".0" in k)&("0.00" not in k)&("0.01" not in k)&("0.02" not in k)&("0.03" not in k)&("0.04" not in k)&("0.05" not in k)&("0.06" not in k)&("0.07" not in k)&("0.08" not in k)&("0.09" not in k):
                    dosage_size_1[k.replace(".0","")] = 0
            elif "nan" in k:
                del dosage_size_1[k]
        dosage_size_1_req = 1 if (row[1][9]) == 1 else 0
        dosage_size_2_ = (row[1][10])
        dosage_size_2_meas_ = (row[1][11])


        if dosage_size_2_meas_ == "МГ":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_2 = {str(dosage_size_2_)+"МГ": 0,str(dosage_size_2_)+" МГ": 0,str(dosage_size_2_/1000)+"Г":0,str(dosage_size_2_/1000)+" Г":0, str(round(dosage_size_2_*1000,1))+"МКГ":0,str(round(dosage_size_2_*1000,1))+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_2 = {str(dosage_size_2_/1000)+"Г": 0,str(dosage_size_2_/1000)+" Г": 0,str(dosage_size_2_)+"МГ": 0,str(dosage_size_2_)+" МГ": 0,str(round(dosage_size_2_/1000*100,1))+"%":0,str(round(dosage_size_2_/1000*100,1))+" %":0,str(round(dosage_size_2_*1000,1))+"МКГ":0,str(round(dosage_size_2_*1000,1))+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_2 = {str(dosage_size_2_/1000)+"Г": 0,str(dosage_size_2_/1000)+" Г": 0,str(dosage_size_2_)+"МГ": 0,str(dosage_size_2_)+" МГ": 0,str(round(dosage_size_2_/1000*100,1))+"%":0,str(round(dosage_size_2_/1000*100,1))+" %":0}
            else:
                dosage_size_2 = {}
        elif dosage_size_2_meas_ == "Г":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_2 = {str(round(dosage_size_2_*1000,1))+"МГ": 0,str(round(dosage_size_2_*1000,1))+" МГ": 0,str(dosage_size_2_)+"Г":0,str(dosage_size_2_)+" Г":0, str(round(dosage_size_2_*1000000,1))+"МКГ":0,str(round(dosage_size_2_*1000000,1))+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_2 = {str(dosage_size_2_)+"Г": 0,str(dosage_size_2_)+" Г": 0, str(round(dosage_size_2_*1000,1))+"МГ": 0,str(round(dosage_size_2_*1000,1))+" МГ": 0,str(round(dosage_size_2_*100,1))+"%":0,str(round(dosage_size_2_*100,1))+" %":0,str(round(dosage_size_2_*1000000,1))+"МКГ":0,str(round(dosage_size_2_*1000000,1))+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_2 = {str(dosage_size_2_)+"Г": 0,str(dosage_size_2_)+" Г": 0, str(round(dosage_size_2_*1000,1))+"МГ": 0,str(round(dosage_size_2_*1000,1))+" МГ": 0,str(round(dosage_size_2_*100,1))+"%":0,str(round(dosage_size_2_*100,1))+" %":0}
            else:
                dosage_size_2 = {}
        elif dosage_size_2_meas_ == "МКГ":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_2 = {str(dosage_size_2_/1000)+"МГ": 0,str(dosage_size_2_/1000)+" МГ": 0,str(dosage_size_2_/1000000)+"Г":0,str(dosage_size_2_/1000000)+" Г":0, str(dosage_size_2_)+"МКГ":0,str(dosage_size_2_)+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_2 = {str(dosage_size_2_/1000000)+"Г": 0,str(dosage_size_2_/1000000)+" Г": 0, str(dosage_size_2_/1000)+"МГ": 0,str(dosage_size_2_/1000)+" МГ": 0,str(dosage_size_2_/10000)+"%":0,str(dosage_size_2_/10000)+" %":0,str(dosage_size_2_)+"МКГ":0,str(dosage_size_2_)+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_2 = {str(dosage_size_2_/1000000)+"Г": 0,str(dosage_size_2_/1000000)+" Г": 0, str(dosage_size_2_/1000)+"МГ": 0,str(dosage_size_2_/1000)+" МГ": 0,str(dosage_size_2_/10000)+"%":0,str(dosage_size_2_/10000)+" %":0}
            else:
                dosage_size_2 = {}
        elif dosage_size_2_meas_ == "%":
            dosage_size_2 = {str(dosage_size_2_)+"%": 0,str(dosage_size_2_)+" %": 0,str(round(dosage_size_2_*10,1))+"МГ":0,str(round(dosage_size_2_*10,1))+" МГ":0, str(dosage_size_2_/100)+"Г":0,str(dosage_size_2_/100)+" Г":0}
        elif dosage_size_2_meas_ in ["АТЕ","ДТ","ЕД","ЛЕ","МЕ","МО"]:
            dosage_size_2 = {str(dosage_size_2_)+dosage_size_2_meas_: 0,str(dosage_size_2_)+" "+dosage_size_2_meas_: 0}
        else:
            dosage_size_2 = {}

        for k in dosage_size_2.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                dosage_size_2[k2] = 0
                if (".0" in k)&("0.00" not in k)&("0.01" not in k)&("0.02" not in k)&("0.03" not in k)&("0.04" not in k)&("0.05" not in k)&("0.06" not in k)&("0.07" not in k)&("0.08" not in k)&("0.09" not in k):
                    dosage_size_2[k.replace(".0", "")] = 0
            elif "nan" in k:
                del dosage_size_2[k]
        dosage_size_2_req = 1 if (row[1][12]) == 1 else 0
        dosage_size_3_ = (row[1][13])
        dosage_size_3_meas_ = (row[1][14])
        
        
        if dosage_size_3_meas_ == "МГ":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_3 = {str(dosage_size_3_)+"МГ": 0,str(dosage_size_3_)+" МГ": 0,str(dosage_size_3_/1000)+"Г":0,str(dosage_size_3_/1000)+" Г":0, str(round(dosage_size_3_*1000,1))+"МКГ":0,str(round(dosage_size_3_*1000,1))+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_3 = {str(dosage_size_3_/1000)+"Г": 0,str(dosage_size_3_/1000)+" Г": 0,str(dosage_size_3_)+"МГ": 0,str(dosage_size_3_)+" МГ": 0,str(round(dosage_size_3_/1000*100,1))+"%":0,str(round(dosage_size_3_/1000*100,1))+" %":0,str(round(dosage_size_3_*1000,1))+"МКГ":0,str(round(dosage_size_3_*1000,1))+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_3 = {str(dosage_size_3_/1000)+"Г": 0,str(dosage_size_3_/1000)+" Г": 0,str(dosage_size_3_)+"МГ": 0,str(dosage_size_3_)+" МГ": 0,str(round(dosage_size_3_/1000*100,1))+"%":0,str(round(dosage_size_3_/1000*100,1))+" %":0}
            else:
                dosage_size_3 = {}
        elif dosage_size_3_meas_ == "Г":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_3 = {str(round(dosage_size_3_*1000,1))+"МГ": 0,str(round(dosage_size_3_*1000,1))+" МГ": 0,str(dosage_size_3_)+"Г":0,str(dosage_size_3_)+" Г":0, str(round(dosage_size_3_*1000000,1))+"МКГ":0,str(round(dosage_size_3_*1000000,1))+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_3 = {str(dosage_size_3_)+"Г": 0,str(dosage_size_3_)+" Г": 0, str(round(dosage_size_3_*1000,1))+"МГ": 0,str(round(dosage_size_3_*1000,1))+" МГ": 0,str(round(dosage_size_3_*100,1))+"%":0,str(round(dosage_size_3_*100,1))+" %":0,str(round(dosage_size_3_*1000000,1))+"МКГ":0,str(round(dosage_size_3_*1000000,1))+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_3 = {str(dosage_size_3_)+"Г": 0,str(dosage_size_3_)+" Г": 0, str(round(dosage_size_3_*1000,1))+"МГ": 0,str(round(dosage_size_3_*1000,1))+" МГ": 0,str(round(dosage_size_3_*100,1))+"%":0,str(round(dosage_size_3_*100,1))+" %":0}
            else:
                dosage_size_3 = {}
        elif dosage_size_3_meas_ == "МКГ":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_3 = {str(dosage_size_3_/1000)+"МГ": 0,str(dosage_size_3_/1000)+" МГ": 0,str(dosage_size_3_/1000000)+"Г":0,str(dosage_size_3_/1000000)+" Г":0, str(dosage_size_3_)+"МКГ":0,str(dosage_size_3_)+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_3 = {str(dosage_size_3_/1000000)+"Г": 0,str(dosage_size_3_/1000000)+" Г": 0, str(dosage_size_3_/1000)+"МГ": 0,str(dosage_size_3_/1000)+" МГ": 0,str(dosage_size_3_/10000)+"%":0,str(dosage_size_3_/10000)+" %":0,str(dosage_size_3_)+"МКГ":0,str(dosage_size_3_)+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_3 = {str(dosage_size_3_/1000000)+"Г": 0,str(dosage_size_3_/1000000)+" Г": 0, str(dosage_size_3_/1000)+"МГ": 0,str(dosage_size_3_/1000)+" МГ": 0,str(dosage_size_3_/10000)+"%":0,str(dosage_size_3_/10000)+" %":0}
            else:
                dosage_size_3 = {}
        elif dosage_size_3_meas_ == "%":
            dosage_size_3 = {str(dosage_size_3_)+"%": 0,str(dosage_size_3_)+" %": 0,str(round(dosage_size_3_*10,1))+"МГ":0,str(round(dosage_size_3_*10,1))+" МГ":0, str(dosage_size_3_/100)+"Г":0,str(dosage_size_3_/100)+" Г":0}
        elif dosage_size_3_meas_ in ["АТЕ","ДТ","ЕД","ЛЕ","МЕ","МО"]:
            dosage_size_3 = {str(dosage_size_3_)+dosage_size_3_meas_: 0,str(dosage_size_3_)+" "+dosage_size_3_meas_: 0}
        else:
            dosage_size_3 = {}
        for k in dosage_size_3.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                dosage_size_3[k2] = 0
                if (".0" in k)&("0.00" not in k)&("0.01" not in k)&("0.02" not in k)&("0.03" not in k)&("0.04" not in k)&("0.05" not in k)&("0.06" not in k)&("0.07" not in k)&("0.08" not in k)&("0.09" not in k):
                    dosage_size_3[k.replace(".0", "")] = 0
            elif "nan" in k:
                del dosage_size_3[k]
        dosage_size_3_req = 1 if (row[1][15]) == 1 else 0

        per_dosage_size_ = (row[1][16])
        per_dosage_size_meas_ = (row[1][17])
        if per_dosage_size_meas_=="МЛ":
            per_dosage_size = {str(per_dosage_size_) + "МЛ": 0, str(per_dosage_size_) + " МЛ": 0, str(per_dosage_size_ / 1000) + "Л": 0, str(per_dosage_size_ / 1000) + " Л": 0}
        elif per_dosage_size_meas_=="Г":
            per_dosage_size = {str(per_dosage_size_) + "Г": 0, str(per_dosage_size_) + " Г": 0, str(round(per_dosage_size_ * 1000,1)) + "МГ": 0, str(round(per_dosage_size_ * 1000,1)) + " МГ": 0}
        elif per_dosage_size_meas_=="МЛ":
            per_dosage_size = {str(per_dosage_size_) + "МЛ": 0, str(per_dosage_size_) + " МЛ": 0, str(per_dosage_size_ / 1000) + "Г": 0, str(per_dosage_size_ / 1000) + " Г": 0}
        elif per_dosage_size_meas_ in ["ДОЗ"]:
            per_dosage_size = {str(per_dosage_size_) + "ДОЗ": 0, str(per_dosage_size_) + " ДОЗ": 0}
        else:
            per_dosage_size = {}
        for k in per_dosage_size.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                per_dosage_size[k2] = 0
                if (".0" in k)&("0.00" not in k)&("0.01" not in k)&("0.02" not in k)&("0.03" not in k)&("0.04" not in k)&("0.05" not in k)&("0.06" not in k)&("0.07" not in k)&("0.08" not in k)&("0.09" not in k):
                    per_dosage_size[k.replace(".0", "")] = 0
            elif "nan" in k:
                del per_dosage_size[k]
        per_dosage_size_req = 1 if (row[1][18]) == 1 else 0

        volume_ = (row[1][19])
        volume_meas_ = (row[1][20])

        if volume_meas_=="МЛ":
            volume = {str(volume_) + "МЛ": 0, str(volume_) + " МЛ": 0, str(volume_ / 1000) + "Л": 0, str(volume_ / 1000) + " Л": 0}
        elif volume_meas_=="Л":
            volume = {str(volume_) + "Л": 0, str(volume_) + " Л": 0, str(round(volume_ * 1000,1)) + "МЛ": 0, str(round(volume_ * 1000,1)) + " МЛ": 0}
        elif volume_meas_ in ["Г"]:
            volume = {str(volume_) + "Г": 0, str(volume_) + " Г": 0, str(round(volume_ * 1000,1)) + "МГ": 0, str(round(volume_ * 1000,1)) + " МГ": 0}
        elif volume_meas_ in ["МГ"]:
            volume = {str(volume_/1000) + "Г": 0, str(volume_/1000) + " Г": 0, str(volume_) + "МГ": 0, str(volume_) + " МГ": 0}
        elif volume_meas_ in ["КГ","ДОЗ"]:
            volume = {str(volume_) + volume_meas_: 0, str(volume_) + " "+volume_meas_: 0}
        else:
            volume = {}
        for k in volume.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                volume[k2] = 0
                if (".0" in k)&("0.00" not in k)&("0.01" not in k)&("0.02" not in k)&("0.03" not in k)&("0.04" not in k)&("0.05" not in k)&("0.06" not in k)&("0.07" not in k)&("0.08" not in k)&("0.09" not in k):
                    volume[k.replace(".0", "")] = 0
            elif "nan" in k:
                del volume[k]
        volume_req = 1 if (row[1][21]) == 1 else 0
        try:
            quantity_ = int(row[1][22])

            quantity = {"№"+str(quantity_): 0, "№ "+str(quantity_): 0}

            for k in quantity.copy():
                if "nan" in k:
                    del quantity[k]
        except ValueError:
            quantity = {}
        quantity_req = 1 if (row[1][23]) == 1 else 0
        if type(row[1][24])!=float:
            marker_ = (row[1][24]).split(";")
            marker = {}
            for m in marker_:
                marker[m] = 0
        else:
            marker = {}
        marker_req = 1
        if type(row[1][25])!=float:
            marker_ = (row[1][25]).split(";")
            marker = {}
            for m in marker_:
                marker[m] = 0
        else:
            marker = {}


        print("=======================")
        print("PRODUCT ID",product_id)
        print("PRODUCT NAME",name, name_req)
        print("MANUFACTURER",manufacturer, manufacturer_req)
        print("DOSAGE FORM",dosage_form,dosage_form_req)
        print("DOSAGE 1",dosage_size_1, dosage_size_1_req)
        print("DOSAGE 2",dosage_size_2, dosage_size_2_req)
        print("DOSAGE 3",dosage_size_3, dosage_size_3_req)
        print("PER DOSAGE",per_dosage_size, per_dosage_size_req)
        print("VOLUME",volume, volume_req)
        print("QUANTITY",quantity, quantity_req)
        print("MARKER",marker, marker_req)

        # if product_id in [5798,"5798"]:
        #     quit()

        seed = {
            "product_id": product_id,
            "name": name,
            "name_req": name_req,
            "manufacturer": manufacturer,
            "manufacturer_req": manufacturer_req,
            "dosage_form": dosage_form,
            "dosage_form_req": dosage_form_req,
            "marker": marker,
            "marker_req": marker_req,
            "dosage_size_1": dosage_size_1,
            "dosage_size_1_req": dosage_size_1_req,
            "dosage_size_2": dosage_size_2,
            "dosage_size_2_req": dosage_size_2_req,
            "dosage_size_3": dosage_size_3,
            "dosage_size_3_req": dosage_size_3_req,
            "dosage_size_unique": {},
            "dosage_size_unique_req": 0,
            "per_dosage_size": per_dosage_size,
            "per_dosage_size_req": per_dosage_size_req,
            "volume": volume,
            "volume_req": volume_req,
            "quantity": quantity,
            "quantity_req": quantity_req

        }
        await titex.add(data=seed)
        c+=1
        # if c>1000:
        #     break

    print("OK")

    print("********** TEST COMPLETE **********")


async def import_title_dataold2():
    import pandas as pd
    pd.set_option('display.max_rows', 3000)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    data = pd.read_excel("/var/www/business/title recognition data check.xlsx")

    from warehouse.ProductsExecutorClient import ProductsExecutorClient
    pex = ProductsExecutorClient()
    from operations.TitleExecutorClient import TitleExecutorClient
    titex = TitleExecutorClient()

    print(data.head(40))

    # quit()
    c = 0
    for row in data.iterrows():
        # print(row[1][1], row[1][3],row[1][0])
        undefined = 1 if (row[1][26]) == 1 else 0

        product_id = (row[1][0])
        if undefined == 1:
            print("undefined", product_id)
            # quit()
            continue
        name_ = (row[1][2]).split(";")
        name = {}
        for n in name_:
            name[n] = 0
        name_req = 1
        manufacturer = (row[1][3])
        manufacturer_req = 1 if (row[1][4]) == 1 else 0
        dosage_form_ = (row[1][5])
        if dosage_form_ == "спрей":
            dosage_form = {"спрей": 0}
        elif dosage_form_ == "таблетки":
            dosage_form = {"табл": 0, "тб": 0, "таб": 0}
        elif dosage_form_ == "капсулы":
            dosage_form = {"капс": 0}
        elif dosage_form_ == "суспензия":
            dosage_form = {"сус": 0}
        elif dosage_form_ == "раствор":
            dosage_form = {"р-р": 0, "раст": 0, "амп": 0, "амл": 0, "д/инф": 0, "д/ инф": 0, "д / инф": 0, "д /инф": 0, "д.инф": 0, "д. инф": 0, "я инф": 0}
        elif dosage_form_ == "порошок":
            dosage_form = {"пор": 0, "пак": 0, "саш": 0, "сш": 0}
        elif dosage_form_ == "гель":
            dosage_form = {"гель": 0}
        elif dosage_form_ == "крем":
            dosage_form = {"крем": 0}
        elif dosage_form_ == "мазь":
            dosage_form = {"мазь": 0}
        elif dosage_form_ == "суппозиторий":
            dosage_form = {"супп": 0}
        elif dosage_form_ == "пастилки":
            dosage_form = {"пастил": 0}
        elif dosage_form_ == "сироп":
            dosage_form = {"сироп": 0}
        elif dosage_form_ == "капли":
            dosage_form = {"капл": 0, "гл.": 0, "г.кап.": 0}
        elif dosage_form_ == "эмульсия":
            dosage_form = {"эмул": 0}
        elif dosage_form_ == "линимент":
            dosage_form = {"линим": 0}
        else:
            dosage_form = {}
        dosage_form_req = 1 if (row[1][6]) == 1 else 0
        dosage_size_1_ = (row[1][7])
        dosage_size_1_meas_ = (row[1][8])
        print(dosage_size_1_, dosage_size_1_meas_, 1111111111111)
        if dosage_size_1_meas_ == "МГ":
            if dosage_form_ in ["таблетки", "капсулы", "суспензия", "порошок", "суппозиторий"]:
                dosage_size_1 = {str(dosage_size_1_): 0,
                                 str(dosage_size_1_ / 1000) + "Г": 0, str(dosage_size_1_ / 1000) + " Г": 0,
                                 str(round(dosage_size_1_ * 1000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_1_ * 1000, 1)) + " МКГ": 0}
            elif dosage_form_ in ["раствор", "спрей", "капли", "сироп", "мазь", "крем", "гель"]:
                dosage_size_1 = {str(dosage_size_1_ / 1000) + "Г": 0, str(dosage_size_1_ / 1000) + " Г": 0,
                                 str(dosage_size_1_): 0,
                                 str(round(dosage_size_1_ / 1000 * 100, 1)) + "%": 0,
                                 str(round(dosage_size_1_ / 1000 * 100, 1)) + " %": 0,
                                 str(round(dosage_size_1_ * 1000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_1_ * 1000, 1)) + " МКГ": 0}
            elif dosage_form_ in ["сироп", "эмульсия", "линимент"]:
                dosage_size_1 = {str(dosage_size_1_ / 1000) + "Г": 0, str(dosage_size_1_ / 1000) + " Г": 0,
                                 str(dosage_size_1_): 0,
                                 str(round(dosage_size_1_ / 1000 * 100, 1)) + "%": 0,
                                 str(round(dosage_size_1_ / 1000 * 100, 1)) + " %": 0}
            else:
                dosage_size_1 = {str(dosage_size_1_): 0,
                                 str(dosage_size_1_ / 1000) + "Г": 0, str(dosage_size_1_ / 1000) + " Г": 0,
                                 str(round(dosage_size_1_ * 1000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_1_ * 1000, 1)) + " МКГ": 0
                                 }
        elif dosage_size_1_meas_ == "Г":
            if dosage_form_ in ["таблетки", "капсулы", "суспензия", "порошок", "суппозиторий"]:
                dosage_size_1 = {str(round(dosage_size_1_ * 1000, 1)) + "МГ": 0,
                                 str(round(dosage_size_1_ * 1000, 1)) + " МГ": 0,
                                 str(dosage_size_1_): 0,
                                 str(round(dosage_size_1_ * 1000000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_1_ * 1000000, 1)) + " МКГ": 0}
            elif dosage_form_ in ["раствор", "спрей", "капли", "сироп", "мазь", "крем", "гель"]:
                dosage_size_1 = {str(dosage_size_1_): 0,
                                 str(round(dosage_size_1_ * 1000, 1)) + "МГ": 0,
                                 str(round(dosage_size_1_ * 1000, 1)) + " МГ": 0,
                                 str(round(dosage_size_1_ * 100, 1)) + "%": 0,
                                 str(round(dosage_size_1_ * 100, 1)) + " %": 0,
                                 str(round(dosage_size_1_ * 1000000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_1_ * 1000000, 1)) + " МКГ": 0}
            elif dosage_form_ in ["сироп", "эмульсия", "линимент"]:
                dosage_size_1 = {str(dosage_size_1_): 0,
                                 str(round(dosage_size_1_ * 1000, 1)) + "МГ": 0,
                                 str(round(dosage_size_1_ * 1000, 1)) + " МГ": 0,
                                 str(round(dosage_size_1_ * 100, 1)) + "%": 0,
                                 str(round(dosage_size_1_ * 100, 1)) + " %": 0}
            else:
                dosage_size_1 = {str(round(dosage_size_1_ * 1000, 1)) + "МГ": 0,
                                 str(round(dosage_size_1_ * 1000, 1)) + " МГ": 0,
                                 str(dosage_size_1_): 0,
                                 str(round(dosage_size_1_ * 1000000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_1_ * 1000000, 1)) + " МКГ": 0}
        elif dosage_size_1_meas_ == "МКГ":
            if dosage_form_ in ["таблетки", "капсулы", "суспензия", "порошок", "суппозиторий"]:
                dosage_size_1 = {str(dosage_size_1_ / 1000) + "МГ": 0, str(dosage_size_1_ / 1000) + " МГ": 0,
                                 str(dosage_size_1_ / 1000000) + "Г": 0, str(dosage_size_1_ / 1000000) + " Г": 0,
                                 str(dosage_size_1_): 0}
            elif dosage_form_ in ["раствор", "спрей", "капли", "сироп", "мазь", "крем", "гель"]:
                dosage_size_1 = {str(dosage_size_1_ / 1000000) + "Г": 0, str(dosage_size_1_ / 1000000) + " Г": 0,
                                 str(dosage_size_1_ / 1000) + "МГ": 0, str(dosage_size_1_ / 1000) + " МГ": 0,
                                 str(dosage_size_1_ / 10000) + "%": 0, str(dosage_size_1_ / 10000) + " %": 0,
                                 str(dosage_size_1_): 0}
            elif dosage_form_ in ["сироп", "эмульсия", "линимент"]:
                dosage_size_1 = {str(dosage_size_1_ / 1000000) + "Г": 0, str(dosage_size_1_ / 1000000) + " Г": 0,
                                 str(dosage_size_1_ / 1000) + "МГ": 0, str(dosage_size_1_ / 1000) + " МГ": 0,
                                 str(dosage_size_1_ / 10000) + "%": 0, str(dosage_size_1_ / 10000) + " %": 0,
                                 str(dosage_size_1_): 0}
            else:
                dosage_size_1 = {str(dosage_size_1_ / 1000) + "МГ": 0, str(dosage_size_1_ / 1000) + " МГ": 0,
                                 str(dosage_size_1_ / 1000000) + "Г": 0, str(dosage_size_1_ / 1000000) + " Г": 0,
                                 str(dosage_size_1_): 0}
        elif dosage_size_1_meas_ == "%":
            dosage_size_1 = {str(dosage_size_1_) + "%": 0, str(dosage_size_1_) + " %": 0,
                             str(round(dosage_size_1_ * 10, 1)) + "МГ": 0,
                             str(round(dosage_size_1_ * 10, 1)) + " МГ": 0, str(dosage_size_1_ / 100) + "Г": 0,
                             str(dosage_size_1_ / 100) + " Г": 0}
        elif dosage_size_1_meas_ in ["АТЕ", "ДТ", "ЕД", "ЛЕ", "МЕ", "МО"]:
            dosage_size_1 = {str(dosage_size_1_) + dosage_size_1_meas_: 0,
                             str(dosage_size_1_) + " " + dosage_size_1_meas_: 0}
        else:
            dosage_size_1 = {}

        for k in dosage_size_1.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                dosage_size_1[k2] = 0
                if (".0" in k) & ("0.00" not in k) & ("0.01" not in k) & ("0.02" not in k) & ("0.03" not in k) & (
                    "0.04" not in k) & ("0.05" not in k) & ("0.06" not in k) & ("0.07" not in k) & ("0.08" not in k) & (
                    "0.09" not in k):
                    dosage_size_1[k.replace(".0", "")] = 0
            elif "nan" in k:
                del dosage_size_1[k]
        dosage_size_1_req = 1 if (row[1][9]) == 1 else 0
        dosage_size_2_ = (row[1][10])
        dosage_size_2_meas_ = (row[1][11])

        if dosage_size_2_meas_ == "МГ":
            if dosage_form_ in ["таблетки", "капсулы", "суспензия", "порошок", "суппозиторий"]:
                dosage_size_2 = {str(dosage_size_2_): 0,
                                 str(dosage_size_2_ / 1000) + "Г": 0, str(dosage_size_2_ / 1000) + " Г": 0,
                                 str(round(dosage_size_2_ * 1000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_2_ * 1000, 1)) + " МКГ": 0}
            elif dosage_form_ in ["раствор", "спрей", "капли", "сироп", "мазь", "крем", "гель"]:
                dosage_size_2 = {str(dosage_size_2_ / 1000) + "Г": 0, str(dosage_size_2_ / 1000) + " Г": 0,
                                 str(dosage_size_2_): 0,
                                 str(round(dosage_size_2_ / 1000 * 100, 1)) + "%": 0,
                                 str(round(dosage_size_2_ / 1000 * 100, 1)) + " %": 0,
                                 str(round(dosage_size_2_ * 1000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_2_ * 1000, 1)) + " МКГ": 0}
            elif dosage_form_ in ["сироп", "эмульсия", "линимент"]:
                dosage_size_2 = {str(dosage_size_2_ / 1000) + "Г": 0, str(dosage_size_2_ / 1000) + " Г": 0,
                                 str(dosage_size_2_): 0,
                                 str(round(dosage_size_2_ / 1000 * 100, 1)) + "%": 0,
                                 str(round(dosage_size_2_ / 1000 * 100, 1)) + " %": 0}
            else:
                dosage_size_2 = {str(dosage_size_2_): 0,
                                 str(dosage_size_2_ / 1000) + "Г": 0, str(dosage_size_2_ / 1000) + " Г": 0,
                                 str(round(dosage_size_2_ * 1000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_2_ * 1000, 1)) + " МКГ": 0
                                 }
        elif dosage_size_2_meas_ == "Г":
            if dosage_form_ in ["таблетки", "капсулы", "суспензия", "порошок", "суппозиторий"]:
                dosage_size_2 = {str(round(dosage_size_2_ * 1000, 1)) + "МГ": 0,
                                 str(round(dosage_size_2_ * 1000, 1)) + " МГ": 0,
                                 str(dosage_size_2_): 0,
                                 str(round(dosage_size_2_ * 1000000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_2_ * 1000000, 1)) + " МКГ": 0}
            elif dosage_form_ in ["раствор", "спрей", "капли", "сироп", "мазь", "крем", "гель"]:
                dosage_size_2 = {str(dosage_size_2_): 0,
                                 str(round(dosage_size_2_ * 1000, 1)) + "МГ": 0,
                                 str(round(dosage_size_2_ * 1000, 1)) + " МГ": 0,
                                 str(round(dosage_size_2_ * 100, 1)) + "%": 0,
                                 str(round(dosage_size_2_ * 100, 1)) + " %": 0,
                                 str(round(dosage_size_2_ * 1000000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_2_ * 1000000, 1)) + " МКГ": 0}
            elif dosage_form_ in ["сироп", "эмульсия", "линимент"]:
                dosage_size_2 = {str(dosage_size_2_): 0,
                                 str(round(dosage_size_2_ * 1000, 1)) + "МГ": 0,
                                 str(round(dosage_size_2_ * 1000, 1)) + " МГ": 0,
                                 str(round(dosage_size_2_ * 100, 1)) + "%": 0,
                                 str(round(dosage_size_2_ * 100, 1)) + " %": 0}
            else:
                dosage_size_2 = {str(round(dosage_size_2_ * 1000, 1)) + "МГ": 0,
                                 str(round(dosage_size_2_ * 1000, 1)) + " МГ": 0,
                                 str(dosage_size_2_): 0,
                                 str(round(dosage_size_2_ * 1000000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_2_ * 1000000, 1)) + " МКГ": 0}
        elif dosage_size_2_meas_ == "МКГ":
            if dosage_form_ in ["таблетки", "капсулы", "суспензия", "порошок", "суппозиторий"]:
                dosage_size_2 = {str(dosage_size_2_ / 1000) + "МГ": 0, str(dosage_size_2_ / 1000) + " МГ": 0,
                                 str(dosage_size_2_ / 1000000) + "Г": 0, str(dosage_size_2_ / 1000000) + " Г": 0,
                                 str(dosage_size_2_): 0}
            elif dosage_form_ in ["раствор", "спрей", "капли", "сироп", "мазь", "крем", "гель"]:
                dosage_size_2 = {str(dosage_size_2_ / 1000000) + "Г": 0, str(dosage_size_2_ / 1000000) + " Г": 0,
                                 str(dosage_size_2_ / 1000) + "МГ": 0, str(dosage_size_2_ / 1000) + " МГ": 0,
                                 str(dosage_size_2_ / 10000) + "%": 0, str(dosage_size_2_ / 10000) + " %": 0,
                                 str(dosage_size_2_): 0}
            elif dosage_form_ in ["сироп", "эмульсия", "линимент"]:
                dosage_size_2 = {str(dosage_size_2_ / 1000000) + "Г": 0, str(dosage_size_2_ / 1000000) + " Г": 0,
                                 str(dosage_size_2_ / 1000) + "МГ": 0, str(dosage_size_2_ / 1000) + " МГ": 0,
                                 str(dosage_size_2_ / 10000) + "%": 0, str(dosage_size_2_ / 10000) + " %": 0,
                                 str(dosage_size_2_): 0}
            else:
                dosage_size_2 = {str(dosage_size_2_ / 1000) + "МГ": 0, str(dosage_size_2_ / 1000) + " МГ": 0,
                                 str(dosage_size_2_ / 1000000) + "Г": 0, str(dosage_size_2_ / 1000000) + " Г": 0,
                                 str(dosage_size_2_): 0}
        elif dosage_size_2_meas_ == "%":
            dosage_size_2 = {str(dosage_size_2_) + "%": 0, str(dosage_size_2_) + " %": 0,
                             str(round(dosage_size_2_ * 10, 1)) + "МГ": 0,
                             str(round(dosage_size_2_ * 10, 1)) + " МГ": 0, str(dosage_size_2_ / 100) + "Г": 0,
                             str(dosage_size_2_ / 100) + " Г": 0}
        elif dosage_size_2_meas_ in ["АТЕ", "ДТ", "ЕД", "ЛЕ", "МЕ", "МО"]:
            dosage_size_2 = {str(dosage_size_2_) + dosage_size_2_meas_: 0,
                             str(dosage_size_2_) + " " + dosage_size_2_meas_: 0}
        else:
            dosage_size_2 = {}

        for k in dosage_size_2.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                dosage_size_2[k2] = 0
                if (".0" in k) & ("0.00" not in k) & ("0.01" not in k) & ("0.02" not in k) & ("0.03" not in k) & (
                    "0.04" not in k) & ("0.05" not in k) & ("0.06" not in k) & ("0.07" not in k) & ("0.08" not in k) & (
                    "0.09" not in k):
                    dosage_size_2[k.replace(".0", "")] = 0
            elif "nan" in k:
                del dosage_size_2[k]
        dosage_size_2_req = 1 if (row[1][12]) == 1 else 0
        dosage_size_3_ = (row[1][13])
        dosage_size_3_meas_ = (row[1][14])

        if dosage_size_3_meas_ == "МГ":
            if dosage_form_ in ["таблетки", "капсулы", "суспензия", "порошок", "суппозиторий"]:
                dosage_size_3 = {str(dosage_size_3_): 0,
                                 str(dosage_size_3_ / 1000) + "Г": 0, str(dosage_size_3_ / 1000) + " Г": 0,
                                 str(round(dosage_size_3_ * 1000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_3_ * 1000, 1)) + " МКГ": 0}
            elif dosage_form_ in ["раствор", "спрей", "капли", "сироп", "мазь", "крем", "гель"]:
                dosage_size_3 = {str(dosage_size_3_ / 1000) + "Г": 0, str(dosage_size_3_ / 1000) + " Г": 0,
                                 str(dosage_size_3_): 0,
                                 str(round(dosage_size_3_ / 1000 * 100, 1)) + "%": 0,
                                 str(round(dosage_size_3_ / 1000 * 100, 1)) + " %": 0,
                                 str(round(dosage_size_3_ * 1000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_3_ * 1000, 1)) + " МКГ": 0}
            elif dosage_form_ in ["сироп", "эмульсия", "линимент"]:
                dosage_size_3 = {str(dosage_size_3_ / 1000) + "Г": 0, str(dosage_size_3_ / 1000) + " Г": 0,
                                 str(dosage_size_3_): 0,
                                 str(round(dosage_size_3_ / 1000 * 100, 1)) + "%": 0,
                                 str(round(dosage_size_3_ / 1000 * 100, 1)) + " %": 0}
            else:
                dosage_size_3 = {str(dosage_size_3_): 0,
                                 str(dosage_size_3_ / 1000) + "Г": 0, str(dosage_size_3_ / 1000) + " Г": 0,
                                 str(round(dosage_size_3_ * 1000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_3_ * 1000, 1)) + " МКГ": 0
                                 }
        elif dosage_size_3_meas_ == "Г":
            if dosage_form_ in ["таблетки", "капсулы", "суспензия", "порошок", "суппозиторий"]:
                dosage_size_3 = {str(round(dosage_size_3_ * 1000, 1)) + "МГ": 0,
                                 str(round(dosage_size_3_ * 1000, 1)) + " МГ": 0,
                                 str(dosage_size_3_): 0,
                                 str(round(dosage_size_3_ * 1000000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_3_ * 1000000, 1)) + " МКГ": 0}
            elif dosage_form_ in ["раствор", "спрей", "капли", "сироп", "мазь", "крем", "гель"]:
                dosage_size_3 = {str(dosage_size_3_): 0,
                                 str(round(dosage_size_3_ * 1000, 1)) + "МГ": 0,
                                 str(round(dosage_size_3_ * 1000, 1)) + " МГ": 0,
                                 str(round(dosage_size_3_ * 100, 1)) + "%": 0,
                                 str(round(dosage_size_3_ * 100, 1)) + " %": 0,
                                 str(round(dosage_size_3_ * 1000000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_3_ * 1000000, 1)) + " МКГ": 0}
            elif dosage_form_ in ["сироп", "эмульсия", "линимент"]:
                dosage_size_3 = {str(dosage_size_3_): 0,
                                 str(round(dosage_size_3_ * 1000, 1)) + "МГ": 0,
                                 str(round(dosage_size_3_ * 1000, 1)) + " МГ": 0,
                                 str(round(dosage_size_3_ * 100, 1)) + "%": 0,
                                 str(round(dosage_size_3_ * 100, 1)) + " %": 0}
            else:
                dosage_size_3 = {str(round(dosage_size_3_ * 1000, 1)) + "МГ": 0,
                                 str(round(dosage_size_3_ * 1000, 1)) + " МГ": 0,
                                 str(dosage_size_3_): 0,
                                 str(round(dosage_size_3_ * 1000000, 1)) + "МКГ": 0,
                                 str(round(dosage_size_3_ * 1000000, 1)) + " МКГ": 0}
        elif dosage_size_3_meas_ == "МКГ":
            if dosage_form_ in ["таблетки", "капсулы", "суспензия", "порошок", "суппозиторий"]:
                dosage_size_3 = {str(dosage_size_3_ / 1000) + "МГ": 0, str(dosage_size_3_ / 1000) + " МГ": 0,
                                 str(dosage_size_3_ / 1000000) + "Г": 0, str(dosage_size_3_ / 1000000) + " Г": 0,
                                 str(dosage_size_3_): 0}
            elif dosage_form_ in ["раствор", "спрей", "капли", "сироп", "мазь", "крем", "гель"]:
                dosage_size_3 = {str(dosage_size_3_ / 1000000) + "Г": 0, str(dosage_size_3_ / 1000000) + " Г": 0,
                                 str(dosage_size_3_ / 1000) + "МГ": 0, str(dosage_size_3_ / 1000) + " МГ": 0,
                                 str(dosage_size_3_ / 10000) + "%": 0, str(dosage_size_3_ / 10000) + " %": 0,
                                 str(dosage_size_3_): 0}
            elif dosage_form_ in ["сироп", "эмульсия", "линимент"]:
                dosage_size_3 = {str(dosage_size_3_ / 1000000) + "Г": 0, str(dosage_size_3_ / 1000000) + " Г": 0,
                                 str(dosage_size_3_ / 1000) + "МГ": 0, str(dosage_size_3_ / 1000) + " МГ": 0,
                                 str(dosage_size_3_ / 10000) + "%": 0, str(dosage_size_3_ / 10000) + " %": 0,
                                 str(dosage_size_3_): 0}
            else:
                dosage_size_3 = {str(dosage_size_3_ / 1000) + "МГ": 0, str(dosage_size_3_ / 1000) + " МГ": 0,
                                 str(dosage_size_3_ / 1000000) + "Г": 0, str(dosage_size_3_ / 1000000) + " Г": 0,
                                 str(dosage_size_3_): 0}
        elif dosage_size_3_meas_ == "%":
            dosage_size_3 = {str(dosage_size_3_) + "%": 0, str(dosage_size_3_) + " %": 0,
                             str(round(dosage_size_3_ * 10, 1)) + "МГ": 0,
                             str(round(dosage_size_3_ * 10, 1)) + " МГ": 0, str(dosage_size_3_ / 100) + "Г": 0,
                             str(dosage_size_3_ / 100) + " Г": 0}
        elif dosage_size_3_meas_ in ["АТЕ", "ДТ", "ЕД", "ЛЕ", "МЕ", "МО"]:
            dosage_size_3 = {str(dosage_size_3_) + dosage_size_3_meas_: 0,
                             str(dosage_size_3_) + " " + dosage_size_3_meas_: 0}
        else:
            dosage_size_3 = {}
        for k in dosage_size_3.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                dosage_size_3[k2] = 0
                if (".0" in k) & ("0.00" not in k) & ("0.01" not in k) & ("0.02" not in k) & ("0.03" not in k) & (
                    "0.04" not in k) & ("0.05" not in k) & ("0.06" not in k) & ("0.07" not in k) & ("0.08" not in k) & (
                    "0.09" not in k):
                    dosage_size_3[k.replace(".0", "")] = 0
            elif "nan" in k:
                del dosage_size_3[k]
        dosage_size_3_req = 1 if (row[1][15]) == 1 else 0

        per_dosage_size_ = (row[1][16])
        per_dosage_size_meas_ = (row[1][17])
        if per_dosage_size_meas_ == "МЛ":
            per_dosage_size = {str(per_dosage_size_) + "МЛ": 0, str(per_dosage_size_) + " МЛ": 0,
                               str(per_dosage_size_ / 1000) + "Л": 0, str(per_dosage_size_ / 1000) + " Л": 0}
        elif per_dosage_size_meas_ == "Г":
            per_dosage_size = {str(per_dosage_size_) + "Г": 0, str(per_dosage_size_) + " Г": 0,
                               str(round(per_dosage_size_ * 1000, 1)) + "МГ": 0,
                               str(round(per_dosage_size_ * 1000, 1)) + " МГ": 0}
        elif per_dosage_size_meas_ == "МЛ":
            per_dosage_size = {str(per_dosage_size_) + "МЛ": 0, str(per_dosage_size_) + " МЛ": 0,
                               str(per_dosage_size_ / 1000) + "Г": 0, str(per_dosage_size_ / 1000) + " Г": 0}
        elif per_dosage_size_meas_ in ["ДОЗ"]:
            per_dosage_size = {str(per_dosage_size_) + "ДОЗ": 0, str(per_dosage_size_) + " ДОЗ": 0}
        else:
            per_dosage_size = {}
        for k in per_dosage_size.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                per_dosage_size[k2] = 0
                if (".0" in k) & ("0.00" not in k) & ("0.01" not in k) & ("0.02" not in k) & ("0.03" not in k) & (
                    "0.04" not in k) & ("0.05" not in k) & ("0.06" not in k) & ("0.07" not in k) & ("0.08" not in k) & (
                    "0.09" not in k):
                    per_dosage_size[k.replace(".0", "")] = 0
            elif "nan" in k:
                del per_dosage_size[k]
        per_dosage_size_req = 1 if (row[1][18]) == 1 else 0

        volume_ = (row[1][19])
        volume_meas_ = (row[1][20])

        if volume_meas_ == "МЛ":
            volume = {str(volume_) + "МЛ": 0, str(volume_) + " МЛ": 0, str(volume_ / 1000) + "Л": 0,
                      str(volume_ / 1000) + " Л": 0}
        elif volume_meas_ == "Л":
            volume = {str(volume_) + "Л": 0, str(volume_) + " Л": 0, str(round(volume_ * 1000, 1)) + "МЛ": 0,
                      str(round(volume_ * 1000, 1)) + " МЛ": 0}
        elif volume_meas_ in ["Г"]:
            volume = {str(volume_) + "Г": 0, str(volume_) + " Г": 0, str(round(volume_ * 1000, 1)) + "МГ": 0,
                      str(round(volume_ * 1000, 1)) + " МГ": 0}
        elif volume_meas_ in ["МГ"]:
            volume = {str(volume_ / 1000) + "Г": 0, str(volume_ / 1000) + " Г": 0, str(volume_) + "МГ": 0,
                      str(volume_) + " МГ": 0}
        elif volume_meas_ in ["КГ", "ДОЗ"]:
            volume = {str(volume_) + volume_meas_: 0, str(volume_) + " " + volume_meas_: 0}
        else:
            volume = {}
        for k in volume.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                volume[k2] = 0
                if (".0" in k) & ("0.00" not in k) & ("0.01" not in k) & ("0.02" not in k) & ("0.03" not in k) & (
                    "0.04" not in k) & ("0.05" not in k) & ("0.06" not in k) & ("0.07" not in k) & ("0.08" not in k) & (
                    "0.09" not in k):
                    volume[k.replace(".0", "")] = 0
            elif "nan" in k:
                del volume[k]
        volume_req = 1 if (row[1][21]) == 1 else 0
        try:
            quantity_ = int(row[1][22])

            quantity = {"№" + str(quantity_): 0, "№ " + str(quantity_): 0}

            for k in quantity.copy():
                if "nan" in k:
                    del quantity[k]
        except ValueError:
            quantity = {}
        quantity_req = 1 if (row[1][23]) == 1 else 0
        if type(row[1][24]) != float:
            marker_ = (row[1][24]).split(";")
            marker = {}
            for m in marker_:
                marker[m] = 0
        else:
            marker = {}
        marker_req = 1 if (row[1][25]) == 1 else 0

        print("=======================")
        print("PRODUCT ID", product_id)
        print("PRODUCT NAME", name, name_req)
        print("MANUFACTURER", manufacturer, manufacturer_req)
        print("DOSAGE FORM", dosage_form, dosage_form_req)
        print("DOSAGE 1", dosage_size_1, dosage_size_1_req)
        print("DOSAGE 2", dosage_size_2, dosage_size_2_req)
        print("DOSAGE 3", dosage_size_3, dosage_size_3_req)
        print("PER DOSAGE", per_dosage_size, per_dosage_size_req)
        print("VOLUME", volume, volume_req)
        print("QUANTITY", quantity, quantity_req)
        print("MARKER", marker, marker_req)

        # if product_id in [5798,"5798"]:
        #     quit()

        seed = {
            "product_id": product_id,
            "name": name,
            "name_req": name_req,
            "manufacturer": manufacturer,
            "manufacturer_req": manufacturer_req,
            "dosage_form": dosage_form,
            "dosage_form_req": dosage_form_req,
            "marker": marker,
            "marker_req": marker_req,
            "dosage_size_1": dosage_size_1,
            "dosage_size_1_req": dosage_size_1_req,
            "dosage_size_2": dosage_size_2,
            "dosage_size_2_req": dosage_size_2_req,
            "dosage_size_3": dosage_size_3,
            "dosage_size_3_req": dosage_size_3_req,
            "dosage_size_unique": {},
            "dosage_size_unique_req": 0,
            "per_dosage_size": per_dosage_size,
            "per_dosage_size_req": per_dosage_size_req,
            "volume": volume,
            "volume_req": volume_req,
            "quantity": quantity,
            "quantity_req": quantity_req

        }
        await titex.add(data=seed)
        c += 1
        # if c>1000:
        #     break

    print("OK")

    print("********** TEST COMPLETE **********")

async def import_title_data():
    import pandas as pd
    pd.set_option('display.max_rows', 3000)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    data = pd.read_excel("/var/www/business/title recognition data check.xlsx")

    from warehouse.ProductsExecutorClient import ProductsExecutorClient
    pex = ProductsExecutorClient()
    from operations.TitleExecutorClient import TitleExecutorClient
    titex = TitleExecutorClient()

    print(data.head(40))

    # quit()
    c = 0
    for row in data.iterrows():
        # print(row[1][1], row[1][3],row[1][0])
        undefined = 1 if (row[1][26]) == 1 else 0

        product_id = (row[1][0])
        # if undefined == 1:
        #     print("undefined", product_id)
            # quit()
            # continue
        name_ = (row[1][2]).split(";")
        name = {}
        for n in name_:
            name[n] = 0
        name_req = 1
        manufacturer = (row[1][3])
        manufacturer_req = 1 if (row[1][4]) == 1 else 0
        dosage_form_ = (row[1][5])
        if dosage_form_ == "спрей":
            dosage_form = {"спрей": 0}
        elif dosage_form_ == "таблетки":
            dosage_form = {"табл": 0, "тб": 0, "таб": 0}
        elif dosage_form_ == "капсулы":
            dosage_form = {"капс": 0}
        elif dosage_form_ == "суспензия":
            dosage_form = {"сус": 0}
        elif dosage_form_ == "раствор":
            dosage_form = {"р-р": 0, "раст": 0, "амп": 0, "амл": 0, "д/инф": 0, "д/ инф": 0, "д / инф": 0, "д /инф": 0, "д.инф": 0, "д. инф": 0, "я инф": 0}
        elif dosage_form_ == "порошок":
            dosage_form = {"пор": 0, "пак": 0, "саш": 0, "сш": 0}
        elif dosage_form_ == "гель":
            dosage_form = {"гель": 0}
        elif dosage_form_ == "крем":
            dosage_form = {"крем": 0}
        elif dosage_form_ == "мазь":
            dosage_form = {"мазь": 0}
        elif dosage_form_ == "суппозиторий":
            dosage_form = {"супп": 0}
        elif dosage_form_ == "пастилки":
            dosage_form = {"пастил": 0}
        elif dosage_form_ == "сироп":
            dosage_form = {"сироп": 0}
        elif dosage_form_ == "капли":
            dosage_form = {"капл": 0, "гл.": 0, "г.кап.": 0}
        elif dosage_form_ == "эмульсия":
            dosage_form = {"эмул": 0}
        elif dosage_form_ == "линимент":
            dosage_form = {"линим": 0}
        else:
            dosage_form = {dosage_form_:0}
        dosage_form_req = 1 if (row[1][6]) == 1 else 0
        dosage_size_1_ = (row[1][7])
        dosage_size_1_meas_ = (row[1][8])
        print(dosage_size_1_, dosage_size_1_meas_, 1111111111111)
        
        
        if dosage_size_1_meas_ == "МГ":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_1 = {str(dosage_size_1_)+"МГ": 0,str(dosage_size_1_)+" МГ": 0,str(dosage_size_1_/1000)+"Г":0,str(dosage_size_1_/1000)+" Г":0, str(round(dosage_size_1_*1000,1))+"МКГ":0,str(round(dosage_size_1_*1000,1))+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_1 = {str(dosage_size_1_/1000)+"Г": 0,str(dosage_size_1_/1000)+" Г": 0,str(dosage_size_1_)+"МГ": 0,str(dosage_size_1_)+" МГ": 0,str(round(dosage_size_1_/1000*100,1))+"%":0,str(round(dosage_size_1_/1000*100,1))+" %":0,str(round(dosage_size_1_*1000,1))+"МКГ":0,str(round(dosage_size_1_*1000,1))+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_1 = {str(dosage_size_1_/1000)+"Г": 0,str(dosage_size_1_/1000)+" Г": 0,str(dosage_size_1_)+"МГ": 0,str(dosage_size_1_)+" МГ": 0,str(round(dosage_size_1_/1000*100,1))+"%":0,str(round(dosage_size_1_/1000*100,1))+" %":0}
            else:
                dosage_size_1 = {str(dosage_size_1_): 0,
                                 str(dosage_size_1_ / 1000): 0,
                                 str(round(dosage_size_1_ * 1000, 1)): 0
                                 }
        elif dosage_size_1_meas_ == "Г":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_1 = {str(round(dosage_size_1_*1000,1))+"МГ": 0,str(round(dosage_size_1_*1000,1))+" МГ": 0,str(dosage_size_1_)+"Г":0,str(dosage_size_1_)+" Г":0, str(round(dosage_size_1_*1000000,1))+"МКГ":0,str(round(dosage_size_1_*1000000,1))+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_1 = {str(dosage_size_1_)+"Г": 0,str(dosage_size_1_)+" Г": 0, str(round(dosage_size_1_*1000,1))+"МГ": 0,str(round(dosage_size_1_*1000,1))+" МГ": 0,str(round(dosage_size_1_*100,1))+"%":0,str(round(dosage_size_1_*100,1))+" %":0,str(round(dosage_size_1_*1000000,1))+"МКГ":0,str(round(dosage_size_1_*1000000,1))+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_1 = {str(dosage_size_1_)+"Г": 0,str(dosage_size_1_)+" Г": 0, str(round(dosage_size_1_*1000,1))+"МГ": 0,str(round(dosage_size_1_*1000,1))+" МГ": 0,str(round(dosage_size_1_*100,1))+"%":0,str(round(dosage_size_1_*100,1))+" %":0}
            else:
                dosage_size_1 = {str(round(dosage_size_1_ * 1000, 1)): 0,
                                 str(dosage_size_1_): 0,
                                 str(round(dosage_size_1_ * 1000000, 1)): 0}
        elif dosage_size_1_meas_ == "МКГ":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_1 = {str(dosage_size_1_/1000)+"МГ": 0,str(dosage_size_1_/1000)+" МГ": 0,str(dosage_size_1_/1000000)+"Г":0,str(dosage_size_1_/1000000)+" Г":0, str(dosage_size_1_)+"МКГ":0,str(dosage_size_1_)+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_1 = {str(dosage_size_1_/1000000)+"Г": 0,str(dosage_size_1_/1000000)+" Г": 0, str(dosage_size_1_/1000)+"МГ": 0,str(dosage_size_1_/1000)+" МГ": 0,str(dosage_size_1_/10000)+"%":0,str(dosage_size_1_/10000)+" %":0,str(dosage_size_1_)+"МКГ":0,str(dosage_size_1_)+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_1 = {str(dosage_size_1_/1000000)+"Г": 0,str(dosage_size_1_/1000000)+" Г": 0, str(dosage_size_1_/1000)+"МГ": 0,str(dosage_size_1_/1000)+" МГ": 0,str(dosage_size_1_/10000)+"%":0,str(dosage_size_1_/10000)+" %":0}
            else:
                dosage_size_1 = {str(dosage_size_1_ / 1000): 0,
                                 str(dosage_size_1_ / 1000000): 0,
                                 str(dosage_size_1_): 0}
        elif dosage_size_1_meas_ == "%":
            dosage_size_1 = {str(dosage_size_1_)+"%": 0,str(dosage_size_1_)+" %": 0,str(round(dosage_size_1_*10,1))+"МГ":0,str(round(dosage_size_1_*10,1))+" МГ":0, str(dosage_size_1_/100)+"Г":0,str(dosage_size_1_/100)+" Г":0}
        elif dosage_size_1_meas_ in ["АТЕ","ДТ","ЕД","ЛЕ","МЕ","МО"]:
            dosage_size_1 = {str(dosage_size_1_)+dosage_size_1_meas_: 0,str(dosage_size_1_)+" "+dosage_size_1_meas_: 0}
        else:
            dosage_size_1 = {}
        
        
        # if dosage_size_1_meas_ == "МГ":
        #     if dosage_form_ in ["таблетки", "капсулы", "суспензия", "порошок", "суппозиторий"]:
        #         dosage_size_1 = {str(dosage_size_1_): 0,
        #                          str(dosage_size_1_ / 1000): 0,
        #                          str(round(dosage_size_1_ * 1000, 1)): 0}
        #     elif dosage_form_ in ["раствор", "спрей", "капли", "сироп", "мазь", "крем", "гель"]:
        #         dosage_size_1 = {str(dosage_size_1_ / 1000): 0,
        #                          str(dosage_size_1_): 0,
        #                          str(round(dosage_size_1_ / 1000 * 100, 1)): 0,
        #                          str(round(dosage_size_1_ * 1000, 1)): 0}
        #     elif dosage_form_ in ["сироп", "эмульсия", "линимент"]:
        #         dosage_size_1 = {str(dosage_size_1_ / 1000): 0,
        #                          str(dosage_size_1_): 0,
        #                          str(round(dosage_size_1_ / 1000 * 100, 1)): 0}
        #     else:
        #         dosage_size_1 = {str(dosage_size_1_): 0,
        #                          str(dosage_size_1_ / 1000): 0,
        #                          str(round(dosage_size_1_ * 1000, 1)): 0
        #                          }
        # elif dosage_size_1_meas_ == "Г":
        #     if dosage_form_ in ["таблетки", "капсулы", "суспензия", "порошок", "суппозиторий"]:
        #         dosage_size_1 = {str(round(dosage_size_1_ * 1000, 1)): 0,
        #                          str(dosage_size_1_): 0,
        #                          str(round(dosage_size_1_ * 1000000, 1)): 0}
        #     elif dosage_form_ in ["раствор", "спрей", "капли", "сироп", "мазь", "крем", "гель"]:
        #         dosage_size_1 = {str(dosage_size_1_): 0,
        #                          str(round(dosage_size_1_ * 1000, 1)): 0,
        #                          str(round(dosage_size_1_ * 100, 1)): 0,
        #                          str(round(dosage_size_1_ * 1000000, 1)): 0}
        #     elif dosage_form_ in ["сироп", "эмульсия", "линимент"]:
        #         dosage_size_1 = {str(dosage_size_1_): 0,
        #                          str(round(dosage_size_1_ * 1000, 1)): 0,
        #                          str(round(dosage_size_1_ * 100, 1)): 0}
        #     else:
        #         dosage_size_1 = {str(round(dosage_size_1_ * 1000, 1)): 0,
        #                          str(dosage_size_1_): 0,
        #                          str(round(dosage_size_1_ * 1000000, 1)): 0}
        # elif dosage_size_1_meas_ == "МКГ":
        #     if dosage_form_ in ["таблетки", "капсулы", "суспензия", "порошок", "суппозиторий"]:
        #         dosage_size_1 = {str(dosage_size_1_ / 1000): 0,
        #                          str(dosage_size_1_ / 1000000): 0,
        #                          str(dosage_size_1_): 0}
        #     elif dosage_form_ in ["раствор", "спрей", "капли", "сироп", "мазь", "крем", "гель"]:
        #         dosage_size_1 = {str(dosage_size_1_ / 1000000): 0,
        #                          str(dosage_size_1_ / 1000): 0,
        #                          str(dosage_size_1_ / 10000): 0,
        #                          str(dosage_size_1_): 0}
        #     elif dosage_form_ in ["сироп", "эмульсия", "линимент"]:
        #         dosage_size_1 = {str(dosage_size_1_ / 1000000): 0,
        #                          str(dosage_size_1_ / 1000): 0, 
        #                          str(dosage_size_1_ / 10000): 0,
        #                          str(dosage_size_1_): 0}
        #     else:
        #         dosage_size_1 = {str(dosage_size_1_ / 1000): 0,
        #                          str(dosage_size_1_ / 1000000): 0,
        #                          str(dosage_size_1_): 0}
        # elif dosage_size_1_meas_ == "%":
        #     dosage_size_1 = {str(dosage_size_1_): 0, 
        #                      str(round(dosage_size_1_ * 10, 1)): 0, str(dosage_size_1_ / 100): 0}
        # elif dosage_size_1_meas_ in ["АТЕ", "ДТ", "ЕД", "ЛЕ", "МЕ", "МО"]:
        #     dosage_size_1 = {str(dosage_size_1_) + dosage_size_1_meas_: 0,
        #                      str(dosage_size_1_) + " " + dosage_size_1_meas_: 0}
        # else:
        #     dosage_size_1 = {}

        for k in dosage_size_1.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                dosage_size_1[k2] = 0
                if (".0" in k) & ("0.00" not in k) & ("0.01" not in k) & ("0.02" not in k) & ("0.03" not in k) & (
                    "0.04" not in k) & ("0.05" not in k) & ("0.06" not in k) & ("0.07" not in k) & ("0.08" not in k) & (
                    "0.09" not in k):
                    dosage_size_1[k.replace(".0", "")] = 0
            elif "nan" in k:
                del dosage_size_1[k]
        dosage_size_1_req = 1 if (row[1][9]) == 1 else 0
        dosage_size_2_ = (row[1][10])
        dosage_size_2_meas_ = (row[1][11])

        if dosage_size_2_meas_ == "МГ":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_2 = {str(dosage_size_2_)+"МГ": 0,str(dosage_size_2_)+" МГ": 0,str(dosage_size_2_/1000)+"Г":0,str(dosage_size_2_/1000)+" Г":0, str(round(dosage_size_2_*1000,1))+"МКГ":0,str(round(dosage_size_2_*1000,1))+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_2 = {str(dosage_size_2_/1000)+"Г": 0,str(dosage_size_2_/1000)+" Г": 0,str(dosage_size_2_)+"МГ": 0,str(dosage_size_2_)+" МГ": 0,str(round(dosage_size_2_/1000*100,1))+"%":0,str(round(dosage_size_2_/1000*100,1))+" %":0,str(round(dosage_size_2_*1000,1))+"МКГ":0,str(round(dosage_size_2_*1000,1))+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_2 = {str(dosage_size_2_/1000)+"Г": 0,str(dosage_size_2_/1000)+" Г": 0,str(dosage_size_2_)+"МГ": 0,str(dosage_size_2_)+" МГ": 0,str(round(dosage_size_2_/1000*100,1))+"%":0,str(round(dosage_size_2_/1000*100,1))+" %":0}
            else:
                dosage_size_2 = {str(dosage_size_2_): 0,
                                 str(dosage_size_2_ / 1000): 0,
                                 str(round(dosage_size_2_ * 1000, 1)): 0
                                 }
        elif dosage_size_2_meas_ == "Г":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_2 = {str(round(dosage_size_2_*1000,1))+"МГ": 0,str(round(dosage_size_2_*1000,1))+" МГ": 0,str(dosage_size_2_)+"Г":0,str(dosage_size_2_)+" Г":0, str(round(dosage_size_2_*1000000,1))+"МКГ":0,str(round(dosage_size_2_*1000000,1))+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_2 = {str(dosage_size_2_)+"Г": 0,str(dosage_size_2_)+" Г": 0, str(round(dosage_size_2_*1000,1))+"МГ": 0,str(round(dosage_size_2_*1000,1))+" МГ": 0,str(round(dosage_size_2_*100,1))+"%":0,str(round(dosage_size_2_*100,1))+" %":0,str(round(dosage_size_2_*1000000,1))+"МКГ":0,str(round(dosage_size_2_*1000000,1))+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_2 = {str(dosage_size_2_)+"Г": 0,str(dosage_size_2_)+" Г": 0, str(round(dosage_size_2_*1000,1))+"МГ": 0,str(round(dosage_size_2_*1000,1))+" МГ": 0,str(round(dosage_size_2_*100,1))+"%":0,str(round(dosage_size_2_*100,1))+" %":0}
            else:
                dosage_size_2 = {str(round(dosage_size_2_ * 1000, 1)): 0,
                                 str(dosage_size_2_): 0,
                                 str(round(dosage_size_2_ * 1000000, 1)): 0}
        elif dosage_size_2_meas_ == "МКГ":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_2 = {str(dosage_size_2_/1000)+"МГ": 0,str(dosage_size_2_/1000)+" МГ": 0,str(dosage_size_2_/1000000)+"Г":0,str(dosage_size_2_/1000000)+" Г":0, str(dosage_size_2_)+"МКГ":0,str(dosage_size_2_)+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_2 = {str(dosage_size_2_/1000000)+"Г": 0,str(dosage_size_2_/1000000)+" Г": 0, str(dosage_size_2_/1000)+"МГ": 0,str(dosage_size_2_/1000)+" МГ": 0,str(dosage_size_2_/10000)+"%":0,str(dosage_size_2_/10000)+" %":0,str(dosage_size_2_)+"МКГ":0,str(dosage_size_2_)+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_2 = {str(dosage_size_2_/1000000)+"Г": 0,str(dosage_size_2_/1000000)+" Г": 0, str(dosage_size_2_/1000)+"МГ": 0,str(dosage_size_2_/1000)+" МГ": 0,str(dosage_size_2_/10000)+"%":0,str(dosage_size_2_/10000)+" %":0}
            else:
                dosage_size_2 = {str(dosage_size_2_ / 1000): 0,
                                 str(dosage_size_2_ / 1000000): 0,
                                 str(dosage_size_2_): 0}
        elif dosage_size_2_meas_ == "%":
            dosage_size_2 = {str(dosage_size_2_)+"%": 0,str(dosage_size_2_)+" %": 0,str(round(dosage_size_2_*10,1))+"МГ":0,str(round(dosage_size_2_*10,1))+" МГ":0, str(dosage_size_2_/100)+"Г":0,str(dosage_size_2_/100)+" Г":0}
        elif dosage_size_2_meas_ in ["АТЕ","ДТ","ЕД","ЛЕ","МЕ","МО"]:
            dosage_size_2 = {str(dosage_size_2_)+dosage_size_2_meas_: 0,str(dosage_size_2_)+" "+dosage_size_2_meas_: 0}
        else:
            dosage_size_2 = {}
        for k in dosage_size_2.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                dosage_size_2[k2] = 0
                if (".0" in k) & ("0.00" not in k) & ("0.01" not in k) & ("0.02" not in k) & ("0.03" not in k) & (
                    "0.04" not in k) & ("0.05" not in k) & ("0.06" not in k) & ("0.07" not in k) & ("0.08" not in k) & (
                    "0.09" not in k):
                    dosage_size_2[k.replace(".0", "")] = 0
            elif "nan" in k:
                del dosage_size_2[k]
        dosage_size_2_req = 1 if (row[1][12]) == 1 else 0
        dosage_size_3_ = (row[1][13])
        dosage_size_3_meas_ = (row[1][14])

        if dosage_size_3_meas_ == "МГ":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_3 = {str(dosage_size_3_)+"МГ": 0,str(dosage_size_3_)+" МГ": 0,str(dosage_size_3_/1000)+"Г":0,str(dosage_size_3_/1000)+" Г":0, str(round(dosage_size_3_*1000,1))+"МКГ":0,str(round(dosage_size_3_*1000,1))+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_3 = {str(dosage_size_3_/1000)+"Г": 0,str(dosage_size_3_/1000)+" Г": 0,str(dosage_size_3_)+"МГ": 0,str(dosage_size_3_)+" МГ": 0,str(round(dosage_size_3_/1000*100,1))+"%":0,str(round(dosage_size_3_/1000*100,1))+" %":0,str(round(dosage_size_3_*1000,1))+"МКГ":0,str(round(dosage_size_3_*1000,1))+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_3 = {str(dosage_size_3_/1000)+"Г": 0,str(dosage_size_3_/1000)+" Г": 0,str(dosage_size_3_)+"МГ": 0,str(dosage_size_3_)+" МГ": 0,str(round(dosage_size_3_/1000*100,1))+"%":0,str(round(dosage_size_3_/1000*100,1))+" %":0}
            else:
                dosage_size_3 = {str(dosage_size_3_): 0,
                                 str(dosage_size_3_ / 1000): 0,
                                 str(round(dosage_size_3_ * 1000, 1)): 0
                                 }
        elif dosage_size_3_meas_ == "Г":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_3 = {str(round(dosage_size_3_*1000,1))+"МГ": 0,str(round(dosage_size_3_*1000,1))+" МГ": 0,str(dosage_size_3_)+"Г":0,str(dosage_size_3_)+" Г":0, str(round(dosage_size_3_*1000000,1))+"МКГ":0,str(round(dosage_size_3_*1000000,1))+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_3 = {str(dosage_size_3_)+"Г": 0,str(dosage_size_3_)+" Г": 0, str(round(dosage_size_3_*1000,1))+"МГ": 0,str(round(dosage_size_3_*1000,1))+" МГ": 0,str(round(dosage_size_3_*100,1))+"%":0,str(round(dosage_size_3_*100,1))+" %":0,str(round(dosage_size_3_*1000000,1))+"МКГ":0,str(round(dosage_size_3_*1000000,1))+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_3 = {str(dosage_size_3_)+"Г": 0,str(dosage_size_3_)+" Г": 0, str(round(dosage_size_3_*1000,1))+"МГ": 0,str(round(dosage_size_3_*1000,1))+" МГ": 0,str(round(dosage_size_3_*100,1))+"%":0,str(round(dosage_size_3_*100,1))+" %":0}
            else:
                dosage_size_3 = {str(round(dosage_size_3_ * 1000, 1)): 0,
                                 str(dosage_size_3_): 0,
                                 str(round(dosage_size_3_ * 1000000, 1)): 0}
        elif dosage_size_3_meas_ == "МКГ":
            if dosage_form_ in ["таблетки","капсулы","суспензия","порошок","суппозиторий"]:
                dosage_size_3 = {str(dosage_size_3_/1000)+"МГ": 0,str(dosage_size_3_/1000)+" МГ": 0,str(dosage_size_3_/1000000)+"Г":0,str(dosage_size_3_/1000000)+" Г":0, str(dosage_size_3_)+"МКГ":0,str(dosage_size_3_)+" МКГ":0}
            elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
                dosage_size_3 = {str(dosage_size_3_/1000000)+"Г": 0,str(dosage_size_3_/1000000)+" Г": 0, str(dosage_size_3_/1000)+"МГ": 0,str(dosage_size_3_/1000)+" МГ": 0,str(dosage_size_3_/10000)+"%":0,str(dosage_size_3_/10000)+" %":0,str(dosage_size_3_)+"МКГ":0,str(dosage_size_3_)+" МКГ":0}
            elif dosage_form_ in ["сироп","эмульсия","линимент"]:
                dosage_size_3 = {str(dosage_size_3_/1000000)+"Г": 0,str(dosage_size_3_/1000000)+" Г": 0, str(dosage_size_3_/1000)+"МГ": 0,str(dosage_size_3_/1000)+" МГ": 0,str(dosage_size_3_/10000)+"%":0,str(dosage_size_3_/10000)+" %":0}
            else:
                dosage_size_3 = {str(dosage_size_3_ / 1000): 0,
                                 str(dosage_size_3_ / 1000000): 0,
                                 str(dosage_size_3_): 0}
        elif dosage_size_3_meas_ == "%":
            dosage_size_3 = {str(dosage_size_3_)+"%": 0,str(dosage_size_3_)+" %": 0,str(round(dosage_size_3_*10,1))+"МГ":0,str(round(dosage_size_3_*10,1))+" МГ":0, str(dosage_size_3_/100)+"Г":0,str(dosage_size_3_/100)+" Г":0}
        elif dosage_size_3_meas_ in ["АТЕ","ДТ","ЕД","ЛЕ","МЕ","МО"]:
            dosage_size_3 = {str(dosage_size_3_)+dosage_size_3_meas_: 0,str(dosage_size_3_)+" "+dosage_size_3_meas_: 0}
        else:
            dosage_size_3 = {}
        for k in dosage_size_3.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                dosage_size_3[k2] = 0
                if (".0" in k) & ("0.00" not in k) & ("0.01" not in k) & ("0.02" not in k) & ("0.03" not in k) & (
                    "0.04" not in k) & ("0.05" not in k) & ("0.06" not in k) & ("0.07" not in k) & ("0.08" not in k) & (
                    "0.09" not in k):
                    dosage_size_3[k.replace(".0", "")] = 0
            elif "nan" in k:
                del dosage_size_3[k]
        dosage_size_3_req = 1 if (row[1][15]) == 1 else 0

        per_dosage_size_ = (row[1][16])
        per_dosage_size_meas_ = (row[1][17])
        if per_dosage_size_meas_ == "МЛ":
            per_dosage_size = {str(per_dosage_size_) + "МЛ": 0, str(per_dosage_size_) + " МЛ": 0,
                               str(per_dosage_size_ / 1000) + "Л": 0, str(per_dosage_size_ / 1000) + " Л": 0}
        elif per_dosage_size_meas_ == "Г":
            per_dosage_size = {str(per_dosage_size_) + "Г": 0, str(per_dosage_size_) + " Г": 0,
                               str(round(per_dosage_size_ * 1000, 1)) + "МГ": 0,
                               str(round(per_dosage_size_ * 1000, 1)) + " МГ": 0}
        elif per_dosage_size_meas_ == "МЛ":
            per_dosage_size = {str(per_dosage_size_) + "МЛ": 0, str(per_dosage_size_) + " МЛ": 0,
                               str(per_dosage_size_ / 1000) + "Г": 0, str(per_dosage_size_ / 1000) + " Г": 0}
        elif per_dosage_size_meas_ in ["ДОЗ"]:
            per_dosage_size = {str(per_dosage_size_) + "ДОЗ": 0, str(per_dosage_size_) + " ДОЗ": 0}
        else:
            per_dosage_size = {}
        for k in per_dosage_size.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                per_dosage_size[k2] = 0
                if (".0" in k) & ("0.00" not in k) & ("0.01" not in k) & ("0.02" not in k) & ("0.03" not in k) & (
                    "0.04" not in k) & ("0.05" not in k) & ("0.06" not in k) & ("0.07" not in k) & ("0.08" not in k) & (
                    "0.09" not in k):
                    per_dosage_size[k.replace(".0", "")] = 0
            elif "nan" in k:
                del per_dosage_size[k]
        per_dosage_size_req = 1 if (row[1][18]) == 1 else 0

        volume_ = (row[1][19])
        volume_meas_ = (row[1][20])

        if volume_meas_ == "МЛ":
            volume = {str(volume_) + "МЛ": 0, str(volume_) + " МЛ": 0, str(volume_ / 1000) + "Л": 0,
                      str(volume_ / 1000) + " Л": 0}
        elif volume_meas_ == "Л":
            volume = {str(volume_) + "Л": 0, str(volume_) + " Л": 0, str(round(volume_ * 1000, 1)) + "МЛ": 0,
                      str(round(volume_ * 1000, 1)) + " МЛ": 0}
        elif volume_meas_ in ["Г"]:
            volume = {str(volume_) + "Г": 0, str(volume_) + " Г": 0, str(round(volume_ * 1000, 1)) + "МГ": 0,
                      str(round(volume_ * 1000, 1)) + " МГ": 0}
        elif volume_meas_ in ["МГ"]:
            volume = {str(volume_ / 1000) + "Г": 0, str(volume_ / 1000) + " Г": 0, str(volume_) + "МГ": 0,
                      str(volume_) + " МГ": 0}
        elif volume_meas_ in ["КГ", "ДОЗ"]:
            volume = {str(volume_) + volume_meas_: 0, str(volume_) + " " + volume_meas_: 0}
        else:
            volume = {}
        for k in volume.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                volume[k2] = 0
                if (".0" in k) & ("0.00" not in k) & ("0.01" not in k) & ("0.02" not in k) & ("0.03" not in k) & (
                    "0.04" not in k) & ("0.05" not in k) & ("0.06" not in k) & ("0.07" not in k) & ("0.08" not in k) & (
                    "0.09" not in k):
                    volume[k.replace(".0", "")] = 0
            elif "nan" in k:
                del volume[k]
        volume_req = 1 if (row[1][21]) == 1 else 0
        try:
            quantity_ = int(row[1][22])

            quantity = {"№" + str(quantity_): 0, "№ " + str(quantity_): 0}

            for k in quantity.copy():
                if "nan" in k:
                    del quantity[k]
        except ValueError:
            quantity = {}
        quantity_req = 1 if (row[1][23]) == 1 else 0
        if type(row[1][24]) != float:
            marker_ = (row[1][24]).split(";")
            marker = {}
            for m in marker_:
                marker[m] = 0
        else:
            marker = {}
        marker_req = 1

        if type(row[1][25]) != float:
            marker2_ = (row[1][25]).split(";")
            marker2 = {}
            for m in marker2_:
                marker2[m] = 0
        else:
            marker2 = {}

        print("=======================")
        print("PRODUCT ID", product_id)
        print("PRODUCT NAME", name, name_req)
        print("MANUFACTURER", manufacturer, manufacturer_req)
        print("DOSAGE FORM", dosage_form, dosage_form_req)
        print("DOSAGE 1", dosage_size_1, dosage_size_1_req)
        print("DOSAGE 2", dosage_size_2, dosage_size_2_req)
        print("DOSAGE 3", dosage_size_3, dosage_size_3_req)
        print("PER DOSAGE", per_dosage_size, per_dosage_size_req)
        print("VOLUME", volume, volume_req)
        print("QUANTITY", quantity, quantity_req)
        print("MARKER", marker, marker_req)

        # if product_id in [5798,"5798"]:
        #     quit()

        seed = {
            "product_id": product_id,
            "name": name,
            "name_req": name_req,
            "manufacturer": manufacturer,
            "manufacturer_req": manufacturer_req,
            "dosage_form": dosage_form,
            "dosage_form_req": dosage_form_req,
            "marker": marker,
            "marker_req": marker_req,
            "marker2": marker2,
            "dosage_size_1": dosage_size_1,
            "dosage_size_1_req": dosage_size_1_req,
            "dosage_size_2": dosage_size_2,
            "dosage_size_2_req": dosage_size_2_req,
            "dosage_size_3": dosage_size_3,
            "dosage_size_3_req": dosage_size_3_req,
            "dosage_size_unique": {},
            "dosage_size_unique_req": 0,
            "per_dosage_size": per_dosage_size,
            "per_dosage_size_req": per_dosage_size_req,
            "volume": volume,
            "volume_req": volume_req,
            "quantity": quantity,
            "quantity_req": quantity_req

        }
        await titex.add(data=seed)
        c += 1
        # if c>1000:
        #     break

    print("OK")

    print("********** TEST COMPLETE **********")


async def create_title_logic():
    import pandas as pd
    pd.set_option('display.max_rows', 3000)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    data = pd.read_excel("/var/www/business/title recognition data check.xlsx")

    from warehouse.ProductsExecutorClient import ProductsExecutorClient
    pex = ProductsExecutorClient()
    from operations.TitleExecutorClient import TitleExecutorClient
    titex = TitleExecutorClient()

    print(data.head(20))

    import numpy as np
    import math
    print(np.unique(data.name))
    c=0
    products = {}
    for i in np.unique(data.name):
        manufacturer_req=0
        dosage_form_req=0
        # if i !="ВИТАПРОСТ":
        #     continue
        print(i)
        if i in ["ТРУБКА ЭНДОТРАХЕАЛЬНАЯ","ШАМПУНЬ АНТИПЕДИКУЛЕЗНЫЙ","ЛЕНТА ЭЛАСТИЧНАЯ","МАРЛЯ"]:
            continue
        name_df=(data[data["name"]==i])
        products_ = np.unique(name_df.product_id)
        if len(products_)>40:
            print(i," MANY", len(products_))
            continue
        # continue
        for p in products_:
            products[str(p)] = {"product_id":p,"manufacturer_req":0,"dosage_form_req":0,"dosage_size_1_req":0,"dosage_size_2_req":0,"dosage_size_3_req":0,"volume_req":0,"quantity_req":0,"undefined":0}
        name_df2=name_df
        if len(name_df2)>1:
            manufacturer=np.unique(name_df2.manufacturer)
            if len(manufacturer)>1:
                # for row in name_df2.iterrows():
                #     if not math.isnan(row[1]["manufacturer"]):
                #         products[str(row[1]["product_id"])]["manufacturer_req"] = 1
                for p in np.unique(name_df2.product_id):
                    products[str(p)]["manufacturer_req"]=1
            for m in manufacturer:
                manu_df = name_df2[name_df2["manufacturer"]==m]
                if len(manu_df)>1:
                    dosage_form = np.unique(manu_df["dosage form"])
                    if len(dosage_form)>1:
                        # print(manu_df)
                        for row in manu_df.iterrows():
                            if type(row[1]["dosage form"])!=str:
                                if not math.isnan(row[1]["dosage form"]):
                                    products[str(row[1]["product_id"])]["dosage_form_req"] = 1
                            else:
                                    products[str(row[1]["product_id"])]["dosage_form_req"] = 1
                    for d in dosage_form:
                        dosage_form_df = manu_df[manu_df["dosage form"]==d]
                        if type(d)!=str:
                            if math.isnan(d):
                                dosage_form_df = manu_df[pd.isnull(manu_df["dosage form"])]
                        if len(dosage_form_df)>1:
                            quantity = np.unique(dosage_form_df["dosage quantity"])
                            if len(quantity)>1:
                                for row in dosage_form_df.iterrows():
                                    if type(row[1]["dosage quantity"])!=str:
                                        if not math.isnan(row[1]["dosage quantity"]):
                                            products[str(row[1]["product_id"])]["quantity_req"] = 1
                                    else:
                                        products[str(row[1]["product_id"])]["quantity_req"] = 1
                            for q in quantity:
                                quantity_df = dosage_form_df[dosage_form_df["dosage quantity"]==q]
                                if type(q) != str:
                                    if math.isnan(q):
                                        quantity_df = dosage_form_df[pd.isnull(dosage_form_df["dosage quantity"])]
                                if len(quantity_df)>1:
                                    dosage_size_1 = np.unique(quantity_df["dosage \nsize_1"])
                                    if len(dosage_size_1)>1:
                                        for row in quantity_df.iterrows():
                                            if type(row[1]["dosage \nsize_1"])!=str:
                                                if not math.isnan(row[1]["dosage \nsize_1"]):
                                                    products[str(row[1]["product_id"])]["dosage_size_1_req"] = 1
                                            else:
                                                products[str(row[1]["product_id"])]["dosage_size_1_req"] = 1
                                    for s1 in dosage_size_1:
                                        dosage_size_1_df = quantity_df[quantity_df["dosage \nsize_1"]==s1]
                                        if type(s1) != str:
                                            if math.isnan(s1):
                                                dosage_size_1_df = quantity_df[pd.isnull(quantity_df["dosage \nsize_1"])]
                                        if len(dosage_size_1_df)>1:
                                            volume = np.unique(dosage_size_1_df["content dosage size"])
                                            if len(volume)>1:
                                                # print(11111)
                                                for row in dosage_size_1_df.iterrows():
                                                    if type(row[1]["content dosage size"])!=str:
                                                        if not math.isnan(row[1]["content dosage size"]):
                                                            products[str(row[1]["product_id"])]["volume_req"] = 1
                                                    else:
                                                        products[str(row[1]["product_id"])]["volume_req"] = 1
                                            for v in volume:
                                                volume_df = dosage_size_1_df[dosage_size_1_df["content dosage size"]==v]
                                                if type(v) != str:
                                                    if math.isnan(v):
                                                        volume_df = dosage_size_1_df[pd.isnull(dosage_size_1_df["content dosage size"])]
                                                if len(volume_df)>1:
                                                    dosage_size_2 = np.unique(dosage_size_1_df["dosage size2"])
                                                    if len(dosage_size_2) > 1:
                                                        for row in volume_df.iterrows():
                                                            if type(row[1]["dosage size2"])!=str:
                                                                if not math.isnan(row[1]["dosage size2"]):
                                                                    products[str(row[1]["product_id"])]["dosage_size_2_req"] = 1
                                                            else:
                                                                products[str(row[1]["product_id"])]["dosage_size_2_req"] = 1
                                                    for s2 in dosage_size_2:
                                                        dosage_size_2_df = volume_df[volume_df["dosage size2"] == s2]
                                                        if type(s2) != str:
                                                            if math.isnan(s2):
                                                                dosage_size_2_df = volume_df[pd.isnull(volume_df["dosage size2"])]
                                                        if len(dosage_size_2_df) > 1:
                                                            for row in dosage_size_2_df.iterrows():
                                                                products[str(row[1]["product_id"])]["undefined"] = 1
        # for row in name_df.iterrows():
        #     print(str(row[1]["product_id"]),row[1]["product_name"][:20],products[str(row[1]["product_id"])])
        #


        c+=1
        if c==5:
            pass
            # quit()
    df = pd.DataFrame(
        columns=["product_id", "manufacturer_req", "dosage_form_req", "dosage_size_1_req", "dosage_size_2_req",
                 "dosage_size_3_req", "volume_req", "undefined"])
    for p in products:
        print("PPP",products[p])
        df = df.append(products[p], ignore_index=True)
    writer = pd.ExcelWriter('/var/www/business/title_logic.xlsx')
    df.to_excel(writer, "Sheet1")
    writer.save()
    # print(df)
    quit()
    c=0
    for row in data.iterrows():
        # print(row[1][1], row[1][3],row[1][0])
        product_id = (row[1][0])
        name_ = (row[1][2]).split(";")
        name = {}
        for n in name_:
            name[n]=0
        name_req=1
        manufacturer_ = (row[1][3]).split(";")
        manufacturer = {}
        for m in manufacturer_:
            manufacturer[m]=0
        manufacturer_req = 1 if (row[1][4])==1 else 0
        dosage_form_ = (row[1][5])
        if dosage_form_=="спрей":
            dosage_form = {"спрей":0}
        elif dosage_form_=="таблетки":
            dosage_form = {"табл":0,"тб":0,"таб":0}
        elif dosage_form_=="капсулы":
            dosage_form = {"капс":0}
        elif dosage_form_=="суспензия":
            dosage_form = {"сус":0}
        elif dosage_form_=="раствор":
            dosage_form = {"р-р":0,"раст":0,"амп":0,"амл":0,"д/инф":0,"д/ инф":0,"д / инф":0,"д /инф":0,"д.инф":0,"д. инф":0,"я инф":0}
        elif dosage_form_=="порошок":
            dosage_form = {"пор":0,"пак":0,"саш":0,"сш":0}
        elif dosage_form_=="гель":
            dosage_form = {"гель":0}
        elif dosage_form_=="крем":
            dosage_form = {"крем":0}
        elif dosage_form_ == "мазь":
            dosage_form = {"мазь": 0}
        elif dosage_form_ == "суппозиторий":
            dosage_form = {"супп": 0}
        elif dosage_form_ == "пастилки":
            dosage_form = {"пастил": 0}
        elif dosage_form_ == "сироп":
            dosage_form = {"сироп": 0}
        elif dosage_form_ == "капли":
            dosage_form = {"капл": 0,"гл.":0,"г.кап.":0}
        elif dosage_form_ == "эмульсия":
            dosage_form = {"эмул": 0}
        elif dosage_form_ == "линимент":
            dosage_form = {"линим": 0}
        else:
            dosage_form = {}
        dosage_form_req = 1 if (row[1][6]) == 1 else 0
        dosage_size_1_ = (row[1][7])
        if dosage_form_ in ["таблетка","капсулы","суспензия","порошок","суппозиторий"]:
            dosage_size_1 = {str(dosage_size_1_)+"МГ": 0,str(dosage_size_1_)+" МГ": 0,str(dosage_size_1_/1000)+"Г":0,str(dosage_size_1_/1000)+" Г":0}
        elif dosage_form_ in ["раствор","спрей","капли","сироп","мазь","крем","гель"]:
            dosage_size_1 = {str(dosage_size_1_)+"МГ": 0,str(dosage_size_1_)+" МГ": 0,str(dosage_size_1_/1000*100)+"%":0,str(dosage_size_1_/1000*100)+" %":0,str(dosage_size_1_*1000)+"МКГ":0,str(dosage_size_1_*1000)+" МКГ":0}
        elif dosage_form_ in ["сироп","эмульсия","линимент"]:
            dosage_size_1 = {str(dosage_size_1_)+"МГ": 0,str(dosage_size_1_)+" МГ": 0,str(dosage_size_1_/1000*100)+"%":0,str(dosage_size_1_/1000*100)+" %":0}
        else:
            dosage_size_1 = {}
        for k in dosage_size_1.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                dosage_size_1[k2] = 0
                if (".0" in k)&("0.00" not in k)&("0.01" not in k)&("0.02" not in k)&("0.03" not in k)&("0.04" not in k)&("0.05" not in k)&("0.06" not in k)&("0.07" not in k)&("0.08" not in k)&("0.09" not in k):
                    dosage_size_1[k.replace(".0","")] = 0
            elif "nan" in k:
                del dosage_size_1[k]
        dosage_size_1_req = 1 if (row[1][9]) == 1 else 0
        dosage_size_2_ = (row[1][10])
        if dosage_form_ in ["таблетка", "капсулы", "суспензия", "порошок", "суппозиторий"]:
            dosage_size_2 = {str(dosage_size_2_) + "МГ": 0, str(dosage_size_2_) + " МГ": 0,
                             str(dosage_size_2_ / 1000) + "Г": 0, str(dosage_size_2_ / 1000) + " Г": 0}
        elif dosage_form_ in ["раствор", "спрей", "капли", "сироп", "мазь", "крем", "гель"]:
            dosage_size_2 = {str(dosage_size_2_) + "МГ": 0, str(dosage_size_2_) + " МГ": 0,
                             str(dosage_size_2_ / 1000 * 100) + "%": 0, str(dosage_size_2_ / 1000 * 100) + " %": 0,
                             str(dosage_size_2_ * 1000) + "МКГ": 0, str(dosage_size_2_ * 1000) + " МКГ": 0}
        elif dosage_form_ in ["сироп", "эмульсия", "линимент"]:
            dosage_size_2 = {str(dosage_size_2_) + "МГ": 0, str(dosage_size_2_) + " МГ": 0,
                             str(dosage_size_2_ / 1000 * 100) + "%": 0, str(dosage_size_2_ / 1000 * 100) + " %": 0}
        else:
            dosage_size_2 = {}
        for k in dosage_size_2.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                dosage_size_2[k2] = 0
                if (".0" in k)&("0.00" not in k)&("0.01" not in k)&("0.02" not in k)&("0.03" not in k)&("0.04" not in k)&("0.05" not in k)&("0.06" not in k)&("0.07" not in k)&("0.08" not in k)&("0.09" not in k):
                    dosage_size_2[k.replace(".0", "")] = 0
            elif "nan" in k:
                del dosage_size_2[k]
        dosage_size_2_req = 1 if (row[1][12]) == 1 else 0
        dosage_size_3_ = (row[1][13])
        if dosage_form_ in ["таблетка", "капсулы", "суспензия", "порошок", "суппозиторий"]:
            dosage_size_3 = {str(dosage_size_3_) + "МГ": 0, str(dosage_size_3_) + " МГ": 0,
                             str(dosage_size_3_ / 1000) + "Г": 0, str(dosage_size_3_ / 1000) + " Г": 0}
        elif dosage_form_ in ["раствор", "спрей", "капли", "сироп", "мазь", "крем", "гель"]:
            dosage_size_3 = {str(dosage_size_3_) + "МГ": 0, str(dosage_size_3_) + " МГ": 0,
                             str(dosage_size_3_ / 1000 * 100) + "%": 0, str(dosage_size_3_ / 1000 * 100) + " %": 0,
                             str(dosage_size_3_ * 1000) + "МКГ": 0, str(dosage_size_3_ * 1000) + " МКГ": 0}
        elif dosage_form_ in ["сироп", "эмульсия", "линимент"]:
            dosage_size_3 = {str(dosage_size_3_) + "МГ": 0, str(dosage_size_3_) + " МГ": 0,
                             str(dosage_size_3_ / 1000 * 100) + "%": 0, str(dosage_size_3_ / 1000 * 100) + " %": 0}
        else:
            dosage_size_3 = {}
        for k in dosage_size_3.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                dosage_size_3[k2] = 0
                if (".0" in k)&("0.00" not in k)&("0.01" not in k)&("0.02" not in k)&("0.03" not in k)&("0.04" not in k)&("0.05" not in k)&("0.06" not in k)&("0.07" not in k)&("0.08" not in k)&("0.09" not in k):
                    dosage_size_3[k.replace(".0", "")] = 0
            elif "nan" in k:
                del dosage_size_3[k]
        dosage_size_3_req = 1 if (row[1][15]) == 1 else 0

        per_dosage_size_ = (row[1][16])
        per_dosage_size = {str(per_dosage_size_) + "МЛ": 0, str(per_dosage_size_) + " МЛ": 0, str(per_dosage_size_ / 1000) + "Л": 0, str(per_dosage_size_ / 1000) + " Л": 0}
        for k in per_dosage_size.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                per_dosage_size[k2] = 0
                if (".0" in k)&("0.00" not in k)&("0.01" not in k)&("0.02" not in k)&("0.03" not in k)&("0.04" not in k)&("0.05" not in k)&("0.06" not in k)&("0.07" not in k)&("0.08" not in k)&("0.09" not in k):
                    per_dosage_size[k.replace(".0", "")] = 0
            elif "nan" in k:
                del per_dosage_size[k]
        per_dosage_size_req = 1 if (row[1][18]) == 1 else 0

        volume_ = (row[1][19])
        volume = {str(volume_) + "МЛ": 0, str(volume_) + " МЛ": 0,
                           str(volume_ / 1000) + "Л": 0, str(volume_ / 1000) + " Л": 0}
        for k in volume.copy():
            if "." in k:
                k2 = k.replace(".", ",", 100)
                volume[k2] = 0
                if (".0" in k)&("0.00" not in k)&("0.01" not in k)&("0.02" not in k)&("0.03" not in k)&("0.04" not in k)&("0.05" not in k)&("0.06" not in k)&("0.07" not in k)&("0.08" not in k)&("0.09" not in k):
                    volume[k.replace(".0", "")] = 0
            elif "nan" in k:
                del volume[k]
        volume_req = 1 if (row[1][21]) == 1 else 0
        try:
            quantity_ = int(row[1][22])

            quantity = {"№"+str(quantity_): 0, "№ "+str(quantity_): 0}

            for k in quantity.copy():
                if "nan" in k:
                    del quantity[k]
        except ValueError:
            quantity = {}
        quantity_req = 1 if (row[1][23]) == 1 else 0
        if type(row[1][24])!=float:
            marker_ = (row[1][24]).split(";")
            marker = {}
            for m in marker_:
                marker[m] = 0
        else:
            marker = {}
        marker_req = 1 if (row[1][25]) == 1 else 0


        print("=======================")
        print("PRODUCT ID",product_id)
        print("PRODUCT NAME",name, name_req)
        print("MANUFACTURER",manufacturer, manufacturer_req)
        print("DOSAGE FORM",dosage_form,dosage_form_req)
        print("DOSAGE 1",dosage_size_1, dosage_size_1_req)
        print("DOSAGE 2",dosage_size_2, dosage_size_2_req)
        print("DOSAGE 3",dosage_size_3, dosage_size_3_req)
        print("PER DOSAGE",per_dosage_size, per_dosage_size_req)
        print("VOLUME",volume, volume_req)
        print("QUANTITY",quantity, quantity_req)
        print("MARKER",marker, marker_req)

        seed = {
            "product_id": product_id,
            "name": name,
            "name_req": name_req,
            "manufacturer": manufacturer,
            "manufacturer_req": manufacturer_req,
            "dosage_form": dosage_form,
            "dosage_form_req": dosage_form_req,
            "marker": marker,
            "marker_req": marker_req,
            "dosage_size_1": dosage_size_1,
            "dosage_size_1_req": dosage_size_1_req,
            "dosage_size_2": dosage_size_2,
            "dosage_size_2_req": dosage_size_2_req,
            "dosage_size_3": dosage_size_3,
            "dosage_size_3_req": dosage_size_3_req,
            "dosage_size_unique": {},
            "dosage_size_unique_req": 0,
            "per_dosage_size": per_dosage_size,
            "per_dosage_size_req": per_dosage_size_req,
            "volume": volume,
            "volume_req": volume_req,
            "quantity": quantity,
            "quantity_req": quantity_req

        }
        # await titex.add(data=seed)
        c+=1
        if c>30:
            break

    print("OK")

    print("********** TEST COMPLETE **********")

async def launch():
    from operations.TitleExecutorClient import  TitleExecutorClient
    titex= TitleExecutorClient()
    p = await titex.find_match(data={"title": "Беландж 2,5мг №30", "manufacturer": "Replek Farm"})
    # p = await titex.find_match(data={"title": "Авизол капс 150мг"})
    print(p)
    print("********** TEST COMPLETE **********")

async def test_pricelist():
    from operations.TitleExecutorClient import  TitleExecutorClient
    titex= TitleExecutorClient()
    import pandas as pd
    data = pd.read_excel("/var/www/business/testpricelist2.xls")
    c=0
    ok=0
    ambiguous=0
    nomatch=0
    data_to_send={}
    for row in data.iterrows():
        name = row[1][0]
        skip = False
        for i in ["БИНТ","БАНДАЖ","АСКОР","ВАТА","ГЕТРЫ","СБОР","ПАСТА","ИГЛА","ИГЛЫ","КОРРЕКТ","КОРСЕТ","КУКУР","ЛЕЙКО","ЛИСТ","МАРЛ",
                  "МАСКА","МАСЛО","ПЕРЧА","ПЛАСТ","ПОЯС","ПЛОД","ПРЕЗЕР","ЛЕЗВ","САЛФ","ТРАВ","ТОНОМ","УСТРОЙ","ЧАЙ","ШИПОВ","ШПРИЦ"]:
            if i in name.upper():
                skip = True

        if not skip:
            c+=1
            manufacturer = row[1][1]
            print(name,"    ",manufacturer)
            data_to_send[c]={"title": name, "manufacturer": manufacturer}

    response = await titex.find_match_many(data=data_to_send)

    for r in response:
        p = response[r]["result"]
        if p["type"]=="ok":
            ok+=1
            print(response[r])
        elif p["type"]=="ambiguous":
            ambiguous+=1
            # print(response[r])
        else:
            # print(response[r])
            nomatch+=1
    print("TOTAL",c)
    print("ok",ok,ok/c)
    print("ambiguous",ambiguous)
    print("nomatch",nomatch)
    # print(data.head(20))
    quit()

    p = await titex.find_match(data={"title": name,"manufacturer":manufacturer})
    # p = await titex.find_match(data={"title": "Авизол капс 150мг"})
    print(p)
    print("********** TEST COMPLETE **********")

async def load_manufacturers():
    from operations.ManufacturerSynonymsExecutorClient import ManufacturerSynonymsExecutorClient
    maex= ManufacturerSynonymsExecutorClient()

    import pandas as pd
    data = pd.read_excel("/var/www/business/manufacturer_synonyms.xlsx")
    print(data.head(20))
    for row in data.iterrows():
        manufacturer_id = row[1][0]
        synonyms_ = row[1][1]
        synonyms_ = synonyms_.split(";")
        synonyms = {}
        for s in synonyms_:
            synonyms[s]=0
        name = row[1][2]
        print(manufacturer_id,"    ",synonyms,name)
        p = await maex.add(data={"manufacturer_id": manufacturer_id, "synonyms": synonyms, "name": name})
        print(p)

    quit()




# main_loop.create_task(add())
# main_loop.create_task(import_title_data())
# main_loop.create_task(launch())
main_loop.create_task(test_pricelist())
# main_loop.create_task(load_manufacturers())
# main_loop.create_task(create_title_logic())
# main_loop.create_task(import_groups())
# main_loop.create_task(correct_demand())
# main_loop.create_task(load_data3())
# main_loop.create_task(duplicate_helper())
# main_loop.create_task(get_by_product_id_by_date_range(8821))
# main_loop.create_task(mod_dem_y())
# main_loop.create_task(get_by_product_id_by_date_range(9535))

main_loop.run_forever()
