from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import os
import datetime
os.chdir("c:\\Users\\astro\\Documents\\Python_Project\\ForecastCloudinJapan")

def make_soup(url:str):
    res = requests.get(url)
    return BeautifulSoup(res.content,"html.parser")

class Scrape:
    def __init__(self,base_url:str,year:int,month:int,day:int,prec_no=44,block_no=47662):
        self.prec_no = prec_no
        self.block_no = block_no
        self.year = year
        self.month = month
        self.day = day
        self.url = base_url+f"?prec_no={prec_no}&block_no={block_no}&year={year}&month={month}&day={day}&view=p1"
        self.soup = make_soup(self.url)
        self.cols = [
            "時間","現地気圧","海面気圧","降水量","気温",
            "露点温度","蒸気圧","湿度","風速",
            "風向","日照時間","全天日射量","降雪","積雪",
            "天気","雲量","視程"
        ]
        self.astype_cols = {
            "時間":int, "現地気圧":float, "海面気圧":float,
            "気温":float, "露点温度":float,
            "蒸気圧":float, "湿度":int, "風速":float,
            "日照時間":float, "全天日射量":float, "視程":float
        }
    
    def get_raw(self,hour:int) -> list:
        raw = self.soup.select(f"#tablefix1 > tr:nth-child({3+hour})")[0]
        return [i.text for i in raw.find_all("td")]
    
    def get_all_raw(self) -> list:
        return [self.get_raw(i) for i in range(24)]
    
    def ret_df(self) -> pd.DataFrame:
        df = pd.DataFrame(data=self.get_all_raw(),columns=self.cols)
        df["日付"] = df["時間"].apply(lambda x: self.make_date(int(x)))

        df.replace({"--":0,"":0},inplace=True)
        try:
            df = df.astype(self.astype_cols)
        except ValueError:
            return df
        return df
    
    def make_date(self,hour) -> datetime.datetime:
        try:
            dt = datetime.datetime(self.year,self.month,self.day,hour)
        except ValueError:
            dt = datetime.datetime(self.year,self.month,self.day,0)
            dt += datetime.timedelta(days=1)
        return dt
    
    def write2csv(self,path="obsData/"):
        path += f"{self.prec_no}_{self.block_no}/{self.year}/{self.month}/"

        os.makedirs(path,exist_ok=True)

        df = self.ret_df()
        try:
            df[["気温","露点温度","蒸気圧","湿度","風速","風向"]] = df[["気温","露点温度","蒸気圧","湿度","風速","風向"]].applymap(lambda x:x.rstrip(" )"))
        except AttributeError:
            pass

        # 雲量の値を独自の記法にする(README.md:雲量表記の統一について)

        df = df.replace("×",np.nan)
        df.to_csv(path+f"{self.prec_no}_{self.block_no}_{self.year}_{self.month}_{self.day}.csv",index=False)

def main():
    base_url = f"https://www.data.jma.go.jp/obd/stats/etrn/view/hourly_s1.php"
    
    dt = datetime.datetime(2010,1,1)

    while True:
        sc = Scrape(base_url,dt.year,dt.month,dt.day)
        sc.write2csv()
        dt += datetime.timedelta(days=1)
        print(f"\r{dt.year}-{dt.month}-{dt.day}",end="")

        if dt.year == 2023:
            break

def debug():
    print("debug")
    base_url = f"https://www.data.jma.go.jp/obd/stats/etrn/view/hourly_s1.php"
    
    dt = datetime.datetime(2000,5,5)
    sc = Scrape(base_url,dt.year,dt.month,dt.day)
    sc.write2csv()
    

if __name__ == "__main__":
    main()