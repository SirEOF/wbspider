# -*- coding: utf-8 -*-
import os
import csv
import socket
import httplib2
import time
from peewee import *
from apiclient import discovery, errors
from src.conf import CX, KEY, DEFAULT_TIMEOUT, DOWNLOAD_WORKER_NUM
from src.downloader import init_downloader, generate_filepath, DownloadThread, add_task, download_worker
from src.sn import get_sn_list, analysis_excel
from src.saver import init_db, db, Saver

socket.setdefaulttimeout(DEFAULT_TIMEOUT)


def main():
    download_image = False
    input = raw_input('Download Image? (yes or no)')
    if input == 'yes':
        download_image = True
        print('CONFIRMED DOWNLOAD IMAGE, WILL START')
    else:
        download_image = False
        print('NO IMAGES DOWNLOAD, WILL START')
    print('')

    link = open('link.csv', 'ab')
    linkwriter = csv.writer(link, delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)

    init_db()
    init_downloader()
    print("Prepare to connect the google server...")
    cse = discovery.build("customsearch", "v1", developerKey=KEY).cse()
    print("Google server has connected\n")

    print("Prepare to analysis excel file...")
    # sn_list = get_sn_list()
    sn_list = analysis_excel()
    print("Found " + str(len(sn_list)) + " sn in excel\n")
    count = 0
    sn_list_len = len(sn_list)
    for sn in sn_list:
        count += 1
        sn = sn.encode('utf-8')
        img_url = ""
        filepath = ""
        # exist = True
        # try:
        #     s = Saver.get(Saver.sn == sn)
        #     img_url = s.img_url.encode('utf-8')
        #     filepath = s.filepath
        # except DoesNotExist:
        #     exist = False
        exist = False

        if not exist:
            time.sleep(1)
            try:
                res = cse.list(q=sn, cx=CX, searchType="image", num="1").execute()
            except errors.HttpError as e:
                print("(%d/%d) " % (count, sn_list_len) + "FAIL: Cannot access google server. REASON(HTTPERROR): %s" % e)
                linkwriter.writerow([sn, "FAIL: Cannot access google server. REASON(HTTPERROR): %s" % e])
                continue
            except httplib2.HttpLib2Error as e:
                print("(%d/%d) " % (count, sn_list_len) + "FAIL: Cannot access google server. REASON(HTTPLIB2ERROR): %s" % e)
                linkwriter.writerow([sn, "FAIL: Cannot access google server. REASON(HTTPLIB2ERROR): %s" % e])
                continue
            except Exception as e:
                print("(%d/%d) " % (count, sn_list_len) + "FAIL: " + e.message)
                linkwriter.writerow([sn, "FAIL: " + e.message])
                continue
            if "items" in res:
                img_url = res["items"][0]["link"].encode('utf-8')
                linkwriter.writerow([sn, img_url])
                filepath = generate_filepath(sn, img_url)
                if not download_image:
                    print("(%d/%d) " % (count, sn_list_len) + "SN " + sn + " HAS LINKED")
            else:
                print("(%d/%d) " % (count, sn_list_len) + "SKIP: SN " + sn + " NO RESULT")
                linkwriter.writerow([sn, "SKIP: NO RESULT"])
                continue

        if download_image:
            if os.path.exists(filepath):
                print("(%d/%d) " % (count, sn_list_len) + "SKIP: SN " + sn + " HAS DOWNLOADED, IN DISK")
                # saver, created = Saver.get_or_create(sn=sn, img_url=img_url, filepath=filepath)
                # saver.status = True
                # saver.save()
                continue

            # saver, created = Saver.get_or_create(sn=sn, img_url=img_url, filepath=filepath)
            # saver.status = False
            # saver.save()

            add_task(sn, img_url, filepath)
            print("(%d/%d) " % (count, sn_list_len) + "OK: SN " + sn + " HAS GOT LINK, ADDED TO THE QUEUE")

    print("ALL LINKS DONE!")
    link.close()

    if download_image:
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
