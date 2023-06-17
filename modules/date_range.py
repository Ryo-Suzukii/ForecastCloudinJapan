import datetime as dt
import pathlib
import sys

ROOT_PATH = pathlib.Path(__file__).parents[1]
sys.path.append(str(ROOT_PATH))

from modules.errors import *

class DateRange:
    def __init__(self,) -> None:
        pass
    def date_range(
            self,
            start_date : dt.datetime,
            end_date : dt.datetime,
            step : str
        ):

        if not step in ["hours","days"]:
            raise NoValueError(f"{step} cannot be specified as an argument.")
        
        if step == "days":
            step = dt.timedelta(days=1)
        elif step == "hours":
            step = dt.timedelta(hours=1)
        current = start_date
        
        while current < end_date:
            yield current
            current += step
