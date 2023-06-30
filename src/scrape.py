import os
import re
import time
import numpy as np
import pandas as pd
import urllib.request
import pathlib
from bs4 import BeautifulSoup
from datetime import timedelta
import datetime as dt

import sys
import pathlib
ROOT_PATH = pathlib.Path(__file__).parents[1]
sys.path.append(str(ROOT_PATH))

import modules.getdata as getdata


def date_range(start, stop, step = "days"):
    """datetime,dateを用いてイテレーションにする関数

    Args:
        start (date,datetime): はじまりのdate
        stop (date,datetime): 終わりのdate
        step (str, optional): 日ごとにするのか時間ごとにするのか."days" or "hours". Defaults to "days".

    Yields:
        _type_: _description_
    """
    if step == "days":
        step = dt.timedelta(days=1)
    elif step == "hours":
        step = dt.timedelta(hours=1)
    current = start
    while current < stop:
        yield current
        current += step

class Get_amedas_station:
    """気象庁の過去の気象データを取得する際に使用するprec_noとblock_noを取得する
    """
    
    def __init__(self):
        url = 'https://www.data.jma.go.jp/obd/stats/etrn/select/prefecture00.php?prec_no=&block_no=&year=&month=&day=&view='
        html = urllib.request.urlopen(url)
        self.soup = BeautifulSoup(html, 'html.parser')

    def get_area_link(self) -> list:
        """precの名前とurl(https://www.data.jma.go.jp/obd/stats/etrn/select/ までは共通)をそれぞれリストにする
        """
        # area属性のタグをリストにする
        elements = self.soup.find_all('area')
        # alt(地方名)
        self.area_list = [element['alt'] for element in elements]
        # href(prec_noが入力されたurl)
        self.area_link_list = [element['href'] for element in elements]
        return self.area_link_list

    def get_station_link(self):
        """気象庁の過去データより調べた各アメダスの情報とリンクをDataFrameにする
        """
        
        try:
            type(self.area_link_list)
        except:
            self.get_area_link()
        
        out = pd.DataFrame(columns=['station','url','area'])
        for area, area_link in zip(self.area_list, self.area_link_list):
            url = 'https://www.data.jma.go.jp/obd/stats/etrn/select/'+ area_link
            html = urllib.request.urlopen(url)
            soup = BeautifulSoup(html, 'html.parser')
            # area属性で各アメダス取得
            elements = soup.find_all('area')
            # altでアメダスの名前
            station_list = [element['alt'] for element in elements]
            # prec_noとblock_noの入ったリンク
            station_link_list = [element['href'].strip('../') for element in elements]
            df1 = pd.DataFrame(station_list,columns=['station'])
            df2 = pd.DataFrame(station_link_list,columns=['url'])
            df = pd.concat([df1, df2],axis=1).assign(area=area)
            out = pd.concat([out,df])
            print("\r"+area+" "*12,end="")
        self.out = out
        return out

    def data_arange(self,output=True):
        """スクレイピングしてDataFrameにしたデータをきれいにしてcsvとして出力
        """
        try:
            type(self.out)
        except:
            self.get_station_link()
        
        out = self.out[~self.out.duplicated()].assign(append='https://www.data.jma.go.jp/obd/stats/etrn/')
        out['amedas_url'] = out['append'] + out['url']
        out = out.loc[:,['area','station','amedas_url']]
        
        # drop_index = out[out["amedas_url"].str.contains("block_no=&")].index
        # out = out.drop(drop_index)
        
        output_file = 'amedas_url_list2.csv'
        if output:
            out.to_csv(output_file,index=None, encoding='utf-8')
            return out
        else:
            return out
    
    def all_do(self,output=False):
        self.get_area_link()
        self.get_station_link()
        self.data_arange(output=output)
        return 0

# getmasterの方使う
class ScrapeFromHP:
    """amemasterに載っている情報よりスクレイピングを行う
    """
    def __init__(self) -> None:
        master = getdata.Getmaster()
        self.point_df = master.getter()
        self.url = "https://www.data.jma.go.jp/obd/stats/etrn/view/"
        
        self.df = pd.DataFrame(columns=["AMSID","WindSpeed","SnowFall"])

    def scrape(self,AMSID,prec,block,year,month,day) -> pd.DataFrame:
        # 特殊な値欄を処理する
        def check_value(value):
            if (value == "///") or (" ]" in str(value)) or ("×" in str(value)):
                return np.nan
            elif "--" in str(value):
                return 0
            elif ")" in str(value):
                return float(value.split(" )")[0])
            else:
                return float(value)
        
        # block_noが5桁以上の場所とそれ以外で扱いが違うのでその対処
        if block > 9999:
            hourly = "hourly_s1"
            wind_ = "風向・風速(m/s)"
            fusoku = "風速"
            yuki = "雪(cm)"
            kousetu = "降雪"
        else:
            hourly = "hourly_a1"
            wind_ = "風速・風向"
            fusoku = "平均風速 (m/s)"
            yuki = "雪"
            kousetu = "降雪 (cm)"
            
            block = str(block).zfill(4)
        
        url_end = f".php?prec_no={prec}&block_no={block}&year={year}&month={month}&day={day}&view=p1"
            
        self.url_ = self.url + hourly + url_end
        try:
            df = pd.read_html(self.url_)[0]
        except:
            prec = 12
            self.url_ = self.url + hourly + url_end
            df = pd.read_html(self.url_)[0]
            
        wind = df[wind_][fusoku]
        snow = df[yuki][kousetu]
        
        tmpdf = pd.DataFrame(columns=["風速","降雪"])
        tmpdf["風速"] = wind
        tmpdf["降雪"] = snow
        tmpdf["降雪"] = tmpdf["降雪"].apply(check_value)
        tmpdf["風速"] = tmpdf["風速"].apply(check_value)
        tmpdf["time"] = list(range(1,25))
        
        # csvファイルとして保存する
        csv_file_name = pathlib.Path(f"{year}_{month}_{day}_{AMSID}.csv")
        csv_path = pathlib.Path(f"./csv/{year}/{month}/{day}")
        os.makedirs(csv_path,exist_ok=True)
        
        tmpdf.to_csv(csv_path/csv_file_name,index=False)
        
        return tmpdf
    
    # data変える
    def scrape_all_position(self,start=dt.date(2022,9,1),end=dt.date(2023,6,1)):
        for date in date_range(start,end):
            for _,row in self.point_df.iterrows():
                prec = str(row["amedas_id"])[:2]
                block = row["block_id"]
                try:
                    scr = self.scrape(row["amedas_id"],prec,block,date.year,date.month,date.day)
                    
                    # 地点指定がおかしかったりするとき
                except ValueError as e:
                    # エラーログをtxtに出力する
                    with open("./tmp/error_url.txt",mode="a") as f:
                        f.write(f"AMSID:{row['amedas_id']},{self.url_}\n")
                    continue
                
                del scr
                print(f"\rdate:{date},amedas_id:{row['amedas_id']}",end="")

def main():
    amedas = Get_amedas_station()
    amedas.all_do()
    
def do_master():
    scrape_master = ScrapeFromHP()
    scrape_master.scrape(50331,50,47656,2023,4,17)
    # scrape_master.scrape_all_position(dt.date(2023,1,26),dt.date(2023,1,27))

if __name__ == "__main__":
    start_time = time.perf_counter()
    # main()
    do_master()
    end_time = time.perf_counter()
    print(f"実行時間:{end_time-start_time}s")