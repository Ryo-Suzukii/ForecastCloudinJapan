import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

class Diff:
    def __init__(self,cloud_diff) -> None:
        self.cloud_diff = cloud_diff
        self.season_list = {
            "spring":[dt.datetime(2022,3,1),dt.datetime(2022,6,30)],
            "summer":[dt.datetime(2022,6,1),dt.datetime(2022,8,31)],
            "fall"  :[dt.datetime(2022,8,1),dt.datetime(2022,10,31)],
            "winter":[dt.datetime(2022,11,1),dt.datetime(2022,12,31)]
        }
    
    def make_color(self,thres):
        mask = (thres > self.cloud_diff["cloud_diff"]) & (self.cloud_diff["cloud_diff"] > -thres)
        self.x_sub = self.cloud_diff.index[mask]
        self.y_sub = self.cloud_diff["cloud_diff"][mask]

    def plot(self,start=None,end=None,season=None,thres=10):
        if (start == None) & (end == None):
            start = dt.datetime(2022,1,1)
            end = dt.datetime(2022,12,31)
        else:
            mask = (start <= self.cloud_diff.index) & (self.cloud_diff.index <= end)
            self.cloud_diff = self.cloud_diff[mask]
        if season:
            start = self.season_list[season][0]
            end = self.season_list[season][1]
            
            mask = (start <= self.cloud_diff.index) & (self.cloud_diff.index <= end)
            self.cloud_diff = self.cloud_diff[mask]
        
        self.make_color(thres)
        fig,ax = plt.subplots(figsize=(20,3))
        ax.plot(self.cloud_diff.index,self.cloud_diff["cloud_diff"],label="diff")
        ax.plot(self.x_sub,self.y_sub,color="red",label="thres")
        ax.legend()
        ax.set_title("obs-msmの雲量の差")
        ax.set_ylabel("diff")
        ax.set_xlabel("date")
        ax.set_xlim(start,end+dt.timedelta(days=1))
        plt.show()