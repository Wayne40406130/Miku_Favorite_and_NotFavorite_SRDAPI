from pixivpy3 import *
from Pixiv_Miku_DownloaderAPI.Download_CenterAPI import Pixiv_Miku_Download_API  # nopep8
import os
import sys
import csv
import pandas as pd
import time
sys.dont_write_bytecode = True


class Pixiv_Miku_Downloader(Pixiv_Miku_Download_API):

    def __init__(self, aim="favorite", mode="both"):
        aim = aim
        mode = mode

        sni = False
        if not sni:
            self.api = AppPixivAPI()
        else:
            self.api = ByPassSniApi()  # Same as AppPixivAPI, but bypass the GFW
            self.api.require_appapi_hosts()

        self.login_user()
        self.IDrecord_dic = {'favorite': [], 'not_favorite': []}

    def downloader(self,
                   json_results=None,
                   IDrecord_lists=[],
                   member_id=5545356,
                   aim='favorite',
                   count=0,
                   NF_break_value=-1,
                   Illusts_path=os.getcwd()):
        print('aim:'+aim)
        if json_results:
            json_results = self.get_next_queue(json_results=json_results, json_result_key=aim)
            print('get next jsons')
        else:
            json_results = self.get_json(aim=aim, member_id=member_id)
            Illusts_path = self.create_illusts_dir(aim=aim)
            print('start get jsons')

        for idx, illust in enumerate(json_results.illusts):
            if aim == 'not_favorite' and illust.total_bookmarks >= 100 or illust.id in self.IDrecord_dic['favorite']:
                continue
            elif aim=='not_favorite' and illust.id in self.IDrecord_dic['not_favorite']:
                continue
            print("current idx:"+str(idx))
            print("current illust.id:"+str(illust.id))
            print("count:"+str(count))
            print("NF_break_value:"+str(NF_break_value))
            if aim == 'favorite' and illust.id in self.IDrecord_dic['favorite']:
                print('illust.id in old_F_lists')
                return IDrecord_lists
            count += 1
            image_url = []



            if illust.page_count == 1:
                image_url.append(illust.meta_single_page.get('original_image_url', illust.image_urls.large))
            elif illust.page_count > 1:
                for i in illust.meta_pages:
                    image_url.append(i.image_urls.original)
            else:
                continue

            remove_file = False
            if aim == 'favorite' and illust.id in self.IDrecord_dic['not_favorite']:
                remove_file = True

            for a in image_url:
                print(a)
                self.api.download(a, path=Illusts_path, name=None)

                if remove_file:
                    print('remove old illust')
                    old_NF_file_path = os.path.join(self.create_illusts_dir(aim='not_favorite'), os.path.basename(a))
                    print(old_NF_file_path)
                    try:
                        os.remove(old_NF_file_path)
                    except FileNotFoundError:
                        pass
            if remove_file:
                self.IDrecord_dic['not_favorite'].remove(illust.id)

            IDrecord_lists.append(illust.id)

            if count == NF_break_value:
                print('stop!!!!!!!!')
                return IDrecord_lists

        if json_results.next_url:
            time.sleep(1)
            self.downloader(json_results=json_results,
                            IDrecord_lists=IDrecord_lists,
                            aim=aim,
                            count=count,
                            NF_break_value=NF_break_value,
                            Illusts_path=Illusts_path)

        return IDrecord_lists

    def download_bookmark_and_search(self):
        favorite_IDrecord_lists = self.downloader(aim='favorite', member_id=58130520)
        print(favorite_IDrecord_lists)
        self.IDrecord_dic['favorite'] = favorite_IDrecord_lists

        NF_break_value = len(favorite_IDrecord_lists)
        print('NF_break_value:' + str(NF_break_value))

        not_favorite_IDrecord_lists = self.downloader(IDrecord_lists=[], aim='not_favorite',
                                                                   NF_break_value=NF_break_value)
        print(not_favorite_IDrecord_lists)
        self.IDrecord_dic['not_favorite'] = not_favorite_IDrecord_lists

        print(self.IDrecord_dic)
        df = pd.DataFrame.from_dict(self.IDrecord_dic)
        print(df)
        df.to_csv("Miku_Illusts_record.csv", index=False)

    def update_bookmark_and_search(self):
        old_DF_records = pd.read_csv('Miku_Illusts_record.csv')
        print(old_DF_records)
        self.IDrecord_dic = {'favorite': old_DF_records['favorite'].tolist(),
                        'not_favorite': old_DF_records['not_favorite'].tolist()
                        }
        print(self.IDrecord_dic)

        new_favorite_lists = self.downloader(aim='favorite', member_id=58130520)
        current_favorite_lists = new_favorite_lists + self.IDrecord_dic['favorite']

        print(len(current_favorite_lists))
        print(len(self.IDrecord_dic['not_favorite']))
        self.IDrecord_dic['favorite'] = current_favorite_lists
        print(self.IDrecord_dic)
        NF_break_value = len(current_favorite_lists) - len(self.IDrecord_dic['not_favorite'])

        if NF_break_value ==0:
            print('not any more new bookmark')
            return

        new_not_favorite_lists = self.downloader(IDrecord_lists=[], aim='not_favorite',
                                                            NF_break_value=NF_break_value)
        current_not_favorite_lists = new_not_favorite_lists + self.IDrecord_dic['not_favorite']
        self.IDrecord_dic['not_favorite'] = current_not_favorite_lists
        df = pd.DataFrame.from_dict(self.IDrecord_dic)
        print(df)
        #df.to_csv("Miku_Illusts_record.csv", index=False)


API=Pixiv_Miku_Downloader()
API.update_bookmark_and_search()