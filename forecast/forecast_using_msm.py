import xarray as xr
import pathlib
import sys
import datetime as dt
from dateutil.relativedelta import relativedelta
import lightgbm as lgb
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pickle

ROOT_PATH = pathlib.Path(__file__).parents[1]
ROOT_PATH

sys.path.append(str(ROOT_PATH))

from modules.date_range import date_range

print("start")
start = dt.date(2022,1,1)
end = dt.date(2023,1,1)

amemaster = pd.read_csv(ROOT_PATH/"ame_master_20230323.csv")
amemaster_kan = amemaster[(amemaster["種類"] == "官")].drop_duplicates(subset="観測所番号")

X_df_ = pd.DataFrame()
y_df_ = pd.DataFrame()

for i in range(12):
    date = start + relativedelta(months=i)
    print(date)
    datasets = [xr.open_dataset(date.strftime(f"{ROOT_PATH}/data/%Y/%m/%Y_%m%d.nc"))[['psea', 'sp', 'u', 'v', 'temp', 'rh', 'r1h', 'dswrf','ncld']].dropna(dim="time") for i in date_range(date, date + relativedelta(months=1))]
    
    combined_dataset = xr.concat(datasets,dim="time")
    del datasets
    
    X = combined_dataset[['psea', 'sp', 'u', 'v', 'temp', 'rh', 'r1h', 'dswrf']]
    y = combined_dataset['ncld']

    del combined_dataset
    
    X_df = X.to_dataframe().rename_axis(['time', 'lat', 'lon']).reset_index()
    del X
    print("Complete to dataframe X")

    y_df = y.to_dataframe().rename_axis(['time', 'lat', 'lon']).reset_index()
    del y
    print("complete to dataframe y")
    
    for _,i in amemaster_kan.iterrows():
        lon = i["経度(度)"] + i["経度(分)"] / 60
        lat = i["緯度(度)"] + i["緯度(分)"] / 60
        # print(f"{lon},{lat}")
        tmpdf = X_df[(round(X_df["lon"],2) == round(int(lon / 0.0625) * 0.0625, 2))
                    &
                    (round(X_df["lat"],2) == round(int(lat / 0.04999977) * 0.04999977,2))
                    ]
        
        tmp_y_df = y_df[(round(y_df["lon"],2) == round(int(lon / 0.0625) * 0.0625, 2))
                    &
                    (round(y_df["lat"],2) == round(int(lat / 0.04999977) * 0.04999977,2))
                    ]
        # display(tmpdf)
        X_df_ = pd.concat([X_df_.reset_index(drop=True),tmpdf.reset_index(drop=True)],axis=0)
        y_df_ = pd.concat([y_df_.reset_index(drop=True),tmp_y_df.reset_index(drop=True)],axis=0)
        del tmpdf,tmp_y_df
        
    print(X_df_.shape)
    del X_df,y_df
    print("Complete extract df")

X_df_.to_csv(ROOT_PATH/"csv/2023-07-03X_df.csv",index=False)
y_df_.to_csv(ROOT_PATH/"csv/2023-07-03y_df.csv",index=False)

X_train, X_test, y_train, y_test = train_test_split(X_df_, y_df_, test_size=0.3)

# LightGBMデータセットに変換する
lgb_train = lgb.Dataset(X_train, label=y_train)

del X_train,y_train


params = {
    'objective': 'regression',
    'metric': 'mse'
}

# モデルのトレーニング
model = lgb.train(params, lgb_train)


filename = "model_using_msm1.pkl"
with open(ROOT_PATH/filename,"wb") as f:
    pickle.dump(model,f)