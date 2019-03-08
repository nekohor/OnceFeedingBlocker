import pandas as pd
import sys
sys.path.append("C:/NutCloudSync/code/enigineerbox")
import utils
from grade import GradePurpose
from dbon import DBON


class Context:

    def __init__(self, ent):

        self.frequency = ent.frequency
        self.table_use = ent.table_use

        self.start_month = ent.start_month
        self.end_month = ent.end_month
        self.month_list = utils.generate_month(ent.start_month, ent.end_month)
        self.year_list = [201800, 201900]

        if self.table_use == "single":
            self.config_table = pd.read_excel(
                "tables/configTable_single.xlsx".format(self.frequency))
        elif self.table_use == "normal":
            self.config_table = pd.read_excel(
                "tables/configTable_{}.xlsx".format(self.frequency))
        else:
            raise Exception("wrong table use mode")

        self.plot_config = pd.read_excel(
            "plot/plotConfig.xlsx"
        )

        self.result_dir = "D:/Work/一次投料合格率"
        self.inter_dir = "D:/Work/一次投料合格率/中间计算结果"

        self.db = {}
        self.db["2250"] = DBON(2250)
        self.db["1580"] = DBON(1580)

        self.gp = GradePurpose()

        self.sub_list = ["shape", "surface", "perf_comp"]

        if self.frequency == "weekly":
            self.group_col = "date_bin"
        elif self.frequency == "monthly":
            self.group_col = "month"
        else:
            raise Exception("wrong frequency in context init()")

        self.mkdir = utils.mkdir
