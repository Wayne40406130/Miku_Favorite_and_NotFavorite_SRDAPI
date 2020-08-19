from Pixiv_Miku_DownloaderAPI.Download_CenterAPI import *
from pixivpy3 import *
import os
import time
import pandas as pd


sni = False
if not sni:
    api = AppPixivAPI()
else:
    api = ByPassSniApi()  # Same as AppPixivAPI, but bypass the GFW
    api.require_appapi_hosts()

MDapi=Pixiv_Miku_Download_API()
MDapi.login_user()

IDrecord_lists=[]

def download_bookmark_and_search(json_results=None,aim='favorite',count=0,NF_break_value=-1,Illusts_path=os.getcwd()):
    if json_results:
        json_results=MDapi.get_next_queue(json_results=json_results,json_result_key=aim)
    else:
        json_results=MDapi.get_json(aim=aim,member_id=58130520)
        Illusts_path=MDapi.create_illusts_dir(aim=aim)

    for idx, illust in enumerate(json_results.illusts):
        if aim=='not_favorite' and illust.total_bookmarks>=100:
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
        IDrecord_lists.append(illust.id)

        if count == NF_break_value:
            print('stop!!!!!!!!')
            return

    if json_results.next_url:
        time.sleep(1)
        download_bookmark_and_search(json_results=json_results,aim=aim,count=count,NF_break_value=NF_break_value,Illusts_path=Illusts_path)
        



def update_bookmark_and_search():
    pass





download_bookmark_and_search(aim='favorite')
IDrecord_dic={'favorite':IDrecord_lists}

NF_break_value=len(IDrecord_lists)
print('NF_break_value:'+str(NF_break_value))
IDrecord_lists=[]

download_bookmark_and_search(aim='not_favorite',NF_break_value=NF_break_value)
IDrecord_dic['not_favorite']=IDrecord_lists

print(IDrecord_dic)
df=pd.DataFrame.from_dict(IDrecord_dic)
print(df)
df.to_csv("Miku_Illusts_record.csv", index=False)