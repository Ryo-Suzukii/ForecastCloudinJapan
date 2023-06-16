import os
import sys
import pathlib
import xarray as xr
import numpy as np
import datetime as dt

current_path = pathlib.Path(__file__)
root_path = current_path.parents[1]

class Reduce:
    def __init__(self,date:dt.datetime) -> None:
        self.date = date
        self.file_path = f"{self.date.year}/{str(self.date.month).zfill(2)}/{self.date.year}_{str(self.date.month).zfill(2)}{str(self.date.day).zfill(2)}.nc"

    def reduce(
            self,
            use_col = [
                "temp","rh","r1h","ncld","u","v"
            ]
    ):
        nc = xr.open_dataset(root_path/"data"/self.file_path)
        reduced_nc = nc.sel()[use_col].astype(float)
        reduced_nc.attrs["_FillValue"] = np.nan

        return reduced_nc
    
    def save_netcdf(self,nc):
        to_path = root_path/f"data_reduced/{self.date.year}/{str(self.date.month).zfill(2)}"
        os.makedirs(to_path,exist_ok=True)
        nc.to_netcdf(to_path/f"{self.date.year}_{str(self.date.month).zfill(2)}{str(self.date.day).zfill(2)}.nc")
        return 0


def main():
    start_date = dt.date(2022,1,1)
    end_date = dt.date(2022,1,31)

    while start_date <= end_date:
        print(f"\r{start_date}",end="")
        reduce = Reduce(start_date)
        nc = reduce.reduce()
        reduce.save_netcdf(nc)

        start_date += dt.timedelta(days=1)
    print(0)

if __name__ == "__main__":
    main()