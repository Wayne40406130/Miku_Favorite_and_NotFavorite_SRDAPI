from pixivpy3 import *
import os
import sys
import csv
import pandas as pd
sys.dont_write_bytecode = True


class Pixiv_Miku_Download_API(object):
    _USERNAME = "userbay"
    _PASSWORD = "userpay"

    def __init__(self, aim="favorite", **requests_kwargs):
        self.aim = aim
        sni = False
        if not sni:
            self.api = AppPixivAPI()
        else:
            self.api = ByPassSniApi()  # Same as AppPixivAPI, but bypass the GFW
            self.api.require_appapi_hosts()

    def login_user(self, username=_USERNAME, password=_PASSWORD):
        self.api.login(username, password)

    def create_illusts_dir(self, Illusts_path="C:/Users/Administrateur/Pictures/Illusts", aim="favorite"):
        Illusts_path_favorite = os.path.join(Illusts_path, aim)
        if not os.path.exists(Illusts_path_favorite):
            os.makedirs(Illusts_path_favorite)
        return Illusts_path_favorite

    def create_illusts_records(self,
                               Record_path="C:/Users/Administrateur/Documents/Illusts_records",
                               Record_filename="Miku_Illusts_record.csv"):
        Record_path_filename = os.path.join(Record_path, Record_filename)
        if not os.path.isfile(Record_path_filename):
            with open(Record_path_filename, "w", newline='') as csvFile:
                writer = csv.writer(csvFile, delimiter=',')
                writer.writerow(["favorite", "not_favorite"])

    def get_json(self, aim="favorite"):
        if aim == 'favorite':
            json_results = self.api.user_bookmarks_illust(
                5545356, filter=None, req_auth=True, tag="初音ミク")
        elif aim == 'not_favorite':
            json_results = self.api.search_illust('初音ミク',
                                                  search_target='partial_match_for_tags',
                                                  sort='date_desc',
                                                  )
        return json_results

    def get_next_queue(self, json_results, json_result_key='favorite'):
        next_qs = self.api.parse_qs(
            json_results[json_result_key].next_url)

        if json_result_key == 'favorite':
            json_results[json_result_key] = self.api.user_bookmarks_illust(
                **next_qs)
        elif json_result_key == 'not_favorite':
            json_results[json_result_key] = self.api.search_illust(
                **next_qs)

        return json_results


"""

AAA = Pixiv_Miku_Download_API()
AAA.login_user()
WWW = AAA.get_json(aim="favorite")
print(WWW)
WWW = {x:AAA.get_json(x) for x in ["favorite", "not_favorite"]}
for i in WWW["favorite"].illusts:
    print(i.id)
"""
