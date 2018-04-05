#!/usr/bin/python

from pandas import Series, DataFrame
import pandas as pd
import glob, os
import re
import random

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

    packages = df['Package'].drop_duplicates().values.tolist()
    for package in packages:
        package_sheet = df.ix[df['Package'] == package]
        package_sheet = package_sheet.sort_values(by=['Realtime'], ascending=[True])
        package_sheet.insert(0, 'Index', range(1, 1 + len(package_sheet)))
        package_sheet.to_excel(writer, sheet_name=package+'_total')

        #excel chart from : http://xlsxwriter.readthedocs.io/example_pandas_chart_line.html
        #chart only interest column
        package_sheet.set_index('Index', inplace=True)
        interest_column = [col for col in package_sheet.columns if 'Pss Total' in col]
        interest_sheet = package_sheet[interest_column]
        interest_sheet.to_excel(writer, sheet_name=package)

        workbook = writer.book
        worksheet = writer.sheets[package]
        chart = workbook.add_chart({'type': 'line'})

        max_row = len(interest_sheet)
        for i in range(len(interest_sheet.columns)):
            col = i + 1
            chart.add_series({
                'name': [package, 0, col],
                'categories': [package, 1, 0, max_row, 0],
                'values': [package, 1, col, max_row, col],
            })

        chart.set_x_axis({'name': 'Runs'})
        chart.set_y_axis({'name': 'K Bytes', 'major_gridlines': {'visible': False}})

        # Insert the chart into the worksheet.
        worksheet.insert_chart('G2', chart, {'x_offset':-500, 'y_offset':-500, 'x_scale': 3, 'y_scale': 2})

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
    save_to_excel(total_data, "dumpsys_datas.xlsx")


if __name__ == "__main__":
  main()

