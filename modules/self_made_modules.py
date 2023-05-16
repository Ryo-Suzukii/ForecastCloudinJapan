import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import xarray as xr
import cartopy.crs as crs
import datetime as dt
import japanize_matplotlib
from PIL import Image
import glob
import os
import shutil

class PlotCloudOnJapan:
    def __init__(self, date:dt.datetime):
        self.date = date
        self.map_data = {
            "zenkoku":[127, 147, 27, 47],
            "hokkaido":[139, 147, 39, 47],
            "kanto":[137, 142, 33, 38],
        }

    def plot(self, hour: int, isgif=False,map=None):
        """netCDF2ファイルより雲の動きをプロットする

        Args:
            hour (int): 表示する時間
            isgif (bool, optional): gifにするかどうか. Defaults to False.
            map (list, optional): 拡大表示するかどうか. Defaults to None.

        Returns:
            _type_: _description_
        """
        # データを読み込む
        ds = xr.open_dataset(f"../data/{self.date.year}/{str(self.date.month).zfill(2)}/{self.date.year}_{str(self.date.month).zfill(2)}{str(self.date.day).zfill(2)}.nc")

        # もしも時間指定があった時はそっちを優先
        if hour:
            self.date = self.date.replace(hour=hour)

        # dateから1時間後のdatetimeオブジェクトを生成
        end_time = self.date + dt.timedelta(hours=1)

        # データからcloudを取り出す
        cloud_array = ds.sel(time=slice(self.date, end_time))['ncld'].values[0]

        # 欠損値をマスクする
        masked_data = np.ma.masked_where(np.isnan(cloud_array), cloud_array)

        # 表示する範囲の指定
        if isinstance(map,str):
            try:
                map_range = self.map_data[map]
            except KeyError:
                print("辞書にないため全国表示します")
                map_range = self.map_data["zenkoku"]
        
        if isinstance(map,list):
            map_range = map

        # 地図を作成する
        fig, ax = plt.subplots(facecolor="darkblue", subplot_kw={'projection': crs.PlateCarree()})
        ax.set_extent(map_range, crs.PlateCarree())
        ax.coastlines(resolution='10m')

        # カラーマップを設定する
        cmap = plt.colormaps.get_cmap('Blues')

        # プロットする
        img = ax.imshow(masked_data, cmap=cmap, origin='upper', extent=map_range, transform=crs.PlateCarree())
        cbar = plt.colorbar(img, cmap=cmap, orientation='horizontal', shrink=0.8)
        cbar.set_label('Cloud Cover')

        ax.set_title(f"{self.date.year}/{self.date.month}/{self.date.day} {self.date.hour}時(UTC)の雲")

        # gifにするならtmp画像として保存
        if isgif:
            return fig.savefig(f"../tmp/{self.date.year}_{str(self.date.month).zfill(2)}{str(self.date.day).zfill(2)}_{str(hour).zfill(2)}.png")
        # ただ1時間の画像としてみたいならそのまま表示
        else:
            plt.show()

    def plot_gif(self,start:dt.datetime,end=None,during=None,dir="../png",file="image.gif",maps="zenkoku"):
        """gifにして保存する

        Args:
            start (dt.datetime): 開始のdatetime
            end (dt.datetime): 終了のdatetime
            during (int, optional): endを指定しない場合の何時間分表示するか. Defaults to None.
            dir (str, optional): 保存するディレクトリ. Defaults to "../png".
            file (str, optional): ファイル名. Defaults to "image.gif".
            maps (list, optional): 拡大表示する範囲. Defaults to None.

        Yields:
            _type_: _description_
        """
        ims = []

        if end == None:
            end = start
        
        if during:
            end = start + dt.timedelta(hours=during)

        # startから1時間ずつ増やして返すジェネレータ
        def date_range(st,en,step=dt.timedelta(hours=1)):
            current = st
            while current < en:
                yield current
                current += step

        for current_day in date_range(start,end):
            self.plot(current_day.hour,True,map=maps)
            plt.clf()
            plt.close()
        
        # tmpフォルダのpngを読み込む
        files = sorted(glob.glob("../tmp/*.png"))
        images = list(map(lambda file : Image.open(file) , files))
        
        # gifにする
        if dir[-1] != "/":
            dir = dir+"/"
        
        if not "." in file:
            file = file+".gif"

        save_file = dir+file
        images[0].save(save_file, save_all=True, append_images=images[1:], duration=400, loop=0)
        
        # tmpフォルダ空にする (tmpフォルダごと削除->tmpフォルダの作成をしてるから今後tmpフォルダ使うなら修正必要)
        shutil.rmtree("../tmp")
        os.mkdir("../tmp")

def main():
    print("main")