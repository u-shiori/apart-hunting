from copy import deepcopy
from time import sleep
from datetime import datetime as dt

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def get_time(time_str):
    hour = 0
    if '時間' in time_str:
        tmp_hour, time_str = time_str.split('時間')
        hour = int(tmp_hour)*60
    if len(time_str)==0:
        minute = 0
    else:
        minute = time_str.split('分')[0]
    time = int(minute) + hour
    return time


def main(url):
    try:
        #2
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.implicitly_wait(10)

        driver.get(url)
        driver.implicitly_wait(10)

        #3
        elem_train = driver.find_element(by=By.XPATH, value='//*[@id="omnibox-directions"]/div/div[2]/div/div/div[1]/div[3]/button')
        elem_train.click()
        driver.implicitly_wait(10)
        
        try:
            try:
                elem_pulldown = driver.find_element(by=By.XPATH, value='//*[@id="pane"]/div/div[1]/div/div/div[2]/span/div/div/div/div[2]')
            except:
                elem_pulldown = driver.find_element(by=By.XPATH, value='//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/span/div')

            elem_pulldown.click()
            driver.implicitly_wait(10)
        
            try:
                elem_arrival = driver.find_element(by=By.XPATH, value='//*[@id=":2"]')
                elem_arrival.click()
                driver.implicitly_wait(10)
                try:
                    try:
                        elem_time = driver.find_element(by=By.XPATH, value='//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/span[1]/input')
                    except:
                        elem_time = driver.find_element(by=By.NAME, value="transit-time")
                    elem_time.clear()
                    driver.implicitly_wait(10)
                    elem_time.send_keys("10:00")
                    sleep(1)
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)


        #4
        min_norikae = 100
        time_delta = None
        trip_texts = [deepcopy(elem_trip.text) for elem_trip in driver.find_elements(by=By.CLASS_NAME, value="UgZKXd") ]
        for trip_text in trip_texts:
            if len(trip_text)==0:
                continue
            if not (len(trip_text.split('\n'))>=3):
                continue
            if len(trip_text.split('\n')[2])==0:
                continue
            norikae = len(trip_text.split('\n')[2].split(' ')) - 1 # 乗り換え回数
            print("乗り換え", norikae)
            print(trip_text)
            print()
            if min_norikae > norikae:
                min_norikae = norikae
                time_delta = get_time(trip_text.split('\n')[0]) # 移動時間

        current_url = driver.current_url
        #5
        driver.close()

        norikae = min_norikae
        print("Succeed")
    except Exception as e:
        # 失敗した場合も閉じておく
        print(e)
        print("Fail")
        norikae = None
        time_delta = None
        current_url = url
        driver.close()
    return norikae, time_delta, current_url

if __name__ == "__main__":
    df = pd.read_csv(f"../result/{str(dt.now())[:10]}/suumo_wo_same.csv")
    norikaes = list()
    time_deltas = list()
    urls = list()
    for _, row in df.iterrows():
        norikae, time_delta, url = main(row["目的地までの交通機関URL"])
        norikaes.append(norikae)
        time_deltas.append(time_delta)
        urls.append(url)
    df["目的地までの乗り換え数"] = norikaes
    df["目的地までの電車時間(分)"] = time_deltas
    del df["目的地までの交通機関URL"]
    df["目的地までの交通機関URL"] = urls
    df = df.sort_values("目的地までの電車時間(分)")
    df.to_csv(f"../result/{str(dt.now())[:10]}/suumo_wo_same_w_transit.csv", index=False)

    df = df[df["目的地までの乗り換え数"]<=0]
    df.to_csv(f"../result/{str(dt.now())[:10]}/suumo_wo_same_wo_norikae.csv", index=False)