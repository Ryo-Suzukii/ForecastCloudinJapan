import pandas as pd
import datetime as dt
import os

class Trans:
    def __init__(self,prevdf:pd.DataFrame,nowdf:pd.DataFrame,prevtarget:str,nowtarget:str=None):
        """UTC(0-23)になっているcsvをJST(0-23)に変換する

        Args:
            prevdf (pd.DataFrame): 変換したい日の前日のデータ
            nowdf (pd.DataFrame): 変換したい日のデータ
            prevtarget (str): 変換したいカラム名
            nowtarget (str): _変換したいカラム名(同じ場合はNone)
        """
        self.prevdf = prevdf
        self.nowdf = nowdf
        self.prevtarget = prevtarget
        if nowtarget == None:
            self.nowtarget = prevtarget
        else:
            self.nowtarget = nowtarget
    
    def concat_utc(self,ret=True):
        """二つのdataframeをjst基準でつなげる

        Args:
            ret (bool, optional): つなげたデータを戻すかどうか. Defaults to True.

        Returns:
            pd.DataFrame: つなげたデータ(UTC)
        """
        prev = self.prevdf[pd.to_datetime(self.prevdf[self.prevtarget]).dt.hour > 14]
        now = self.prevdf[pd.to_datetime(self.nowdf[self.nowtarget]).dt.hour <= 14]
        if ret:
            self.utcdf = pd.concat([prev,now])
            return self.utcdf
        else:
            self.utcdf = pd.concat([prev,now])
    
    def transform_utc_2_jst(self,column:str=None,issave=False,path=None,file=None) -> pd.DataFrame:
        """JST基準でつなげたデータをJSTに変換する

        Args:
            column (str, optional): カラムのなまえNoneなら元と同じ. Defaults to None.
            issave (bool, False): 保存するかどうか
            path (str, None):保存するときのパス.issaveがTrueの時は絶対指定しないとダメ

        Returns:
            pd.DataFrame: JSTに変換したデータ
        """

        self.jstdf = self.utcdf
        self.jstdf[self.prevtarget] = pd.to_datetime(self.utcdf[self.prevtarget]) + dt.timedelta(hours=9)
        
        if column != None:
            self.jstdf.rename(columns={self.prevtarget:column},inplace=True)
        
        if issave:
            try:
                os.makedirs(path,exist_ok=True)
                self.jstdf.to_csv(path+file,index=False)
            except FileNotFoundError:
                print("pathおかしい")
        return self.jstdf

def main():
    date = dt.date(2022,1,2)
    while True:
        prevdate = date - dt.timedelta(days=1)
        nowdf = pd.read_csv(f"../msm_data/{date.year}/{str(date.month).zfill(2)}/{date.year}_{str(date.month).zfill(2)}{str(date.day).zfill(2)}.csv")
        prevdf = pd.read_csv(f"../msm_data/{prevdate.year}/{str(prevdate.month).zfill(2)}/{prevdate.year}_{str(prevdate.month).zfill(2)}{str(prevdate.day).zfill(2)}.csv")

        trans = Trans(prevdf,nowdf,"date(UTC)")
        trans.concat_utc(False)
        trans.transform_utc_2_jst("日付(JST)",issave=True,path=f"../msm_jst_data/{date.year}/{str(date.month).zfill(2)}/",file=f"{date.year}_{str(date.month).zfill(2)}{str(date.day).zfill(2)}.csv")

        print(f"\r{date}",end="")
        date += dt.timedelta(days=1)

        if date.year == 2023:
            break

if __name__ == "__main__":
    main()