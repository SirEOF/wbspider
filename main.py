# -*- coding: utf-8 -*-

from apiclient import discovery
from sn import analysis_excel
from downloader import init_downloader, download_image, generate_filepath
from conf import CX, KEY


def main():
    init_downloader()
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
