# 日本の天気予報に必要なデータ(netCDF2)をxarrayを使って取得し、PandasのDataFrame形式で保存するプログラム。

import numpy as np
import pandas as pd
import datetime as dt
import xarray as xr
import os

PROJECT_NAME = "ForecastCloudinJapan"
cwd_list = os.path.abspath(__file__).split("\\")
cwd_list_copy = cwd_list.copy()
s = -1
c = 0

while True:
    if cwd_list[s] == "ForecastCloudinJapan":
        break
    else:
        cwd_list_copy.pop(-1)
        s -= 1
        c += 1

ABS_PATH = "\\".join(cwd_list_copy).replace("\\","/")

os.chdir(ABS_PATH)


def savecsv(df:pd.DataFrame,path:str,file:str,index=False) -> None:
    os.makedirs(path,exist_ok=True)
    df.to_csv(path+file,index=False)

class CreateDataSet:
    def __init__(self,year:int,month:int,day:int) -> None:
        self.date = dt.datetime(year,month,day)
        self.ds = xr.open_dataset(f"{ABS_PATH}/data/{self.date.year}/{str(self.date.month).zfill(2)}/{self.date.year}_{str(self.date.month).zfill(2)}{str(self.date.day).zfill(2)}.nc")
        self.cols = ["date(UTC)","海面気圧","地上気圧","東風","西風","気温","相対湿度","降水量","雲量","下行短波放射線フラックス"]
        self.df = pd.DataFrame(columns=self.cols)
        self.path = f"msm_data/{self.date.year}/{str(self.date.month).zfill(2)}/"
        self.file = f"{self.date.year}_{str(self.date.month).zfill(2)}{str(self.date.day).zfill(2)}.csv"

    def create_dataframe(self,lat=35,lon=139,method="nearest",issave=True,check=False):
        ds_values = self.ds.sel(lat=lat,lon=lon,method=method)
        self.df["date(UTC)"] = pd.date_range(start=self.date,periods=24,freq="h")
        self.df["海面気圧"] = pd.Series(ds_values.psea.values)
        self.df["地上気圧"] = pd.Series(ds_values.sp.values)
        self.df["気温"] = pd.Series(ds_values.temp.values).apply(lambda x: x-273.15)
        self.df["相対湿度"] = pd.Series(ds_values.rh.values)
        self.df["降水量"] = pd.Series(ds_values.r1h.values)
        self.df["雲量"] = pd.Series(ds_values.ncld.values)
        self.df["東風"] = pd.Series(ds_values.u.values)
        self.df["西風"] = pd.Series(ds_values.v.values)
        self.df["下行短波放射線フラックス"] = pd.Series(ds_values.dswrf.values)

        if issave and check:
            print(self.df.head(3))
            checkbox = input("以上のdataframeを保存していいですか？(yes or no)")

            if checkbox.upper() == "YES":
                savecsv(self.df,self.path,self.file)
            else:
                print("passしました")
        elif issave and (check == False):
            savecsv(self.df,self.path,self.file)
        else:
            pass

    def savecsvbymyself(self):
            savecsv(self.df,self.path,self.file)

def main():
    date = dt.datetime(2022,1,1)
    enddate = dt.datetime(2023,1,1)
    while True:
        cd = CreateDataSet(date.year,date.month,date.day)
        cd.create_dataframe()
        print(f"\r{date}",end="")
        date += dt.timedelta(days=1)
        if date == enddate:
            break

if __name__ == "__main__":
    main()