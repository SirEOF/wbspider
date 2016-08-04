# -*- coding: utf-8 -*-

import os
import httplib2
import xlrd

from apiclient import discovery

# Google API Key
KEY = "AIzaSyBxjaBRqyg8Ql7sC43v_UyMdTQ6om0xXQY"
# Search Engine ID
CX = "015879767730051751981:rndv76votp8"
# 图片存储目录
IMG_DIR = "images"
# Excel 文件名
EXCEL_FILENAME = "data.xlsx"


def analysis_excel():
    """
    解析 Excel 文件并获取 SN 列表
    :return:
    """
    res = []
    book = xlrd.open_workbook(EXCEL_FILENAME)
    sh = book.sheet_by_index(0)
    nrows = sh.nrows
    for i in xrange(0, nrows):
        sn = sh.cell_value(rowx=i, colx=0)
        res.append(sn)
    return res


def download_image(img_url, filepath):
    """
    下载图片
    :param img_url: 图片网址
    :param filepath: 本地保存路径
    """
    h = httplib2.Http()
    resp, content = h.request(img_url)
    if resp["status"] == "200":
        with open(filepath, "wb") as f:
            f.write(content)


def generate_filepath(sn, mime):
    """
    生成图片文件名
    :param sn: SN
    :param mime: MIME
    :return: 图片文件名
    """
    filename = sn + "."
    if mime == "image/png":
        filename += ".png"
    elif mime == "image/jpeg" or mime == "image/jpg":
        filename += ".jpg"
    elif mime == "image/gif":
        filename += ".gif"
    else:
        filename += "png"
    return os.path.join(IMG_DIR, filename)


def main():
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)
    cse = discovery.build("customsearch", "v1", developerKey=KEY).cse()
    sn_list = analysis_excel()
    for sn in sn_list:
        res = cse.list(q=sn, cx=CX, searchType="image", num="1").execute()
        if "items" in res:
            link = res["items"][0]["link"]
            filepath = generate_filepath(sn, link)
            download_image(img_url=link, filepath=filepath)
            print("SN " + sn + " OK")
        else:
            print("SN " + sn + " SKIP")
    print("DONE.")


if __name__ == "__main__":
    main()
