# -*- coding: utf-8 -*-

import os
import socket

import httplib2

from src.conf import IMG_DIR


def init_downloader():
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)


def download_image(img_url, filepath):
    """
    下载图片
    :param img_url: 图片网址
    :param filepath: 本地保存路径
    """
    h = httplib2.Http()
    try:
        resp, content = h.request(img_url)
    except socket.error:
        return False
    if resp["status"] == "200":
        with open(filepath, "wb") as f:
            f.write(content)
    return True


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