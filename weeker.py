from datetime import timedelta
from datetime import datetime
import numpy as np
import pandas as pd


class Weeker:

    def __init__(self, current_year):
        self.table = self.build_table(current_year)

    def get_weektime_list(self, first_datetime, last_datetime):
        days = (last_datetime - first_datetime).days
        weektime_list = []
        for i in range(days + 1):
            current_datetime = first_datetime + timedelta(days=i)
            # judge if current date is wednesday
            if current_datetime.weekday() == 2:
                weektime_list.append(current_datetime)
        print(weektime_list)
        return weektime_list

    def get_date_bin_list(self, weektime_list):
        i = 0
        date_bin_list = []
        for weektime in weektime_list:
            if i == 0:
                i = i + 1
                continue
            else:
                date_bin_list.append(
                    "({}, {}]".format(
                        weektime_list[i - 1].strftime('%Y-%m-%d'),
                        weektime_list[i].strftime('%Y-%m-%d'),
                    )
                )
                i = i + 1
        print(date_bin_list)
        return date_bin_list

    def select_weektimes(self, weektime_list, current_year):
        year_list = np.array(
            [x.year for x in weektime_list]
        )
        first_idx = np.where(year_list == current_year)[0][0]
        last_idx = np.where(year_list == current_year)[0][-1]
        print("first_idx", first_idx)
        print("last_idx", last_idx)
        return weektime_list[first_idx: last_idx]

    def build_table(self, current_year):
        start_year = current_year - 2
        end_year = current_year + 2

        start_datetime = datetime(start_year, 1, 1)
        end_datetime = datetime(end_year, 1, 1)

        weektime_list = self.get_weektime_list(
            start_datetime,
            end_datetime
        )
        # 筛选本年度的周时间节点weektime
        weektime_list = self.select_weektimes(weektime_list, current_year)

        date_bin_list = self.get_date_bin_list(weektime_list)
        print(date_bin_list)
        table = pd.DataFrame()
        i = 0
        for date_bin in date_bin_list:
            i = i + 1
            table.loc[i, "date_bin"] = date_bin

        table.to_excel("week/weekTable.xlsx")
        return table

    def get_date_bin(self, week_num):
        print(self.table)
        return self.table.loc[week_num, "date_bin"]
