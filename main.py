# -*- coding: utf-8 -*-

import socket
import httplib2

from apiclient import discovery, errors
from src.conf import CX, KEY, DEFAULT_TIMEOUT, DOWNLOAD_WORKER_NUM
from src.downloader import init_downloader, generate_filepath, DownloadThread, add_task, download_worker
from src.sn import analysis_excel

socket.setdefaulttimeout(DEFAULT_TIMEOUT)


def main():
    init_downloader()
    print("Prepare to connect the google server...")
    cse = discovery.build("customsearch", "v1", developerKey=KEY).cse()
    print("Google server has connected\n")

    print("Prepare to analysis excel file...")
    sn_list = analysis_excel()
    print("Found " + str(len(sn_list)) + " sn in excel\n")
    for sn in sn_list:
        try:
            res = cse.list(q=sn, cx=CX, searchType="image", num="1").execute()
        except errors.HttpError, httplib2.HttpLib2Error:
            print("FAIL: Cannot access google server, please check your network connection.")
            continue
        if "items" in res:
            img_url = res["items"][0]["link"]
            filepath = generate_filepath(sn, img_url)
            add_task(sn, img_url, filepath)
            print("OK: SN " + sn + " HAS GOT LINK")
        else:
            print("SKIP: SN " + sn + " NO RESULT")
    print("")

    threads = []
    for i in xrange(DOWNLOAD_WORKER_NUM):
        thread = DownloadThread(download_worker)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    print("\nDONE. Please view the \"images\" directory.")
    raw_input("\nPress ENTER key to exit...")


if __name__ == "__main__":
    main()
