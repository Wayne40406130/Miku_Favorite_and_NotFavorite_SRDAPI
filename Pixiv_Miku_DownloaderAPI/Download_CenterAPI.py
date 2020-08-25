from pixivpy3 import *
import os
import sys
import csv
import pandas as pd
import attr
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

    def create_illusts_dir(self, Illusts_path=os.path.join(os.getcwd(),"test_illusts"), aim="favorite"):
        Illusts_path_favorite = os.path.join(Illusts_path, aim)
        if not os.path.exists(Illusts_path_favorite):
            os.makedirs(Illusts_path_favorite)
        return Illusts_path_favorite

    def create_illusts_records(self,
                               Record_path=os.getcwd(),
                               Record_filename="Miku_Illusts_record.csv"):
        Record_path_filename = os.path.join(Record_path, Record_filename)
        if not os.path.isfile(Record_path_filename):
            with open(Record_path_filename, "w", newline='') as csvFile:
                writer = csv.writer(csvFile, delimiter=',')
                writer.writerow(["favorite", "not_favorite"])

    def get_json(self, aim="favorite",member_id=5545356):
        if aim == 'favorite':
            json_results = self.api.user_bookmarks_illust(
                member_id, filter=None, req_auth=True, tag="初音ミク")
        elif aim == 'not_favorite':
            json_results = self.api.search_illust('初音ミク',
                                 search_target='partial_match_for_tags',
                                 sort='date_desc',
                                 end_date='2020-05-01'
                                 )
        return json_results

    def get_next_queue(self, json_results, json_result_key='favorite'):

        search_function = {'favorite': self.api.user_bookmarks_illust,
                           'not_favorite': self.api.search_illust}
        next_qs = self.api.parse_qs(
            json_results.next_url)

        json_results= search_function[json_result_key](**next_qs)

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
