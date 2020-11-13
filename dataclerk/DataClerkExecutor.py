#region import 
import json
import time
import locale
from datetime import datetime
from modules.kinetic_core.DateTimeEncoder import DateTimeEncoderCompact
from modules.business.warehouse.manufacturer.ManufacturerClient import ManufacturerClient
from suppliers.aliases.AgentProductAliasesClient import AgentProductAliasesClient
from modules.kinetic_core.AbstractExecutor import AbstractExecutor
from modules.business.warehouse.ProductsExecutorClient import ProductsExecutorClient
from suppliers.aliases.AgentManufacturerAliasesClient import AgentManufacturerAliasesClient
from suppliers.SuppliersExportTemplateClient import SuppliersExportTemplateClient
from suppliers.aliases.AgentFullAliasesClient import AgentFullAliasesClient
from pricelists.PriceListRevisionClient import PriceListRevisionClient
from modules.kinetic_core.DateTimeDecoder import DateTimeDecoder
from profiles.AgentExecutorClient import AgentExecutorClient
from operations.TitleExecutorClient import  TitleExecutorClient

import arrow
import pandas as pd
#endregion

import sys, unicodedata, re
# Get all unicode characters
all_chars = (chr(i) for i in range(sys.maxunicode))
# Get all non printable characters
control_chars = ''.join(c for c in all_chars if unicodedata.category(c) == 'Cc')
# Create regex of above characters
control_char_re = re.compile('[%s]' % re.escape(control_chars))
# Substitute these characters by empty string in the original string.
def remove_control_chars(s):
    return control_char_re.sub('', s)
