from pixivpy3 import *
from Download_CenterAPI import Pixiv_Miku_Download_API  # nopep8
import os
import sys
import csv
import pandas as pd
sys.dont_write_bytecode = True


class Pixiv_Miku_Downloader(Pixiv_Miku_Download_API):
    def __init__(self, aim="favorite", mode="both"):
        self.aim = aim
        self.mode = mode
        self.df = pd.read_csv(
            'C:\\Users\\Administrateur\\Documents\\Illusts_records\\Miku_Illusts_record.csv')
        self.favorite_list = list(self.df['favorite'])
        self.not_favorite_list = list(self.df['not_favorite'])

        sni = False
        if not sni:
            self.api = AppPixivAPI()
        else:
            self.api = ByPassSniApi()  # Same as AppPixivAPI, but bypass the GFW
            self.api.require_appapi_hosts()

        self.login_user()

    def downloader(self, json_results, count=0, json_result_key="favorite"):
        Illusts_path = self.create_illusts_dir(aim=json_result_key)
        print("Illusts_path:"+Illusts_path)
        id_records = []
        for illust in json_results.illusts:
            image_url = []

            if illust.id in self.favorite_list or illust.id in self.not_favorite_list:
                continue

            if illust.page_count == 1:
                image_url.append(illust.meta_single_page.get(
                    'original_image_url', illust.image_urls.large))
            elif illust.page_count > 1:
                for i in illust.meta_pages:
                    image_url.append(i.image_urls.original)

            id_records.append(illust.id)

            for a in image_url:
                self.api.download(a, path=Illusts_path, name=None)
            count -= 1
            if count == 0:
                break

        if count != 0:
            self.downloader()

        return id_records

    def handle_datas(self, json_results, aim="favorite", mode="both"):
        last_page = False
        id_record_dic = {}
        while not last_page:
            count = 0
            for json_result_key in json_results:
                if not json_results[json_result_key].next_url:
                    last_page = True
                id_record = self.downloader(
                    json_results=json_results[json_result_key], count=count, json_result_key=json_result_key)
                id_record_dic[json_result_key] = id_record

                next_qs = self.api.parse_qs(
                    json_results[json_result_key].next_url)

                if json_result_key == 'favorite':
                    json_results[json_result_key] = self.api.user_bookmarks_illust(
                        **next_qs)
                elif json_result_key == 'not_favorite':
                    json_results[json_result_key] = self.api.search_illust(
                        **next_qs)
            """
            try:
                dftest
                dftest2 = pd.DataFrame.from_dict(id_record_dic)
                dftest = dftest.append(dftest2, ignore_index=True)
            except NameError or UnboundLocalError:
                dftest = pd.DataFrame.from_dict(id_record_dic)

            dftest.to_csv(
                "C:/Users/Administrateur/Documents/Illusts_records/Miku_Illusts_record.csv", index=False, sep=',')
"""


a = Pixiv_Miku_Downloader()
C = {keyword: a.get_json(aim=keyword)
     for keyword in ["favorite", "not_favorite"]}
a.handle_datas(json_results=C)
