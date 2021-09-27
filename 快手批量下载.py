import sys
import requests
import json
from lxml import etree
import os
import re

rstr = r"[\/\\\:\*\?\"\<\>\|]"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Cookie': 'did=web_d9b1b11c6fa6404a9bd20f4f09441c40; didv=1629200954000; clientid=3; client_key=65890b29; kpn=GAME_ZONE; soft_did=1619580708547; kuaishou.live.bfb1s=9b8f70844293bed778aade6e0a8f9942; userId=97328167; userId=97328167; kuaishou.live.web_st=ChRrdWFpc2hvdS5saXZlLndlYi5zdBKgASM2p8Ps1XwSMzr3xx64e0-SMw4QEDwe3IcrT1BK_BWfslbszg5uWLRHyMiONKxSKCTarAtx167cWl3E42L_oSoEq7M5AEzWUnj4ru285GeX2tS1ayaCPz2JjCRt1mmOk94XlJePJpDAuOdKKj3HtiIN1Knj5Pdy_ra0qgA1IBtjYpYq4ZWsMy-MvfROlCviNMSroJ4L3Qw3RlWtFGgmD_8aEnkpvegnDUJtgj96dZ26lsX47iIgOjpintLTdcyh3XjSrPl-NXdLrbA3837LH5n-2GSaQR0oBTAB; kuaishou.live.web_ph=526be5bf092f06b5bdee8f93184eb2376c71',
}
print('获取作者的主页链接请到:https://live.kuaishou.com/,搜索你要喜欢的作者，打开他的主页将链接复制到本程序。')
author_url = input('请输入你要下载的作者的链接:')
print('正在访问作者主页')
resp1 = requests.get(url=author_url, headers=headers)
html = etree.HTML(resp1.text)
dirname = html.xpath('/html/head/title/text()')[0].strip()
dirname = re.sub(rstr, ' ', dirname).split('的')[0]
headers['Content-Type'] = 'application/json'
principalId = author_url.split('/')[-1]
video_url_list = []
video_name_list = []
img_url_dict = {}
pcursor = ""
url = 'https://live.kuaishou.com/live_graphql'
print('正在获取作者视频链接')
while True:
    data = {"operationName": "privateFeedsQuery",
            "variables": {"principalId": principalId, "pcursor": pcursor, "count": 24},
            "query": "query privateFeedsQuery($principalId: String, $pcursor: String, $count: Int) {\n  privateFeeds(principalId: $principalId, pcursor: $pcursor, count: $count) {\n    pcursor\n    list {\n      id\n      thumbnailUrl\n      poster\n      workType\n      type\n      useVideoPlayer\n      imgUrls\n      imgSizes\n      magicFace\n      musicName\n      caption\n      location\n      liked\n      onlyFollowerCanComment\n      relativeHeight\n      timestamp\n      width\n      height\n      counts {\n        displayView\n        displayLike\n        displayComment\n        __typename\n      }\n      user {\n        id\n        eid\n        name\n        avatar\n        __typename\n      }\n      expTag\n      isSpherical\n      __typename\n    }\n    __typename\n  }\n}\n"}
    resp = requests.post(url=url, headers=headers, data=json.dumps(data))
    url_list = resp.json()['data']['privateFeeds']['list']
    # print(resp.json())
    for i in url_list:
        if i['imgUrls']:
            img_url_dict[i['caption']] = i['imgUrls']
            continue
        video_url_list.append(i['id'])
        name = re.sub(rstr, ' ', i['caption'].strip()).replace('\n', '')
        name = name[:25] if len(name) > 25 else name
        video_name_list.append(name)
    pcursor = resp.json()['data']['privateFeeds']['pcursor']
    if pcursor == "no_more":
        break
path = os.path.join(os.getcwd(), dirname)
if not os.path.exists(path):
    os.mkdir(path)
os.chdir(path)
for i in range(len(video_url_list) - 1, -1, -1):
    num = len(video_url_list) - i
    print(f'正在下载第{num}/{len(video_url_list)}' + '------------------------------' + video_name_list[i])
    data = {"operationName": "SharePageQuery", "variables": {"photoId": video_url_list[i], "principalId": principalId},
            "query": "query SharePageQuery($principalId: String, $photoId: String) {\n  feedById(principalId: $principalId, photoId: $photoId) {\n    currentWork {\n      playUrl\n      __typename\n    }\n    __typename\n  }\n}\n"}
    # print(data)
    resp2 = requests.post(url=url, headers=headers, data=json.dumps(data))
    # print(resp2.json())
    download_url = resp2.json()['data']['feedById']['currentWork']['playUrl']
    with open(str(num) + '-' + video_name_list[i] + '.mp4', 'wb') as f:
        resp3 = requests.get(url=download_url)
        f.write(resp3.content)
    print('下载完成' + '------------------------------' + video_name_list[i])
