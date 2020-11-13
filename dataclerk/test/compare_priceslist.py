from collections import OrderedDict

import pandas

first_file = "Польфа.xlsx"
df = pandas.read_excel(first_file, header=None)
print(df)
df = df.applymap(lambda x: x.strip() if type(x) is str else x)
df = df.replace('  ', ' ', regex=True)
first = df.to_dict(orient='list', into=OrderedDict)
has = set()
for item in first[1]:
    has.add(str(item))
second_file = "second.xls"
df2 = pandas.read_excel(second_file, header=None)
df2 = df2.applymap(lambda x: x.strip() if type(x) is str else x)
df2 = df2.replace('  ', ' ', regex=True)
second = df2.to_dict(orient='list', into=OrderedDict)
total = len(second[1])
failed = 0
for item in second[1]:
    if item not in has:
        failed += 1
print(str(failed) + " " + str(total))
print(failed / total)
