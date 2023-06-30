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
datasets = [xr.open_dataset(date.strftime(f"{ROOT_PATH}/data/%Y/%m/%Y_%m%d.nc"))[['psea', 'sp', 'u', 'v', 'temp', 'rh', 'r1h', 'dswrf','ncld']].dropna(dim="time") for date in date_range(start,end)]
del start,end


combined_dataset = xr.concat(datasets,dim="time")

del datasets


# 特徴量とターゲット変数に分割する
X = combined_dataset[['psea', 'sp', 'u', 'v', 'temp', 'rh', 'r1h', 'dswrf']]
y = combined_dataset['ncld']

del combined_dataset


X_df = X.to_dataframe()
del X


y_df = y.to_dataframe()
del y


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