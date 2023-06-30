### 実行前にcurl-MSM-s.shを実行してください

import numpy as np
import pandas as pd
import datetime as dt
import sys
sys.path.append("../init_weather_data/")

import get_coordinates_data_from_netCDF2 as gc
import scrape_weather_data as sw
import utc2jst as uj

date = dt.datetime(2022,1,1)
enddate = dt.datetime(2023,1,1)


# netCDF2ファイルから東京のデータ取り出してcsvにする
while True:
    cd = gc.CreateDataSet(date.year,date.month,date.day)
    cd.create_dataframe()
    print(f"\r{date}",end="")
    date += dt.timedelta(days=1)
    if date == enddate:
        break


# 気象庁から実測値スクレイピングしてくる
base_url = f"https://www.data.jma.go.jp/obd/stats/etrn/view/hourly_s1.php"
    
date = dt.datetime(2010,1,1)
while True:
    sc = sw.Scrape(base_url,dt.year,dt.month,dt.day)
    sc.write2csv()
    date += dt.timedelta(days=1)
    print(f"\r{date.year}-{date.month}-{date.day}",end="")

    if date.year == 2023:
        break

# netCDF2から取り出したデータはUTCなのでJSTにする
date = dt.date(2022,1,2)
while True:
    prevdate = date - dt.timedelta(days=1)
    nowdf = pd.read_csv(f"../msm_data/{date.year}/{str(date.month).zfill(2)}/{date.year}_{str(date.month).zfill(2)}{str(date.day).zfill(2)}.csv")
    prevdf = pd.read_csv(f"../msm_data/{prevdate.year}/{str(prevdate.month).zfill(2)}/{prevdate.year}_{str(prevdate.month).zfill(2)}{str(prevdate.day).zfill(2)}.csv")

    trans = uj.Trans(prevdf,nowdf,"date(UTC)")
    trans.concat_utc(False)
    trans.transform_utc_2_jst("日付(JST)",issave=True,path=f"../msm_jst_data/{date.year}/{str(date.month).zfill(2)}/",file=f"{date.year}_{str(date.month).zfill(2)}{str(date.day).zfill(2)}.csv")

    print(f"\r{date}",end="")
    date += dt.timedelta(days=1)

    if date.year == 2023:
        break

# 気象庁のデータは1-24なので0-23にする
date = dt.date(2010,1,2)
while True:
    obsdf = pd.read_csv(f"../obsData/44_47662/{date.year}/{date.month}/44_47662_{date.year}_{date.month}_{date.day}.csv")

    prevdate = date - dt.timedelta(days=1)
    obs_prev_df = pd.read_csv(f"../obsData/44_47662/{prevdate.year}/{prevdate.month}/44_47662_{prevdate.year}_{prevdate.month}_{prevdate.day}.csv")
    u = uj.Obstrans(date,obs_prev_df,obsdf)
    u.trans()

    date += dt.timedelta(days=1)
    if date.year == 2023:
        break