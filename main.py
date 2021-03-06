# -*- coding: utf-8 -*-

import os
import csv
import socket
import httplib2
import time
from apiclient import discovery, errors
from src.conf import CX, KEY, DEFAULT_TIMEOUT, DOWNLOAD_WORKER_NUM
from src.downloader import init_downloader, generate_filepath, DownloadThread, add_task, download_worker
from src.sn import analysis_excel

socket.setdefaulttimeout(DEFAULT_TIMEOUT)


def main():
    user_input = raw_input('Download Image? (yes or no)')
    if user_input == 'yes':
        download_image = True
        print('CONFIRMED DOWNLOAD IMAGE, WILL START')
    else:
        download_image = False
        print('NO IMAGES DOWNLOAD, WILL START')
    print('')

    link = open('link.csv', 'ab')
    linkwriter = csv.writer(link, delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)

    init_downloader()
    print("Prepare to connect the google server...")
    cse = discovery.build("customsearch", "v1", developerKey=KEY).cse()
    print("Google server has connected\n")

    print("Prepare to analysis excel file...")
    excel_content = analysis_excel()
    print("Found " + str(len(excel_content)) + " sn in excel\n")
    count = 0
    sn_list_len = len(excel_content)
    for row in excel_content:
        sn = row['sn'].encode('utf-8')
        description = row['description'].encode('utf-8')
        count += 1

        if sn == '无条形码':
            print("(%d/%d) " % (count, sn_list_len) + "USE DESCRIPTION: NO SN, USE DESCRIPTION %s" % description)
            sn = description

        time.sleep(1)
        try:
            res = cse.list(q=sn, cx=CX, searchType="image", num="1").execute()
        except errors.HttpError as e:
            print("(%d/%d) " % (count, sn_list_len) + "FAIL: Cannot access google server. REASON(HTTPERROR): %s" % str(e.message))
            linkwriter.writerow([sn, "FAIL: Cannot access google server. REASON(HTTPERROR): %s" % str(e.message)])
            continue
        except httplib2.HttpLib2Error as e:
            print("(%d/%d) " % (count, sn_list_len) + "FAIL: Cannot access google server. REASON(HTTPLIB2ERROR): %s" % str(e.message))
            linkwriter.writerow([sn, "FAIL: Cannot access google server. REASON(HTTPLIB2ERROR): %s" % str(e.message)])
            continue
        except Exception as e:
            print("(%d/%d) " % (count, sn_list_len) + "FAIL: " + str(e.message))
            linkwriter.writerow([sn, "FAIL: " + str(e.message)])
            continue

        if "items" in res:
            img_url = res["items"][0]["link"].encode('utf-8')
            linkwriter.writerow([sn, img_url])
            filepath = generate_filepath(sn, img_url)
            if not download_image:
                print("(%d/%d) " % (count, sn_list_len) + "SN " + sn + " HAS LINKED")
        else:
            if sn == description:
                linkwriter.writerow([sn, "SKIP: NO RESULT"])
                continue

            print("(%d/%d) " % (count, sn_list_len) + "USE DESCRIPTION: SN " + sn + " NO RESULT, USE DESCRIPTION %s" % description)
            time.sleep(1)
            try:
                res = cse.list(q=description, cx=CX, searchType="image", num="1").execute()
            except errors.HttpError as e:
                print("(%d/%d) " % (count, sn_list_len) + "FAIL: Cannot access google server. REASON(HTTPERROR): %s" % str(e.message))
                linkwriter.writerow([sn, "FAIL: Cannot access google server. REASON(HTTPERROR): %s" % str(e.message)])
                continue
            except httplib2.HttpLib2Error as e:
                print("(%d/%d) " % (count, sn_list_len) + "FAIL: Cannot access google server. REASON(HTTPLIB2ERROR): %s" % str(e.message))
                linkwriter.writerow([sn, "FAIL: Cannot access google server. REASON(HTTPLIB2ERROR): %s" % str(e.message)])
                continue
            except Exception as e:
                print("(%d/%d) " % (count, sn_list_len) + "FAIL: " + str(e.message))
                linkwriter.writerow([sn, "FAIL: " + str(e.message)])
                continue

            if "items" in res:
                img_url = res["items"][0]["link"].encode('utf-8')
                linkwriter.writerow([sn, img_url])
                filepath = generate_filepath(sn, img_url)
                if not download_image:
                    print("(%d/%d) " % (count, sn_list_len) + "SN " + sn + " WITH DESCRIPTION " + description + " HAS LINKED")
            else:
                linkwriter.writerow([sn, "SKIP: NO RESULT"])
                continue

        if download_image:
            if os.path.exists(filepath):
                print("(%d/%d) " % (count, sn_list_len) + "SKIP: SN " + sn + " HAS DOWNLOADED, IN DISK")
                continue

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


if __name__ == "__main__":
    main()
