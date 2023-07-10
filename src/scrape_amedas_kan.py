import numpy as np
import pandas as pd
import pathlib
import sys
import os
from datetime import date,datetime,timedelta

ROOT_PATH = pathlib.Path(__file__).parents[1]
sys.path.append(str(ROOT_PATH))

from modules.date_range import date_range

amedas_url = pd.read_csv(ROOT_PATH/"amedas_url_list2.csv")
amemaster = pd.read_csv(ROOT_PATH/"ame_master_20230323.csv")
amemaster_kan = amemaster[amemaster["種類"] == "官"]
df = pd.merge(amedas_url,amemaster_kan,left_on="station",right_on="観測所名")
class ScrapeObsTable:
    def __init__(self) -> None:
        self.cols = ["時","現地","海面","降水量 (mm)","気温 (℃)","露点 温度 (℃)","蒸気圧 (hPa)","湿度 (％)",
                    "風速","風向","日照 時間 (h)","全天 日射量 (MJ/㎡)","降雪",
                    "積雪","天気","雲量","視程 (km)"]
        
        self.a1_cols = [
            "時","降水量 (mm)", "気温 (℃)", "露点 温度 (℃)", "蒸気圧 (hPa)",
            "湿度 (％)", "平均風速 (m/s)", "風向", "日照 時間 (h)", "降雪 (cm)",
            "積雪 (cm)"
        ]
    
    def check_value(self,value):
            if (value == "///") or (" ]" in str(value)) or ("×" in str(value)):
                return np.nan
            elif "--" in str(value):
                return 0
            elif ")" in str(value):
                return float(value.split(" )")[0])
            else:
                try:
                    return float(value)
                except ValueError:
                    return value
    
    def scrape(
        self,
        url : str,
        date : datetime
            ) -> pd.DataFrame:
        try:
            table = pd.read_html(url)[0]
        except ValueError:
            url = url.replace("hourly_s1","hourly_a1")
            table = pd.read_html(url)[0]
        
        try:
            table.columns = self.cols
        except ValueError:
            table.columns = self.a1_cols
        
        for i in table.items():
            table[i[0]] = table[i[0]].apply(lambda x: self.check_value(x))
        table["datetime"] = date
        return table
    
    def save_csv(
        self,
        df : pd.DataFrame,
        filedir : str,
        filename : str
    ) -> None:
        os.makedirs(ROOT_PATH/filedir,exist_ok=True)
        df.to_csv(ROOT_PATH / filedir / filename,index=False)

s = ScrapeObsTable()

for d in date_range(date(2022,12,1),date(2023,1,1)):
    for i in df.iterrows():
        print(f"\r{d},{i[1]['観測所番号']}",end="")
        # url作ろう

        url = i[1]["amedas_url"].replace("index.php","view/hourly_s1.php")
        a_split = url.split("=")
        url = a_split[0]+"=" + a_split[1]+"=" + a_split[2]+d.strftime("=%Y&month=%m&day=%d")
        
        table = s.scrape(url, d)
        
        s.save_csv(table,d.strftime(f"csv/obs_value/{i[1]['観測所番号']}/%Y/%m"),d.strftime(f"%Y%m%d_{i[1]['観測所番号']}.csv"))
        s.save_csv(table,d.strftime(f"csv/obs_value/%Y/%m/%d"),d.strftime(f"%Y%m%d_{i[1]['観測所番号']}.csv"))
