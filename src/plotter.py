import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['savefig.facecolor'] = 'white'
sns.set(font="Yu Gothic")

import japanize_matplotlib
import datetime as dt
import time
import sys
sys.path.append("../")
import os

import modules
import modules.self_made_modules as mymodule

class Plotter:
    def __init__(self,date) -> None:
        pocj = mymodule.PlotCloudOnJapan(date)
        self.date = date
        self.msm_df = pocj.coordinate(lat=35.41,lon=139.45)
        self.obs_df = pd.read_csv(f"../obsData_utc/44_47662/{self.date.year}/{self.date.month}/44_47662_{self.date.year}_{self.date.month}_{self.date.day}.csv")
        self.obs_df["日付"] = pd.to_datetime(self.obs_df["日付"])
        self.obs_df["雲量"] = self.obs_df["雲量"]*10 # 10倍して0-100の範囲にする


        self.obs_df["雲量"] = self.padding_obs(self.obs_df)
        
    def padding_obs(self,obs_df):
        data_list = [0,3,6,9,12,15,18]
        df = obs_df["雲量"].copy()

        df[15] = df[12] + round((df[18] - df[12])/2)
        for i in data_list:
            division = round((df[i+3] - df[i]) / 3)
            tmp = df[i]+division
            df[i+1] = tmp
            df[i+2] = df[i+1]
        return df


    def plott(self,isplot=False):
        fig,ax = plt.subplots()

        ax.plot(self.msm_df.index,self.msm_df["ncld"],label="MSM")
        ax.set_xlabel("Date")
        ax.tick_params(axis="x",rotation=45)
        ax.set_ylim(0,102)

        ax.plot(self.obs_df["日付"],self.obs_df["雲量"],label="OBS",color="red")
        ax.set_ylabel("雲量")

        ax.legend(loc="best")
        plt.title(f"東京(35,139)|{self.date.year}-{self.date.month}-{self.date.day}")
        # plt.subplots_adjust(top=1.2)

        if isplot:
            plt.show()
        else:
            os.makedirs(f"../png/diff/{self.date.month}",exist_ok=True)
            plt.savefig(f"../png/diff/{self.date.month}/東京_{self.date.year}_{self.date.month}_{self.date.day}.png",bbox_inches='tight')
            plt.close()
    
    def getter(self,df):
        obs = ["o","obs","obs_df"]
        msm = ["m","msm","msm_df"]
        if df in obs:
            return self.obs_df
        else:
            return self.msm_df

def main():
    date = dt.date(2022,1,1)
    while True:
        print(f"\r{date}{' '*4}",end="")
        p = Plotter(date)
        p.plott(isplot=False)
        date += dt.timedelta(days=1)