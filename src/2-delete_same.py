
from datetime import datetime as dt

import pandas as pd

delete_indexs = list()
df = pd.read_csv(f"../result/{str(dt.now())[:10]}/suumo.csv")
"""
for _, group1 in df.groupby("住所"):
    for _, group2 in group1.groupby("家賃"):
        for _, group3 in group2.groupby("管理費"):
            for _, group4 in group3.groupby("敷金"):
                for _, group5 in group4.groupby("礼金"):
                    for _, group6 in group5.groupby("間取り"):
                        for _, group7 in group6.groupby("面積"):
                            for _, group8 in group7.groupby("向き"):
                                for _, group9 in group8.groupby("種別"):
                                    for _, group10 in group9.groupby("築年"):
                                        if len(group10)>1:
                                            delete_indexs.extend(list(group10.index[1:]))
"""
for _, group1 in df.groupby("住所"):
    for _, group2 in group1.groupby("家賃"):
        for _, group3 in group2.groupby("管理費"):
            for _, group4 in group3.groupby("面積"):
                    for _, group5 in group4.groupby("種別"):
                        if len(group5)>1:
                            delete_indexs.extend(list(group5.index[1:]))
df = df.drop(index=df.index[delete_indexs])
df.to_csv(f"../result/{str(dt.now())[:10]}/suumo_wo_same.csv", index=False)