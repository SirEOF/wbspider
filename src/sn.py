# -*- coding: utf-8 -*-
import os
import sys
import xlrd
from src.saver import db, Saver
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


def get_sn_list():
    tmp_list = Saver.select()
    for tmp in tmp_list:
        if tmp.status and not os.path.exists(tmp.filepath):
            tmp.status = False
            tmp.save()

    excel_set = set(analysis_excel())
    saver_model_list = Saver.select().where(Saver.status == False)
    saver_list = []
    for saver_model in saver_model_list:
        saver_list.append(saver_model.sn)
    saver_model_total_list = Saver.select()
    saver_total_list = []
    for saver_model in saver_model_total_list:
        saver_total_list.append(saver_model.sn)
    saver_total_set = set(saver_total_list)
    saver_set = set(saver_list)
    return list(saver_set | (excel_set - saver_total_set))
