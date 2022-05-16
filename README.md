# 注意
スクレイピングの利用規約や禁止事項について一切調査しておりません。

そのため、不用意な拡散は避けていただけると幸いです。

# 実行手順
1. 必要なライブラリのインストール
    ```
    pip install -r requirements.txt
    ```

2. `src`ディレクトリに移動し次の通り設定を変更
    - `1-scraping.py`の l11-l24 を変更
        - `base_url`(l13) : 記載のURLを、自分の好きな条件で再検索し上書き
        - `destination`(l16) : 物件からの移動時間を算出したい目的地（Google mapで調べた際に表示される住所が望ましい）
        - `api_key`(l17) : 
          -  もし「車」の移動時間を算出したいなら上記の`api_key`にGCPのAPI keyを入力し、18行目・36-51行目・100行目のコメントアウトを外す。
          -   → 参考 : [GCP スタートガイド](https://developers.google.com/maps/gmp-get-started?hl=ja)
          -  ただし、下手するとお金がかかり、結局「電車」の移動時間は算出できないため非推奨。
          -   → 参考 : [日本では無料で路線検索できない](https://note.com/jinka1997/n/n182603e52c3e)
    - `3-chrome.py`の l49 を変更
        - `"10:00"` : 上で設定した目的地に何時までに到着したいか

3. 実行
    ```
    sh run.sh
    ```
    ※ chromeが起動し始めたら時間がかかるため気長に待つべし。
    
    ※ chromeの起動は処理が重たいため他の作業は控えるべし。
    
    → `../result/{日付}/`直下にcsvファイルが保存されていれば成功。

# ファイル構造
```
.
├── README.txt
├── requirements.txt
├── result
│   └── 2022-05-16 : 実行した日付
│       ├── suumo.csv : 1-scraping.pyの出力
│       ├── suumo_wo_same.csv : 2-delete_same.pyの出力（重複物件を削除）
│       ├── suumo_wo_same_w_transit.csv : 3-chrome.pyの出力（乗り換え回数と移動時間を追加）
│       │                                 ※ 経路が複数ある場合は、乗り換え回数が最も少ない経路の移動時間を採用
│       │                                 ※ 乗り換え回数はたまに正確じゃないのでお許しを(もっと良い算出方法があれば教えてください)
│       └── suumo_wo_same_wo_norikae.csv : 3-chrome.pyの出力（目的地まで乗り換えの必要が無い物件のみを抽出）
└── src
    ├── 1-scraping.py : suumoの検索結果から必要な情報のみを抽出する
    ├── 2-delete_same.py : 「同じ物件だが不動産が違う」物件が多数存在するため、それらを重複とみなし削除する
    ├── 3-chrome.py : 到着時間に対する物件から目的地までの移動時間と乗り換え回数を求める
    └── run.sh
```
