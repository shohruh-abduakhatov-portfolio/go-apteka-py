from collections import OrderedDict
import os  # NOQA: E402
import sys  # NOQA: E402
import uvloop  # NOQA: E402
uvloop.install()  # NOQA: E402
os.environ['VITA_CONFIG'] = '/var/www/config.py'  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../../../modules/vita"))  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../../../"))  # NOQA: E402
print(os.path.abspath(__file__ + "/../../../"))
from modules.kinetic_core.Connector import db
import pandas as pandas

from dataclerk.DataClerkClient import DataClerkClient
from dataclerk.task.DataClerkTaskClient import DataClerkTaskClient
first_file = "/Users/disturber/Downloads/optima.xlsx"

supplier_id = 121


async def test():
    dataclerk = DataClerkClient()

    xls = pandas.ExcelFile(first_file)
    df = None
    for sheet_name in xls.sheet_names:
        df = pandas.read_excel(xls, sheet_name=sheet_name, header=None)
        if len(df) > 0:
            break

# xls = pandas.ExcelFile(first_file)
# df = None
# for sheet_name in xls.sheet_names:
#     df = pandas.read_excel(xls, sheet_name=sheet_name)
#     if len(df) > 0:
#         print(len(df))
#         break
# df = df.applymap(lambda x: x.strip() if type(x) is str else x)
# df = df.replace('  ', ' ', regex=True)
# save_to_redis = df.to_dict(orient='list', into=OrderedDict)
# print(list(save_to_redis.keys())[0])
# df = df.applymap(lambda x: x.strip() if type(x) is str else x)
# df = df.replace('  ', ' ', regex=True)
# first = df.to_dict(orient='list', into=OrderedDict)
# has = set()
# for item in first[1]:
#     has.add(str(item))
# second_file = "second.xls"
# df2 = pandas.read_excel(second_file, header=None)
# df2 = df2.applymap(lambda x: x.strip() if type(x) is str else x)
# df2 = df2.replace('  ', ' ', regex=True)
# second = df2.to_dict(orient='list', into=OrderedDict)
# total = len(second[1])
# failed = 0
# for item in second[1]:
#     if item not in has:
#         failed += 1
# print(str(failed) + " " + str(total))
# print(failed / total)
