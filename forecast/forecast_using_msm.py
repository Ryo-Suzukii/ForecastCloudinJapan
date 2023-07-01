import xarray as xr
import pathlib
import sys
import datetime as dt
import lightgbm as lgb
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pickle

ROOT_PATH = pathlib.Path(__file__).parents[1]
ROOT_PATH

sys.path.append(str(ROOT_PATH))

from modules.date_range import date_range


start = dt.date(2022,1,1)
end = dt.date(2023,1,1)

amemaster = pd.read_csv(ROOT_PATH/"ame_master_20230323.csv")
amemaster_kan = amemaster[(amemaster["種類"] == "官")].drop_duplicates(subset="観測所番号")

datasets = [xr.open_dataset(date.strftime(f"{ROOT_PATH}/data/%Y/%m/%Y_%m%d.nc"))[['psea', 'sp', 'u', 'v', 'temp', 'rh', 'r1h', 'dswrf','ncld']].dropna(dim="time") for date in date_range(start,end)]
del start,end


combined_dataset = xr.concat(datasets,dim="time")

del datasets


# 特徴量とターゲット変数に分割する
X = combined_dataset[['psea', 'sp', 'u', 'v', 'temp', 'rh', 'r1h', 'dswrf']]
y = combined_dataset['ncld']

del combined_dataset


X_df = X.to_dataframe().rename_axis(['lon', 'lat', 'time', 'ref_time']).reset_index()
del X


y_df = y.to_dataframe().rename_axis(['lon', 'lat', 'time', 'ref_time']).reset_index()
del y

X_df = pd.DataFrame()
y_df = pd.DataFrame()

for _,i in amemaster_kan.iterrows():
    lon = i["経度(度)"] + i["経度(分)"] / 60
    lat = i["緯度(度)"] + i["緯度(分)"] / 60
    # print(f"\r{lon},{lat}",end="")
    tmpdf = X_df[(round(X_df["lon"],2) == round(int(lon / 0.0625) * 0.0625, 2))
                &
                (round(X_df["lat"],2) == round(int(lat / 0.04999977) * 0.04999977,2))
                &
                (pd.to_datetime(X_df["ref_time"]).dt.hour == 0)
                ]
    
    tmp_y_df = y_df[(round(y_df["lon"],2) == round(int(lon / 0.0625) * 0.0625, 2))
                &
                (round(y_df["lat"],2) == round(int(lat / 0.04999977) * 0.04999977,2))
                &
                (pd.to_datetime(y_df["ref_time"]).dt.hour == 0) #予測出力時間(ほとんど変わらないけど一番精度が低い時間)
                ]
    # display(tmpdf)
    X_df = pd.concat([X_df.reset_index(drop=True),tmpdf.reset_index(drop=True)],axis=0)
    y_df = pd.concat([y_df.reset_index(drop=True),tmp_y_df.reset_index(drop=True)],axis=0)

# データセットをトレーニングセットとテストセットに分割する
X_train, X_test, y_train, y_test = train_test_split(X_df, y_df, test_size=0.3)

del X_df,y_df


# LightGBMデータセットに変換する
lgb_train = lgb.Dataset(X_train, label=y_train)

del X_train,y_train


params = {
    'objective': 'regression',
    'metric': 'mse'
}

# モデルのトレーニング
model = lgb.train(params, lgb_train)


filename = "model_using_msm.pkl"
with open(ROOT_PATH/filename,"wb") as f:
    pickle.dump(model,f)