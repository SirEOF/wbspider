# -*- coding: utf-8 -*-

import xlrd

# Excel 文件名
EXCEL_FILENAME = "data.xlsx"


def analysis_excel():
    """
    解析 Excel 文件并获取 SN 列表
    :return: SN List
    """
    res = []
    book = xlrd.open_workbook(EXCEL_FILENAME)
    sh = book.sheet_by_index(0)
    nrows = sh.nrows
    for i in xrange(0, nrows):
        sn = sh.cell_value(rowx=i, colx=0)
        res.append(sn)
    return res