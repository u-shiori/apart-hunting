import os
import urllib.request, json
import urllib.parse
from datetime import datetime as dt

import requests
import pandas as pd
from retry import retry
from bs4 import BeautifulSoup

### SETTING START
# suumo
base_url = "https://suumo.jp/jj/chintai/ichiran/FR301FC011/?ar=030&bs=040&fw2=&pc=30&po1=00&po2=99&fw=%E5%86%86&md=04&md=06&md=07&md=09&md=10&md=12&md=13&cb=9.5&ct=10.0&et=5&mb=40&mt=9999999&cn=9999999&co=1&tc=0400101&tc=0400501&tc=0400502&tc=0400301&tc=0400304&tc=0400905&tc=0400906&shkr1=03&shkr2=03&shkr3=03&shkr4=03"

# googlemap
destination = "〒105-0022 東京都港区海岸１丁目７−１ 東京ポートシティ竹芝オフィスタワ".replace(' ','+') #目的地住所
# api_key = ''
"""
もし「車」の移動時間を算出したいなら上記のapi_keyにGCPのAPI keyを入力し、18行目・36-51行目・100行目のコメントアウトを外す。
→ 参考(スタートガイド) : https://developers.google.com/maps/gmp-get-started?hl=ja
ただし、下手するとお金がかかり、結局「電車」の移動時間は算出できないため非推奨。
→ 参考(日本では無料で路線検索できない) : https://note.com/jinka1997/n/n182603e52c3e
"""
### SETTING END


@retry(tries=3, delay=10, backoff=2)
def get_html(page):
    url = base_url + f"&page={page}"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup
all_data = []

def get_map(origin):
    """
    endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'
    origin = origin.replace(' ','+')
    nav_request = 'language=ja&origin={}&destination={}&mode=driving&key={}'.format(origin,destination,api_key)
    nav_request = urllib.parse.quote_plus(nav_request, safe='=&')
    request = endpoint + nav_request
    #Google Maps Platform Directions APIを実行
    response = urllib.request.urlopen(request).read()
    directions = json.loads(response)
    try:
        route = directions['routes'][0]
        driving_distance = route['legs'][0]['distance']['value']
    except IndexError:
        driving_distance = None
        route = None
    """
    driving_distance = None
    transit_url = f"https://www.google.com/maps/dir/?api=1&language=ja&origin={origin}&destination={destination}"
    return driving_distance, transit_url

num_page = 1
while True:
    
    # get html
    soup = get_html(num_page)
    
    # extract all items
    headers = soup.findAll("div", {"class": "property-header"})
    bodys = soup.findAll("div", {"class": "property-body"})
    assert len(headers)==len(bodys)
    print("page", num_page, "items", len(headers))
    if len(headers)==0:
        break
        
    
    # process each item
    for header, body in zip(headers, bodys):
        # define variable 
        data = {}
        # collect base information    
        data["名称"] = header.find("a", {"class": "js-cassetLinkHref"}).getText().strip()

        tmp_div = body.find("div", {"class": "detailbox-property-point"}).getText().strip()
        data["家賃"] = int(float(tmp_div[:-2])*10000)

        tmp_td1 = body.find("td", {"class": "detailbox-property-col detailbox-property--col1"})
        tmp_td1 = tmp_td1.findAll("div")[1].getText().strip()
        if '-' in tmp_td1:
            data["管理費"] = 0
        else:
            data["管理費"] = int(tmp_td1[4:-1])
        data["家賃+管理費"] = data["家賃"] + data["管理費"]
        
        tmp_td2 = body.find("td", {"class": "detailbox-property-col detailbox-property--col2"}).getText().strip().split('\n')
        data["敷金"], data["礼金"] = tmp_td2[:2]
        
        tmp_td3s = body.findAll("td", {"class": "detailbox-property-col detailbox-property--col3"})
        data["間取り"], data["面積"], data["向き"] = tmp_td3s[0].getText().strip().split('\n\n')
        data["種別"], data["築年"] = tmp_td3s[1].getText().strip().split('\n\n')
        
        data["住所"] = body.findAll("td",{"class":"detailbox-property-col"})[-1].getText().strip()
        data["交通"] = body.findAll("div",{"class":"detailnote-box"})[0].getText().strip().replace('\n',' or ')

        tmp_distance, tmp_url = get_map(data["住所"])
        # data["目的地までの車距離(m)"] = tmp_distance
        data["目的地までの交通機関URL"] = tmp_url

        data["SUUMOのURL"] = "https://suumo.jp" + header.find("a", {"class": "js-cassetLinkHref"}).get("href")
        
        all_data.append(data)    

    num_page += 1

# convert to dataframe
os.makedirs(f"../result/{str(dt.now())[:10]}", exist_ok=True)
df = pd.DataFrame(all_data)
df.to_csv(f"../result/{str(dt.now())[:10]}/suumo.csv",index=False)
