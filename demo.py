from Pixiv_Miku_DownloaderAPI.Download_CenterAPI import *
from pixivpy3 import *
import os
import time
import pandas as pd
import shutil
import copy

sni = False
if not sni:
    api = AppPixivAPI()
else:
    api = ByPassSniApi()  # Same as AppPixivAPI, but bypass the GFW
    api.require_appapi_hosts()

MDapi=Pixiv_Miku_Download_API()
MDapi.login_user()

IDrecord_dic={}





def download_bookmark_and_search(json_results=None,
                                 IDrecord_lists=[],
                                 member_id=5545356,
                                 aim='favorite',
                                 count=0,
                                 NF_break_value=-1,
                                 Illusts_path=os.getcwd()):

    if json_results:
        json_results=MDapi.get_next_queue(json_results=json_results,json_result_key=aim)
    else:
        json_results=MDapi.get_json(aim=aim,member_id=member_id)
        Illusts_path=MDapi.create_illusts_dir(aim=aim)

    for idx, illust in enumerate(json_results.illusts):
        if aim=='not_favorite' and illust.total_bookmarks>=100 or illust.id in IDrecord_dic['favorite']:
            continue
        image_url = []
        print(idx)
        print(illust)
        count+=1
        print(count)
        print(NF_break_value)

        if illust.page_count == 1:
            image_url.append(illust.meta_single_page.get('original_image_url', illust.image_urls.large))
        elif illust.page_count > 1:
            for i in illust.meta_pages:
                image_url.append(i.image_urls.original)
        else:
            continue

        for a in image_url:
            api.download(a, path=Illusts_path, name=None)
            print(a)
        IDrecord_lists.append(illust.id)

        if count == NF_break_value:
            print('stop!!!!!!!!')
            return IDrecord_lists

    if json_results.next_url:
        time.sleep(1)
        download_bookmark_and_search(json_results=json_results,
                                     IDrecord_lists=IDrecord_lists,
                                     aim=aim,
                                     count=count,
                                     NF_break_value=NF_break_value,
                                     Illusts_path=Illusts_path)

    return IDrecord_lists
        



def update_bookmark_and_search(json_results=None,
                               IDrecord_lists=[],
                               member_id=5545356,
                               aim='favorite',
                               count=0,
                               NF_break_value=-1,
                               Illusts_path=os.getcwd()):


    if json_results:
        json_results=MDapi.get_next_queue(json_results=json_results,json_result_key=aim)
    else:
        json_results=MDapi.get_json(aim=aim,member_id=member_id)
        Illusts_path=MDapi.create_illusts_dir(aim=aim)

    for idx, illust in enumerate(json_results.illusts):
        if aim=='not_favorite' and illust.total_bookmarks>=100 or illust.id in IDrecord_dic['favorite']:
            continue
        print(idx)
        print(illust)
        print(count)
        print(NF_break_value)
        if aim=='favorite' and illust.id in IDrecord_dic['favorite']:
            print('illust.id in old_F_lists')
            return IDrecord_lists
        image_url = []

        count+=1

        if illust.page_count == 1:
            image_url.append(illust.meta_single_page.get('original_image_url', illust.image_urls.large))
        elif illust.page_count > 1:
            for i in illust.meta_pages:
                image_url.append(i.image_urls.original)
        else:
            continue

        remove_file=False
        if aim == 'favorite' and illust.id in IDrecord_dic['not_favorite']:
            remove_file=True

        for a in image_url:
            print(a)
            api.download(a, path=Illusts_path, name=None)

            if remove_file:
                print('remove old illust')
                old_NF_file_path = os.path.join(MDapi.create_illusts_dir(aim='not_favorite'), os.path.basename(a))
                print(old_NF_file_path)
                # os.remove(old_NF_file_path)
        if remove_file:
            IDrecord_dic['not_favorite'].remove(illust.id)



        IDrecord_lists.append(illust.id)

        if count == NF_break_value:
            print('stop!!!!!!!!')
            return IDrecord_lists

    if json_results.next_url:
        time.sleep(1)
        download_bookmark_and_search(json_results=json_results,
                                     IDrecord_lists=IDrecord_lists,
                                     aim=aim,
                                     count=count,
                                     NF_break_value=NF_break_value,
                                     Illusts_path=Illusts_path)

    return IDrecord_lists





"""
favorite_IDrecord_lists=download_bookmark_and_search(aim='favorite',member_id=58130520)
print(favorite_IDrecord_lists)
IDrecord_dic={'favorite':favorite_IDrecord_lists}

NF_break_value=len(favorite_IDrecord_lists)
print('NF_break_value:'+str(NF_break_value))


not_favorite_IDrecord_lists=download_bookmark_and_search(IDrecord_lists=[],aim='not_favorite',NF_break_value=NF_break_value)
print(not_favorite_IDrecord_lists)
IDrecord_dic['not_favorite']=not_favorite_IDrecord_lists

print(IDrecord_dic)
df=pd.DataFrame.from_dict(IDrecord_dic)
print(df)
df.to_csv("Miku_Illusts_record.csv", index=False)
"""

old_DF_records = pd.read_csv('Miku_Illusts_record.csv')
print(old_DF_records)
IDrecord_dic={'favorite':old_DF_records['favorite'].tolist(),
              'not_favorite':old_DF_records['not_favorite'].tolist()
              }
print(IDrecord_dic)




new_favorite_lists=update_bookmark_and_search(aim='favorite',member_id=58130520)
current_favorite_lists=new_favorite_lists+IDrecord_dic['favorite']

print(len(current_favorite_lists))
print(len(IDrecord_dic['not_favorite']))
IDrecord_dic['favorite']=current_favorite_lists
print(IDrecord_dic)
NF_break_value=len(current_favorite_lists)-len(IDrecord_dic['not_favorite'])

new_not_favorite_lists=update_bookmark_and_search(IDrecord_lists=[],aim='not_favorite',NF_break_value=NF_break_value)
current_not_favorite_lists=new_not_favorite_lists+IDrecord_dic['not_favorite']
IDrecord_dic['not_favorite']=current_not_favorite_lists
df=pd.DataFrame.from_dict(IDrecord_dic)
print(df)