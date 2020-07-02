import os
import sys
import csv
import pandas as pd
sys.dont_write_bytecode = True

from pixivpy3 import *

_USERNAME = "userbay"
_PASSWORD = "userpay"

def main():
    sni = False
    if not sni:
        api = AppPixivAPI()
    else:
        api = ByPassSniApi()  # Same as AppPixivAPI, but bypass the GFW
        api.require_appapi_hosts()
    api.login(_USERNAME, _PASSWORD)

    json_result = api.search_illust('初音ミク',
                                     search_target='partial_match_for_tags',
                                     sort='date_desc',
                                     )

    Illusts_path="C:/Users/Administrateur/Pictures/Illusts"
    Illusts_path_not_favorite=os.path.join(Illusts_path,"not_favorite")
    if not os.path.exists(Illusts_path_not_favorite):
        os.makedirs(Illusts_path_not_favorite)

    Record_path="C:/Users/Administrateur/Documents/Illusts_records"
    Record_filename="Miku_Illusts_record.csv"
    Record_path_filename=os.path.join(Record_path,Record_filename)
    if not os.path.isfile(Record_path_filename):
        with open(Record_path_filename, "w", newline='') as csvFile:
            writer = csv.writer(csvFile, delimiter=',')
            writer.writerow(["favorite","not_favorite"])


    # download all tags "初音ミク" not_bookmarks to 'favorite' dir
    df = pd.read_csv('C:\\Users\\Administrateur\\Documents\\Illusts_records\\Miku_Illusts_record.csv')
    favorite_list = list(df['favorite'])
    not_favorite_list=list(df['not_favorite'])
    last_page=False
    count=0
    while not last_page and count!=df.shape[0]:
        print('!!')
        if not json_result.next_url:
            last_page=True
        for idx, illust in enumerate(json_result.illusts):
            image_url=[]
            if count==df.shape[0]:
                break
            if illust.id in favorite_list or illust.id in not_favorite_list:
                continue
            if illust.page_count==1:
                image_url.append(illust.meta_single_page.get('original_image_url', illust.image_urls.large))
            elif illust.page_count>1:
                for i in illust.meta_pages:
                    image_url.append(i.image_urls.original)
            else:
                continue
            print("%s: %s" % (illust.title, image_url))
            print("id:%s" %(illust.id))
            df.loc[count,'not_favorite']=str(illust.id)
            print(df)
            count+=1
            print(count)

            for a in image_url:
                api.download(a, path=Illusts_path_not_favorite, name=None)
        if count!=df.shape[0]:
            next_qs = api.parse_qs(json_result.next_url)
            json_result = api.search_illust(**next_qs)
    df.to_csv('test.csv',index=False,sep=',')

if __name__ == '__main__':
    main()
