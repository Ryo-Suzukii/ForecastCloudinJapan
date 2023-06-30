import datetime as dt


class DataRange:
    def __init__(self) -> None:
        pass
    
    def date_range(start, stop, step = "days"):
        """datetime,dateを用いてイテレーションにする関数

        Args:
            start (date,datetime): はじまりのdate
            stop (date,datetime): 終わりのdate
            step (str, optional): 日ごとにするのか時間ごとにするのか."days" or "hours". Defaults to "days".

        Yields:
            _type_: _description_
        """
        if step == "days":
            step = dt.timedelta(days=1)
        elif step == "hours":
            step = dt.timedelta(hours=1)
        current = start
        while current < stop:
            yield current
            current += step


def date_range(start, stop, step = "days"):
    """datetime,dateを用いてイテレーションにする関数

    Args:
        start (date,datetime): はじまりのdate
        stop (date,datetime): 終わりのdate
        step (str, optional): 日ごとにするのか時間ごとにするのか."days" or "hours". Defaults to "days".

    Yields:
        _type_: _description_
    """
    if step == "days":
        step = dt.timedelta(days=1)
    elif step == "hours":
        step = dt.timedelta(hours=1)
    current = start
    while current < stop:
        yield current
        current += step
