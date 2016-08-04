# -*- coding: utf-8 -*-
import sys
import xlrd

from src.conf import EXCEL_FILENAME


def analysis_excel():
    """
    解析 Excel 文件并获取 SN 列表
    :return: SN List
    """
    res = []
    try:
        book = xlrd.open_workbook(EXCEL_FILENAME)
    except IOError:
        print("NO data.xlsx FOUND IN CURRENT DIRECTORY.")
        raw_input("\nPress ENTER key to exit...")
        sys.exit(1)
    sh = book.sheet_by_index(0)
    nrows = sh.nrows
    for i in xrange(0, nrows):
        sn = sh.cell_value(rowx=i, colx=0)
        res.append(sn)
    return res
