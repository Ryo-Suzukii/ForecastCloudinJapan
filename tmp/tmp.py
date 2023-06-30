import datetime as dt
import os
import pathlib
import sys
ROOT_PATH = pathlib.Path(__file__).parents[1]
from dateutil.relativedelta import relativedelta

sys.path.append(str(ROOT_PATH))

import modules.date_range as date_range
from modules.time_series_CSV_reader import TimeSeriesCSVReader

ts = TimeSeriesCSVReader(2022)
date_range = date_range.DateRange()

for date in date_range.date_range(dt.date(2022,1,1),dt.date(2023,1,1),"months"):
    df = ts.amedas_csv_loader(date,date + relativedelta(months=1))
    os.makedirs(ROOT_PATH/f"csv_monthly",exist_ok=True)
    df.to_csv(ROOT_PATH/f"csv_monthly/{date.month}.csv",index=False)