class DataClerkExecutor(AbstractExecutor):

    async def upload(self, dictionary):
        key = str(time.time())
        await self.save({key: json.dumps(dictionary, cls=DateTimeEncoderCompact)})
        return {"key": key}

    async def remove(self, key):
        await self.save({key: None})

    async def get_one(self, key=None):
        return await self.get([key])

    # Uses re module for regex
    def isInteger(self, i):
        import re
        if not hasattr(self, '_re'):
            self._re = re.compile(r"[-+]?\d+(\.0*)?$")
        return self._re.match(str(i)) is not None

    async def parse_pricelist(self, supplier, key):

        client = SuppliersExportTemplateClient()
        revision_client = PriceListRevisionClient()
        revision = await revision_client.get_one(key=key)
        t = time.time()
        tpl = None #await client.get_one(key=supplier)

        if revision is not None:
            tpl = revision

        data = None
        if key is not None:
            data_json = await self.get_one(key=key)
            if data_json:
                data = json.loads(data_json, cls=DateTimeDecoder)
            else:
                return None
        

        keyz = list(data.keys())

        prc_base_index = 0
        prd_index = 0;
        if tpl is not None and len(tpl) > 0 and tpl["name_column"] > 0:
            prd_index = tpl["name_column"]

        mnf_index = 0;
        if tpl is not None and len(tpl) > 0 and tpl["manufacturer_column"] > 0:
            mnf_index = tpl["manufacturer_column"]

        prc_index = 0
        if tpl is not None and len(tpl) > 0 and tpl["price_cash_column"] > 0:
            prc_index = tpl["price_cash_column"]

        exp_index = 0
        if tpl is not None and len(tpl) > 0 and tpl["expiry_column"] > 0:
            exp_index = tpl["expiry_column"]

        row_index = 0
        if tpl is not None and len(tpl) > 0 and tpl["row_offset"] > 0:
            row_index = tpl["row_offset"]

        prc_wire100_index = 0
        if tpl is not None and len(tpl) > 0 and tpl["price_wire100_column"] > 0:
            prc_wire100_index = tpl["price_wire100_column"]

        prc_wire75_index = 0
        if tpl is not None and len(tpl) > 0 and tpl["price_wire75_column"] > 0:
            prc_wire75_index = tpl["price_wire75_column"]

        prc_wire50_index = 0
        if tpl is not None and len(tpl) > 0 and tpl["price_wire50_column"] > 0:
            prc_wire50_index = tpl["price_wire50_column"]
        
        prc_wire25_index = 0
        if tpl is not None and len(tpl) > 0 and tpl["price_wire25_column"] > 0:
            prc_wire25_index = tpl["price_wire25_column"]

        prc_wire100_percent = 0
        if tpl is not None and len(tpl) > 0 and tpl["price_wire100_percent"] > 0:
            prc_wire100_percent = tpl["price_wire100_percent"]

        prc_wire75_percent = 0
        if tpl is not None and len(tpl) > 0 and tpl["price_wire75_percent"] > 0:
            prc_wire75_percent = tpl["price_wire75_percent"]

        prc_wire50_percent = 0
        if tpl is not None and len(tpl) > 0 and tpl["price_wire50_percent"] > 0:
            prc_wire50_percent = tpl["price_wire50_percent"]

        prc_wire25_percent = 0
        if tpl is not None and len(tpl) > 0 and tpl["price_wire25_percent"] > 0:
            prc_wire25_percent = tpl["price_wire25_percent"]

        name_detection_row = -1
        expiry_detection_row = -1
        potential = {}
        potential_expiry = {}
        potential_start = {}
        potential_price = {}
        total_rows = len(data[keyz[0]])
        t = time.time()
        _items = data.items()
        for k,v in _items:
            potential_expiry[k] = 0
            avg = 0
            total = len(v)
            c = 0
            for value in v:
                if type(value) is str:
                    word_count = len(value.split(" "))
                    tt = value.replace(" ", "")
                    tt = value.replace(",", "")
                    if tt.isdigit(): #self.isInteger(tt):
                        if not k in potential_price:
                            potential_price[k] = 0
                        potential_price[k] += int(tt)
                    else:
                        if k in potential_price:
                            potential_price[k] = potential_price[k] / 2
                    
                    if not (total > 500 and c > 200 and potential_expiry[k] < 10):
                        if self.validate_date(value) is not None:
                            potential_expiry[k] +=1
                            pass

                    avg = (avg + word_count)

                elif type(value) is int:
                    if not k in potential_price:
                        potential_price[k] = 0
                    potential_price[k] += value
                    pass
                elif type(value) is datetime:
                    if not k in potential_expiry:
                        potential_expiry[k] = 0
                    potential_expiry[k] += 1
                c = c + 1

            if avg > 0:
                potential[k] = avg
        print("parsing data took time " + str(time.time() - t))
        t = time.time()
        for k, v in potential.items():
            potential[k] = v/total_rows
        s = sorted(potential.items(), key=lambda kv: kv[1])
        name_detection_row = s[len(s) - 1][0]
        manufacturer_detection_row = s[len(s) - 2][0]

        s = sorted(potential_price.items(), key=lambda kv: kv[1])
        if len(s) > 0:
            price_detection_row = s[len(s) - 1][0]
        else:
            price_detection_row = None

        s = sorted(potential_expiry.items(), key=lambda kv: kv[1])
        print("sorted time" + str(time.time() - t))
        t = time.time()
        if len(s) > 0:
            expiry_detection_row = s[len(s) - 1][0]

            expiry_column = data[expiry_detection_row]
            potential_start = 0
            for val in expiry_column:
                if type(val) is str and self.validate_date(val) or type(val) is datetime: 
                    break;
                potential_start += 1


        current_row = 0
        keys = data.keys()
        ignore_rows = []
        import math
        invalid_expiry = 0
        v = data[list(data.keys())[0]]
        ignore_load = 0
        print("row  detection time  " + str(time.time() - t))
        t = time.time()
        for it in range(0, len(v)):
            number_of_nan = 0
            price100 = 0
            if prc_wire100_index > 0:
                price100 = data[keyz[prc_wire100_index]][it]
                price = None
            else:
                if price_detection_row is not None:
                    price = data[price_detection_row][it]
                else:
                    price = None
            has_load = False
            for z in keys:
                c = data[z][it]
                if type(c) is str:
                    if "нагрузка" in c.lower():
                        has_load = True
                elif type(c) is float and math.isnan(c):
                    number_of_nan = number_of_nan + 1
            d2 = data[expiry_detection_row][it]
            td2 = type(d2)
            if (current_row < potential_start):
                ignore_rows.append(current_row)
            elif td2 is datetime:
                pass
            elif (td2 is str and self.validate_date(d2) is None) or td2 is not str:
                ignore_rows.append(current_row)
                invalid_expiry += 1
            elif (len(keys) - number_of_nan) < 3:
                ignore_rows.append(current_row)
            # elif price is not None and ((type(price) is float and math.isnan(price)) or type(price) is str or price is None):
            #     if not type(price) is float:
            #         tt = price.replace(" ", "")
            #         tt = price.replace(',', "")
            #         if not tt.isdigit():
            #             ignore_rows.append(current_row)
            #     else:
            #         ignore_rows.append(current_row)
            elif has_load:
                ignore_load += 1
                ignore_rows.append(current_row)
            if prc_wire100_index > 0:
                if type(price100) is str and "," in price100:
                    price100 = price100.replace(" ", "")
                    price100 = price100.replace(",", ".")
                    try:
                        price100 = float(price100)
                    except:
                        pass
                if type(price100) is str and not price100.isdigit():
                    ignore_rows.append(current_row)
                elif type(price100) is float and math.isnan(price100):
                    ignore_rows.append(current_row)

            current_row = current_row + 1
        print("pre result time " + str(time.time() - t))
        
        result = {}
        result["data"]=data
        result["revision"] = {
            "ignore_expiry_count": invalid_expiry,
            "ignore_load_count":ignore_load,
            "row_offset": row_index if row_index > 0 else potential_start,
            "name_column":int(prd_index if prd_index > 0 else name_detection_row),
            "manufacturer_column":int(mnf_index if mnf_index > 0 else manufacturer_detection_row),
            "expiry_column":int(exp_index if exp_index > 0 else expiry_detection_row),
            "price_cash_column":int(prc_index),
            "price_base_column":int(prc_base_index),
            "price_wire100_column":int(prc_wire100_index),
            "price_wire75_column":int(prc_wire75_index),
            "price_wire50_column":int(prc_wire50_index),
            "price_wire25_column":int(prc_wire25_index),
            "price_wire100_percent":prc_wire100_percent,
            "price_wire75_percent":prc_wire75_percent,
            "price_wire50_percent":prc_wire50_percent,
            "price_wire25_percent":prc_wire25_percent,
            "ignore":json.dumps(ignore_rows)
        }
        return result

    async def filter(self, revision):

        to_analyze = []
        agent_client = AgentExecutorClient()
        agent = await agent_client.get_one(agent_id=revision["agent_id"])

        t = time.time()
        data_json = await self.get([revision["key"]])
        
        data = json.loads(data_json, cls=DateTimeDecoder)
        print("loading " + str(time.time() - t))
        t = time.time()
        keyz = list(data.keys())
        values = []
        corrected = []
        products_client = ProductsExecutorClient()
        manufacturers = set()
        corrected_manufacturers = list()
        corrected_manufacturers_set = set()
        product_column = data[keyz[revision["name_column"]]]
        full_alias_client = AgentFullAliasesClient()
        manufacturer_client = ManufacturerClient()
        parent_manufacturer_id = None
        manufacturer_column = None
        hasss = "manufacturer_id" in agent and agent["manufacturer_id"] != None and agent["manufacturer_id"] > 0
        if not hasss:
            manufacturer_column = data[keyz[revision["manufacturer_column"]]]
            for i in range(revision["row_offset"], len(data[keyz[0]])):
                manufacturer = manufacturer_column[i]
                if type(manufacturer) is str:
                    manufacturer = manufacturer.lower()
                    manufacturer = "".join(manufacturer.splitlines())
                if not type(manufacturer) is float:
                    if (manufacturer not in manufacturers) and manufacturer != "":
                        manufacturers.add(str(manufacturer))

            
            manufacturers_l = list(manufacturers)
            for i in range(revision["row_offset"], len(data[keyz[0]])):
                manufacturer = manufacturer_column[i]
                if type(manufacturer) is str:
                    manufacturer = manufacturer.lower()
                    manufacturer = "".join(manufacturer.splitlines())
                if not type(manufacturer) is float:
                    manufacturers.add(str(manufacturer))
                corrected_manufacturers_set.add(str(manufacturer))
                corrected_manufacturers.append(str(manufacturer))

            manufacturer_matches = await manufacturer_client.matches(names=list(corrected_manufacturers_set))
            print("manufacturer time " + str(time.time() - t))
            t = time.time()

            wrong_manufacturers = set()
            for manufacturer in corrected_manufacturers:
                if manufacturer not in manufacturer_matches:
                    wrong_manufacturers.add(manufacturer)
        else:
            parent_manufacturer_id = agent["manufacturer_id"]
            manuf = await manufacturer_client.get_by_id(mid=agent["manufacturer_id"])
            manufacturer_name = manuf["name"]
            for i in range(revision["row_offset"], len(data[keyz[0]])):
                corrected_manufacturers.append(manufacturer_name)
        
        
        corrected_products = list()
        for i in range(revision["row_offset"], len(data[keyz[0]])):
            product = remove_control_chars(str(product_column[i]))
            corrected_products.append(str(product))

        print("correct product time " + str(time.time() - t))
        t = time.time()
        
        if revision["price_cash_column"] >= 0:
            price_cash_column = data[keyz[revision["price_cash_column"]]]
        else:
            price_cash_column = None
        if revision["price_wire100_column"] >= 0:
            price_wire100_column = data[keyz[revision["price_wire100_column"]]]
        else:
            price_wire100_column = None
        if revision["price_wire75_column"] >= 0:
            price_wire75_column = data[keyz[revision["price_wire75_column"]]]
        else:
            price_wire75_column = None
        if revision["price_wire50_column"] >= 0:
            price_wire50_column = data[keyz[revision["price_wire50_column"]]]
        else:
            price_wire50_column = None
        if revision["price_wire25_column"] >= 0:
            price_wire25_column = data[keyz[revision["price_wire25_column"]]]
        else:
            price_wire25_column = None

        matches = await products_client.matches(names=corrected_products)
        expiry_column = data[keyz[revision["expiry_column"]]]

        for i in range(revision["row_offset"], len(data[keyz[0]])):
            row = i - revision["row_offset"]
            name = corrected_products[i - revision["row_offset"]]
            potenial_manufacturer = None
            if ("ignore" in revision and revision["ignore"] is not None and str(i) in revision["ignore"]):
                continue
            if ("manual_ignore" in revision and revision["manual_ignore"] != None and revision["manual_ignore"] is not None and str(i) in revision["manual_ignore"]):
                continue

            match_name = None
            if name in matches:
                match_name = matches[name]
            
            missing_name = match_name is None
            if not missing_name:
                potenial_manufacturer = match_name["manufacturer"]

            manufacturer = corrected_manufacturers[i - revision["row_offset"]]
            missing_manufacturer = False
            if parent_manufacturer_id is not None:
                manufacturer_id = parent_manufacturer_id
            else:
                manufacturer_id = None
                
                if manufacturer in wrong_manufacturers:
                    missing_manufacturer = True
                else:
                    manufacturer_id = manufacturer_matches[manufacturer]["manufacturer_id"]

            if missing_name:
                match_name = await full_alias_client.find(alias_product=name, 
                alias_manufacturer=manufacturer)
                if match_name is not None:
                    missing_name = False
                    missing_manufacturer = False
                    product = await products_client.get_one(product_id=match_name["product_id"])
                    print(match_name["product_id"])
                    name = product["name"]
                    manufacturer = product["manufacturer"]
                else:
                    to_analyze.append({"title": name, "manufacturer": manufacturer})
                    pass
            
            # todo check later
            price_cash = 0
            price_wire100 = None
            price_wire75 = None
            price_wire50 = None
            price_wire25 = None
            if revision["price_cash_column"] > 0:
                price_cash = price_cash_column[i]
                if not isinstance(price_cash, (int, float)):
                    price_cash = price_cash.replace(" ", "")
                    price_cash = price_cash.replace(",", ".")
                    try:
                        price_cash = float(price_cash)
                    except:
                        price_cash = None
                        pass
                    
            if revision["price_wire100_column"] > 0:
                price_wire100 = price_wire100_column[i]
                if not isinstance(price_wire100, (int, float)):
                    price_wire100 = price_wire100.replace(" ", "")
                    price_wire100 = price_wire100.replace(",", ".")
                    try:
                        price_wire100 = float(price_wire100)
                    except:
                        price_wire100 = None
                        pass
            else:
                price_wire100 = price_cash + price_cash * (revision["price_wire100_percent"] / 100.0)
            
            if revision["price_wire75_column"] > 0:
                price_wire75 = price_wire75_column[i]
                if not isinstance(price_wire100, (int, float)):
                    price_wire75 = price_wire75.replace(" ", "")
                    price_wire75 = price_wire75.replace(",", ".")
                    try:
                        price_wire75 = float(price_wire75)
                    except:
                        price_wire75 = None
                        pass
            elif revision["price_wire75_percent"] > 0:
                price_wire75 = price_cash + price_cash * (revision["price_wire75_percent"] / 100.0)

            if revision["price_wire50_column"] > 0:
                price_wire50 = price_wire50_column[i]
                if not isinstance(price_wire50, (int, float)):
                    price_wire50 = price_wire50.replace(" ", "")
                    price_wire50 = price_wire50.replace(",", ".")
                    try:
                        price_wire50 = float(price_wire50)
                    except:
                        price_wire50 = None
                        pass
            elif revision["price_wire50_percent"] > 0:
                price_wire50 = price_cash + price_cash * (revision["price_wire50_percent"] / 100.0)

            if revision["price_wire25_column"] > 0:
                price_wire25 = price_wire25_column[i]
                if not isinstance(price_wire25, (int, float)):
                    price_wire25 = price_wire25.replace(" ", "")
                    price_wire25 = price_wire25.replace(",", ".")
                    try:
                        price_wire25 = float(price_wire25)
                    except:
                        price_wire25 = None
                        pass
            elif revision["price_wire25_percent"] > 0:
                price_wire25 = price_cash + price_cash * (revision["price_wire25_percent"] / 100.0)
            
            if type(expiry_column[i]) is not datetime:
                expiry = self.validate_date(expiry_column[i])
            else:
                expiry = expiry_column[i]
            if name == "nan" and manufacturer == "nan":
                # it's an empty row
                continue
            
            if not missing_name and not missing_manufacturer and expiry is not None and (price_cash is not None or price_wire100 is not None):
                val = {
                    # TODO: do the same in manufacturer in both dicts
                    #"n": name,
                    #"m": manufacturer,
                    "n": product_column[i],
                    "m": manufacturer_column[i] if manufacturer_column is not None else manufacturer,
                    "e": expiry,
                    "mid": manufacturer_id,
                    "quantity": 100, #todo
                    "product_id": match_name["product_id"]
                }
                try:
                    if price_cash is not None:
                        val["price_cash"] = price_cash
                    if price_wire100 is not None:
                        val["price_wire100"] = int(round(price_wire100))
                    if price_wire75 is not None:
                        val["price_wire75"] = int(round(price_wire75))
                    if price_wire50 is not None:
                        val["price_wire50"] = int(round(price_wire50))
                    if price_wire25 is not None:
                        val["price_wire25"] = int(round(price_wire25))
                    corrected.append(val)
                except Exception as e:
                    pass
                continue
            val = {
                # TODO: do the same in manufacturer in both dicts
                # "n": name,
                # "m": manufacturer,
                "n": product_column[i],
                # "cn": self.c(name),
                "m_p": potenial_manufacturer,
                "mid": manufacturer_id,
                "n_c": missing_name,
                "m": manufacturer_column[i] if manufacturer_column is not None else manufacturer,
                "m_c": missing_manufacturer,
                "row": i,
                "e": expiry
            }
            try:
                if price_cash is not None:
                    val["price_cash"] = price_cash
                if price_wire100 is not None:
                    val["price_wire100"] = int(round(price_wire100))
                if price_wire75 is not None:
                    try:
                        val["price_wire75"] = int(round(price_wire75))
                    except:
                        pass
                if price_wire50 is not None:
                    try:
                        val["price_wire50"] = int(round(price_wire50))
                    except:
                        pass
                if price_wire25 is not None:
                    try:
                        val["price_wire25"] = int(round(price_wire25))
                    except:
                        pass
                values.append(val)
            except:
                pass

        print(" to analyze " + str(len(to_analyze)))
        titex= TitleExecutorClient()
        p = await titex.find_match_many(data=to_analyze)
        
        for da in p:
            rr = da["result"]
            if rr["type"] == "ok":

                try:
                    titex= TitleExecutorClient()
                    await full_alias_client.add(data={"product_id": rr["result"]["product_id"],
                                                        "alias_manufacturer": da["manufacturer"],
                                                        "alias_product": da["title"],
                                                        "agent_id": revision["agent_id"]})
                except:
                    print("failed")
            else:
                from dataclerk.NewProductTaskClient import NewProductTaskClient
                new_product_client = NewProductTaskClient()
                await new_product_client.add(task={
                    "name": da["title"], 
                    "supplier_id": revision["agent_id"], 
                    "manufacturer": da["manufacturer"],
                    "type": rr["type"]
                })
        
        corrected = []
        values = []
        for i in range(revision["row_offset"], len(data[keyz[0]])):
            row = i - revision["row_offset"]
            name = corrected_products[i - revision["row_offset"]]
            potenial_manufacturer = None
            if ("ignore" in revision and revision["ignore"] is not None and str(i) in revision["ignore"]):
                continue
            if ("manual_ignore" in revision and revision["manual_ignore"] != None and revision["manual_ignore"] is not None and str(i) in revision["manual_ignore"]):
                continue

            match_name = None
            if name in matches:
                match_name = matches[name]
            
            missing_name = match_name is None
            if not missing_name:
                potenial_manufacturer = match_name["manufacturer"]

            manufacturer = corrected_manufacturers[i - revision["row_offset"]]
            missing_manufacturer = False
            if parent_manufacturer_id is not None:
                manufacturer_id = parent_manufacturer_id
            else:
                manufacturer_id = None
                
                if manufacturer in wrong_manufacturers:
                    missing_manufacturer = True
                else:
                    manufacturer_id = manufacturer_matches[manufacturer]["manufacturer_id"]

            if missing_name:
                match_name = await full_alias_client.find(alias_product=name, 
                alias_manufacturer=manufacturer)
                if match_name is not None:
                    missing_name = False
                    missing_manufacturer = False
                    product = await products_client.get_one(product_id=match_name["product_id"])
                    name = product["name"]
                    manufacturer = product["manufacturer"]
                else:
                    to_analyze.append({"title": name, "manufacturer": manufacturer})
                    pass
            
            # todo check later
            price_cash = 0
            price_wire100 = None
            price_wire75 = None
            price_wire50 = None
            price_wire25 = None
            if revision["price_cash_column"] > 0:
                price_cash = price_cash_column[i]
                if not isinstance(price_cash, (int, float)):
                    price_cash = price_cash.replace(" ", "")
                    price_cash = price_cash.replace(",", ".")
                    try:
                        price_cash = float(price_cash)
                    except:
                        price_cash = None
                        pass
                    
            if revision["price_wire100_column"] > 0:
                price_wire100 = price_wire100_column[i]
                if not isinstance(price_wire100, (int, float)):
                    price_wire100 = price_wire100.replace(" ", "")
                    price_wire100 = price_wire100.replace(",", ".")
                    try:
                        price_wire100 = float(price_wire100)
                    except:
                        price_wire100 = None
                        pass
            else:
                price_wire100 = price_cash + price_cash * (revision["price_wire100_percent"] / 100.0)
            
            if revision["price_wire75_column"] > 0:
                price_wire75 = price_wire75_column[i]
                if not isinstance(price_wire100, (int, float)):
                    price_wire75 = price_wire75.replace(" ", "")
                    price_wire75 = price_wire75.replace(",", ".")
                    try:
                        price_wire75 = float(price_wire75)
                    except:
                        price_wire75 = None
                        pass
            elif revision["price_wire75_percent"] > 0:
                price_wire75 = price_cash + price_cash * (revision["price_wire75_percent"] / 100.0)

            if revision["price_wire50_column"] > 0:
                price_wire50 = price_wire50_column[i]
                if not isinstance(price_wire50, (int, float)):
                    price_wire50 = price_wire50.replace(" ", "")
                    price_wire50 = price_wire50.replace(",", ".")
                    try:
                        price_wire50 = float(price_wire50)
                    except:
                        price_wire50 = None
                        pass
            elif revision["price_wire50_percent"] > 0:
                price_wire50 = price_cash + price_cash * (revision["price_wire50_percent"] / 100.0)

            if revision["price_wire25_column"] > 0:
                price_wire25 = price_wire25_column[i]
                if not isinstance(price_wire25, (int, float)):
                    price_wire25 = price_wire25.replace(" ", "")
                    price_wire25 = price_wire25.replace(",", ".")
                    try:
                        price_wire25 = float(price_wire25)
                    except:
                        price_wire25 = None
                        pass
            elif revision["price_wire25_percent"] > 0:
                price_wire25 = price_cash + price_cash * (revision["price_wire25_percent"] / 100.0)
            
            if type(expiry_column[i]) is not datetime:
                expiry = self.validate_date(expiry_column[i])
            else:
                expiry = expiry_column[i]
            if name == "nan" and manufacturer == "nan":
                # it's an empty row
                continue
            
            if not missing_name and not missing_manufacturer and expiry is not None and (price_cash is not None or price_wire100 is not None):
                val = {
                    # TODO: do the same in manufacturer in both dicts
                    #"n": name,
                    #"m": manufacturer,
                    "n": product_column[i],
                    "m": manufacturer_column[i] if manufacturer_column is not None else manufacturer,
                    "e": expiry,
                    "mid": manufacturer_id,
                    "quantity": 100, #todo
                    "product_id": match_name["product_id"]
                }
                try:
                    if price_cash is not None:
                        val["price_cash"] = price_cash
                    if price_wire100 is not None:
                        val["price_wire100"] = int(round(price_wire100))
                    if price_wire75 is not None:
                        val["price_wire75"] = int(round(price_wire75))
                    if price_wire50 is not None:
                        val["price_wire50"] = int(round(price_wire50))
                    if price_wire25 is not None:
                        val["price_wire25"] = int(round(price_wire25))
                    corrected.append(val)
                except Exception as e:
                    pass
                continue
            val = {
                # TODO: do the same in manufacturer in both dicts
                # "n": name,
                # "m": manufacturer,
                "n": product_column[i],
                # "cn": self.c(name),
                "m_p": potenial_manufacturer,
                "mid": manufacturer_id,
                "n_c": missing_name,
                "m": manufacturer_column[i] if manufacturer_column is not None else manufacturer,
                "m_c": missing_manufacturer,
                "row": i,
                "e": expiry
            }
            try:
                if price_cash is not None:
                    val["price_cash"] = price_cash
                if price_wire100 is not None:
                    val["price_wire100"] = int(round(price_wire100))
                if price_wire75 is not None:
                    try:
                        val["price_wire75"] = int(round(price_wire75))
                    except:
                        pass
                if price_wire50 is not None:
                    try:
                        val["price_wire50"] = int(round(price_wire50))
                    except:
                        pass
                if price_wire25 is not None:
                    try:
                        val["price_wire25"] = int(round(price_wire25))
                    except:
                        pass
                values.append(val)
            except:
                pass

        result = {"problems": values, "ready": corrected}
        print("total time " + str(time.time() - t))
        return result

    def validate_date(self, value):
        if type(value) is float:
            return None
        formats = [
            '%m.%y', '%d.%m.%y', '%d.%m.%Y', '%m/%y', '%m/%Y', '%Y.%m', '%Y',
            '%m.%Y', '%m,%Y', '%Y', '%m/%d/%y %I:%M:%S %p', '%m/%Yг.', '%m/%Yг',
            '%m/%d/%Y %I:%M:%S %p', '%b %Y']
        for format in formats:
            try:
                # val = pendulum.from_format(value, format)
                val = pd.to_datetime(value, format=format)
                return val
            except Exception:
                pass
        

        try:
            value = value.replace("Январь", "January")\
                .replace("Февраль", "February")\
                .replace("Март", "March")\
                .replace("Апрель", "April")\
                .replace("Май", "May")\
                .replace("Июнь", "June")\
                .replace("Июль", "July")\
                .replace("Август", "August")\
                .replace("Сентябрь", "September")\
                .replace("Октябрь", "October")\
                .replace("Ноябрь", "November")\
                .replace("Декабрь", "December")
                # val = pendulum.from_format(value, format)
            val = pd.to_datetime(value, format='%B %y г.')
            return val
        except Exception:
            pass
        

        try:

            value = value.replace("янв.", "January ")\
                .replace("фев.", "February ")\
                .replace("мар.", "March ")\
                .replace("апр.", "April ")\
                .replace("май.", "May ")\
                .replace("июн.", "June ")\
                .replace("июл.", "July ")\
                .replace("авг.", "August ")\
                .replace("сен.", "September ")\
                .replace("окт.", "October ")\
                .replace("ноя.", "November ")\
                .replace("дек.", "December ")
                # val = pendulum.from_format(value, format)
            val = pd.to_datetime(value, format='%B %y')
            return val
        except Exception:
            pass

        try:
                # val = pendulum.from_format(value, format)
            val = pd.to_datetime(value, format='%B %Y г.')
            return val
        except Exception:
            pass

        

        try:
            value = value.replace("янв", "January")\
                .replace("фев", "February")\
                .replace("мар", "March")\
                .replace("апр", "April")\
                .replace("май", "May")\
                .replace("июн", "June")\
                .replace("июл", "July")\
                .replace("авг", "August")\
                .replace("сен", "September")\
                .replace("окт", "October")\
                .replace("ноя", "November")\
                .replace("дек", "December")
                # val = pendulum.from_format(value, format)
            val = pd.to_datetime(value, format='%B %Y')
            return val
        except Exception:
            pass

        # locale.setlocale(locale.LC_TIME, "ru_RU")
        # n = datetime.now()
        return None