import pandas as pd
import sys
from weeker import Weeker

from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches

sys.path.append("C:/NutCloudSync/code/enigineerbox")
import utils
from grade import GradePurpose
from dbon import DBON


class Context:

    def __init__(self, ent):

        self.cn_name = "一次投料合格率"

        self.frequency = ent.frequency
        self.week_num = ent.week_num
        self.month_num = ent.month_num
        self.mon = self.month_num % 100
        self.current_year = self.month_num // 100
        self.last_year = self.current_year - 1

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

        self.result_dir = "D:/Work/{}".format(self.cn_name)
        self.inter_dir = "D:/Work/{}/中间计算结果".format(self.cn_name)

        self.db = {}
        self.db["2250"] = DBON(2250)
        self.db["1580"] = DBON(1580)

        self.gp = GradePurpose()

        self.sub_list = ["shape", "surface", "perf_comp"]
        self.tags = ["main"] + self.sub_list

        if self.frequency == "weekly":
            self.group_col = "date_bin"
        elif self.frequency == "monthly":
            self.group_col = "month"
        else:
            raise Exception("wrong frequency in context init()")

        self.mkdir = utils.mkdir

        self.lang_map = {
            "main": "总体",
            "shape": "板形",
            "surface": "表面",
            "perf_comp": "成份性能",
            "act_weight": "实际吨位",
            "coil_num": "卷数",
            "plot_dist_absolute": "绝对量分布图",
            "plot_dist_relative": "相对量分布图"
        }
        self.weeker = Weeker(self.current_year)

    def add_one_table(self, document, summary):

        def cut_tail(v_str):
            if v_str.endswith(".0"):
                return v_str.split(".")[0]
            else:
                return v_str

        summary = summary.round(2)
        row_num = len(summary.index) + 1
        col_num = len(summary.columns) + 1
        print(row_num, col_num)
        table = document.add_table(rows=row_num, cols=col_num)
        # 表格第一行为DataFrame的列名
        hdr_cells = table.rows[0].cells
        side_cells = table.columns[0].cells
        i = 1
        for val in summary.columns:
            hdr_cells[i].text = cut_tail(str(val))
            i = i + 1

        i = 1
        for val in summary.index:
            side_cells[i].text = cut_tail(str(val))
            i = i + 1

        i = 1
        for col in summary.columns:
            j = 1
            for idx in summary.index:
                table.columns[i].cells[j].text = (
                    cut_tail(str(summary.loc[idx, col]))
                    # 注意cell的text只能接收字符串
                )
                j = j + 1
            i = i + 1
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Table Grid"
        document.add_paragraph("")
