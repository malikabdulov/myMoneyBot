import re
import datetime
from datetime import date, timedelta

if __name__ == '__main__':
    res = [(2, 1, 1, 'Phrease', datetime.datetime(2020, 12, 11, 0, 0), 874, datetime.datetime(2020, 12, 11, 20, 18, 6), datetime.datetime(2020, 12, 11, 20, 18, 6)),
           (3, 1, 1, 'Ued', datetime.datetime(2020, 12, 11, 0, 0), 540, datetime.datetime(2020, 12, 11, 20, 24, 16), datetime.datetime(2020, 12, 11, 20, 24, 16))]
    for r in res:
        print(r[0])
