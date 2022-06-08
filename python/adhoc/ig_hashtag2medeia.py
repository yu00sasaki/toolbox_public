# coding:utf-8

import os
import csv
import argparse
import traceback



def conf_reader(conf_path='conf/conf.yaml'):
    """
    設定ファイルのロード
     - instagram:
        user_id: 認証ユーザのID
        access_token: サードトークン
    """
    with open(conf_path) as fd:
        conf_dic = yaml.safe_load(fd)
    return conf_dic



def hashid2media(hash_id, conf_dic_path, limit, output_path, type):
    """
    ハッシュidからメディア情報を取得する
    type: 1・・・最新の投稿
    Args:
        hash_id (str): ハッシュIDを引くクエリ
        conf_dic_path (str): configのパス
        limit(int): 取得数の上限
        output_path(str): 保存ディレクトリ
        type(int): type=1: 最新の投稿
    Returns:
        None
    """
    conf_dic = conf_reader(conf_dic_path)
    #ディレクトリ作成
    output_dir = pathlib.Path(output_path)
    if output_dir.exists():
        print(f"{output_dir}が既に存在しています")
        pass
    else:
        output_dir.mkdir()

    q, mod = divmod(limit, 25)
    if mod == 0:
        exrtract_num = q
    else:
        exrtract_num = q + 1

    search_type = "top_media"
    if type == "1":
        search_type = "recent_media"


    BASE_URL = "https://graph.facebook.com/v9.0/{HASH_ID}/{SEARCH_TYPE}?user_id={USER_ID}&fields={FIELDS}&access_token={ACCESS_TOKEN}"
    #fieldsには特殊文字が入る可能性があるので変数で分離
    fields = "media_url,media_type,permalink,caption,like_count,comments_count,timestamp"
    req_url = BASE_URL.format(SEARCH_TYPE=search_type, HASH_ID=hash_id, USER_ID=conf_dic["instagram"]["user_id"], FIELDS=fields, ACCESS_TOKEN=conf_dic["instagram"]["access_token"])
    response = requests.get(req_url)
    res_json = json.loads(response.text)

    if "error" in res_json or not "data" in res_json:
        print("data extract error")
        return
    else:
        file_path = f"output0.json"

    #保存
    with open(output_dir/file_path , 'w') as outfile:
        json.dump(res_json, outfile)

    #limit分繰り返す
    for num in range(1, exrtract_num):
        req_url = res_json['paging']['next']
        response = requests.get(req_url)
        res_json = json.loads(response.text)

        if "error" in res_json or not "data" in res_json:
            print("data extract error")
            break
        else:
            file_path = f"output{num}.json"
            with open(output_dir/file_path , 'w') as outfile:
                json.dump(res_json, outfile)

    return

def media2image(mediadir, imagedir, type):
    """
    ハッシュメディアJSONファイルから画像を取得する
    type=1: hashメディア
    type=2: userメディア
    Args:
        mediadir (str): 対象のディレクトリ
        imagedir (str): 保存ディレクトリ
        type(int): type=1: hashメディア, type=2: userメディア
    Returns:
        None
    """
    media_dir = pathlib.Path(mediadir)
    file_list = list(media_dir.glob("*.json"))

    image_dir = pathlib.Path(imagedir)
    if not image_dir.exists():
          image_dir.mkdir()

    counter = 0

    for file in file_list:
        with open(file) as fd:
            insta_data = json.load(fd)
        if type==1:
            medias = insta_data["data"]
        elif type==2:
            medias = insta_data["business_discovery"]["media"]["data"]
        else:
            print("not supported...")
            raise Exception("type option error")
        for media in medias:
            #IMAGEデータのみ分析する
            if not media["media_type"] == "IMAGE":
                continue
            #画像のダウンロード
            media_url = media["media_url"]
            response = requests.get(media_url)
            image = response.content
            with open(image_dir/f"image{counter}.jpg" , "wb") as imd:
                imd.write(image)
            counter+=1

    return



"""
ハッシュタグリストから投稿情報と画像データをスクレイプする
"""

def main():
    parser = argparse.ArgumentParser(description='batch tool')
    parser.add_argument('--hashtag_list_path', default='conf/hashtag_list.csv', help='relative list path')
    parser.add_argument('--conf_path', default='conf/conf.yaml', help='relative conf path')
    parser.add_argument('--limit', default=100, help='the total number of data')
    args = parser.parse_args()

    #作業ディレクトリが無い場合新規に作成する
    os.makedirs('data', exist_ok=True)

    action_type = input('ハッシュタグ単体:1, ハッシュタグリスト:2, default:ハッシュタグ単体\n')
    if action_type == '1' or action_type == '':
        query = input('ハッシュタグを入力してください\n')
        if query == '':
            print('このタイプはサポートされていません')
            exit()
        hashtag_list_path = ''

    elif action_type == '2':
        hashtag_list_path = input('ハッシュタグリストパスを入力してください, default: conf/hashtag_list.csv\n')
        if hashtag_list_path == '':
            hashtag_list_path = args.hashtag_list_path
    else:
        print('このタイプはサポートされていません')
        exit()

    limit = input('取得数を入力してください, default: 100\n')
    if limit == '':
        limit = 100
    try:
        limit = int(limit)
    except:
        print('このタイプはサポートされていません')
        exit()

#メイン処理
    if hashtag_list_path == '':
        try:
            print('{}を処理しています。'.format(query))
            hashid = query2hashid(query, args.conf_path)
            #hashidを書き込む処理
            os.makedirs(f'data/{hashid}', exist_ok=True)
            with open(f'data/{hashid}/hashid.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['クエリ', 'ID'])
                writer.writerow([query, hashid])

            hashid2media(hashid, args.conf_path, limit, f"data/{hashid}", 2)
            media2image(f"data/{hashid}", f"data/{hashid}_img", 1)
        except Exception as e:
            traceback.print_exc()
            print('データ抽出に失敗しました。ログを確認してください')
            exit()
    else:
        try:
            with open(hashtag_list_path, "r") as fd:
                for line in fd:
                    query = line.rstrip()
                    print('{}を処理しています。'.format(query))
                    hashid = query2hashid(query, args.conf_path)
                    #hashidを書き込む処理
                    os.makedirs(f'data/{hashid}', exist_ok=True)
                    with open(f'data/{hashid}/hashid.csv', 'w') as f:
                        writer = csv.writer(f)
                        writer.writerow(['クエリ', 'ID'])
                        writer.writerow([query, hashid])
                    hashid2media(hashid, args.conf_path, limit, f"data/{hashid}", 2)
                    media2image(f"data/{hashid}", f"data/{hashid}_img", 1)
        except Exception as e:
            traceback.print_exc()
            print('データ抽出に失敗しました。ログを確認してください')
            exit()

    print('データ抽出を完了しました')


if __name__ == '__main__':
    main()
