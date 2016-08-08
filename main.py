# -*- coding: utf-8 -*-
import os
import socket
import httplib2
from peewee import *
from apiclient import discovery, errors
from src.conf import CX, KEY, DEFAULT_TIMEOUT, DOWNLOAD_WORKER_NUM
from src.downloader import init_downloader, generate_filepath, DownloadThread, add_task, download_worker
from src.sn import get_sn_list
from src.saver import init_db, db, Saver

socket.setdefaulttimeout(DEFAULT_TIMEOUT)


def main():
    init_db()
    init_downloader()
    print("Prepare to connect the google server...")
    cse = discovery.build("customsearch", "v1", developerKey=KEY).cse()
    print("Google server has connected\n")

    print("Prepare to analysis excel file...")
    sn_list = get_sn_list()
    print("Found " + str(len(sn_list)) + " sn in excel and backup file\n")
    for sn in sn_list:
        img_url = ""
        filepath = ""
        exist = True
        try:
            s = Saver.get(Saver.sn == sn)
            img_url = s.img_url
            filepath = s.filepath
        except DoesNotExist:
            exist = False

        if not exist:
            try:
                res = cse.list(q=sn, cx=CX, searchType="image", num="1").execute()
            except errors.HttpError, httplib2.HttpLib2Error:
                print("FAIL: Cannot access google server, please check your network connection.")
                continue
            except Exception as e:
                print("FAIL: " + e.message)
                continue
            if "items" in res:
                img_url = res["items"][0]["link"]
                filepath = generate_filepath(sn, img_url)
            else:
                print("SKIP: SN " + sn + " NO RESULT")
                continue

        if os.path.exists(filepath):
            print("SKIP: SN " + sn + " HAS DOWNLOADED, IN DISK")
            saver, created = Saver.get_or_create(sn=sn, img_url=img_url, filepath=filepath)
            saver.status = True
            saver.save()
            continue

        saver, created = Saver.get_or_create(sn=sn, img_url=img_url, filepath=filepath)
        saver.status = False
        saver.save()
        
        add_task(sn, img_url, filepath)
        print("OK: SN " + sn + " HAS GOT LINK, ADDED TO THE QUEUE")

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
    db.close()


if __name__ == "__main__":
    main()
