import pandas as pd
import numpy as np
import datetime
import os

class TimeSeriesCSVReader:
    """期間を指定しobsDataよりpd.DataFrameとして読み込む
    """
    def __init__(self,start:int,end=2023):
        """init

        Args:
            start (int): 読み込みたい期間の始まり
            end (int): 読み込みたい期間の終わり. Defaults to 2023.
        """
        self.start = start
        self.end = end
        self.dt = datetime.datetime(start,1,2)
        self.path = f"obsData/44_47662/{self.dt.year}/"
        self.all_df = pd.read_csv(self.path+"1/"+f"44_47662_{self.dt.year}_1_1.csv")
    
    def load_data(self) -> pd.DataFrame:
        """ロードする関数

        Returns:
            pd.DataFrame: 指定期間全部のデータ
        """
        dt = datetime.datetime(self.start,1,2)
        while True:
            self.path = f"obsData/44_47662/{dt.year}/"
            tmpdf = pd.read_csv(f"{self.path}{dt.month}/44_47662_{dt.year}_{dt.month}_{dt.day}.csv")
            self.all_df = pd.concat([self.all_df,tmpdf])
            dt += datetime.timedelta(days=1)
            del tmpdf
            if dt.year == 2023:
                break
            print(f"\r{dt}",end="")
        return self.all_df