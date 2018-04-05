#!/usr/bin/python

from pandas import Series, DataFrame
import pandas as pd
import glob, os
import re

full_categories = ['Pss Total', 'Private Drity', 'Private Clean',
                   'SwapPss Dirty', 'Heap Size', 'Heap Alloc', 'Heap Free']

patterns = {'time':re.compile(r"(Uptime):\s+(\d+)\s+(Realtime):\s+(\d+)"),
            'process':re.compile(r"MEMINFO in pid\s+(\d+)\s+\[(.+)\]"),
            'detail':re.compile(r"(\w+\s*\w+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"),
            'other':re.compile(r"(\w+\s*\w+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")}

def find_with_pattern(content, first_pattern, detail_pattern=None):
    if detail_pattern is not None:
        match = detail_pattern.search(content)
        if match:
            return list(match.groups())

    match = first_pattern.search(content)
    if match:
        return list(match.groups())
    return list()

def get_column_with_category(default, sub):
    return "[" + default + " - " + sub + "]";

def fill_data_frame(dataframe, file, content):
    #Fill time data
    data = find_with_pattern(content, patterns['time'])
    if len(data) > 0:
        dataframe.ix[file, data[0]] = int(data[1])
        dataframe.ix[file, data[2]] = int(data[3])

    #Fill process meta data
    data = find_with_pattern(content, patterns['process'])
    if len(data) > 0:
        dataframe.ix[file, 'PID'] = int(data[0])
        dataframe.ix[file, 'Package'] = data[1]

    #Fill process detail data
    data = find_with_pattern(content, patterns['other'], detail_pattern=patterns['detail'])
    if len(data) > 0:
        default_type = data[0]
        for i in range(1, len(data)):
            dataframe.ix[file, get_column_with_category(default_type,full_categories[i-1])] = int(data[i])

    return None

def save_to_excel(df, file):
    writer = pd.ExcelWriter(file, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()

def main():
    os.chdir("files")
    total_data = DataFrame()
    for file in glob.glob("*.txt"):
        f = open(file, 'r')
        lines = f.readlines()
        for line in lines:
            fill_data_frame(total_data, file, line)
        f.close()
    total_data.fillna(0, inplace=True)
    save_to_excel(total_data, "convert.xlsx")
    print(total_data)

    print(total_data['[Native Heap - Pss Total]'])


if __name__ == "__main__":
  main()

