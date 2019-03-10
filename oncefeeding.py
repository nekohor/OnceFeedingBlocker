from dateutil.parser import parse
from datetime import datetime
import pandas as pd


class OnceFeeding():

    def __init__(self, ctx, rec):
        self.ctx = ctx
        self.rec = rec
        self.record = rec.get_record()

        self.sub_qualify_list = [
            "{}_qualify".format(sub) for sub in self.ctx.sub_list
        ]
        # self.
        self.df_block, self.df_pc = self.get_data()
        self.df_filter = self.filter(self.df_block)
        self.df_qualify = self.qualify(self.df_filter)
        self.df_final = self.cut_date(self.df_qualify)
        self.summary = self.get_summary(self.df_final)
        self.summary.to_excel(
            self.rec.get_item_file_name("result.xlsx")
        )

    def get_data(self):
        df_block = self.ctx.db[
            "{}".format(self.record["line"])
        ].read_by_elems("act_block", "month", self.ctx.month_list)

        df_block.drop_duplicates("coil_id", "first", inplace=True)

        df_pc = self.ctx.db[
            "{}".format(self.record["line"])
        ].read_by_elems("performance_components", "month", self.ctx.year_list)

        return df_block, df_pc

    def filter(self, df):
        if self.record["selector"] == "normal":
            grade_col = self.record["grade_col"]
            specific_grade = self.record["specific_grade"]
            df_filter = self.ctx.gp.select_grade(
                df, grade_col, specific_grade)
        else:
            pass
        return df_filter

    def qualify(self, df):
        df["qualify"] = [
            1 if ("合格" in state) else 0
            for state in df["block_state"]
        ]

        self.defects = {}
        self.defects["shape"] = [
            "宽",
            "厚",
            "楔",
            "平直",
            "凸度"
        ]

        self.defects["surface"] = [
            "翘皮",
            "轧破",
            "烂尾",
            "夹杂",
            "裂纹",
            "气泡",
            "凹坑",
            "麻点",
            "压氧",
            "压入",
            "边损",
            "辊印",
            "锈垢",
            "紅锈",
            "走刀痕",
            "油污",
        ]

        # "shape", "surface" qualify calc
        div_list = ["shape", "surface"]
        for div in div_list:
            df["{}_mult".format(div)] = 1
            for defect in self.defects[div]:
                df[defect] = [
                    0 if (defect in reason) else 1
                    for reason in df["block_reason"]
                ]
                df["{}_mult".format(div)] *= df[defect]

            df["{}_add".format(div)] = (
                df[["{}_mult".format(div), "qualify"]].apply(
                    lambda x: x.sum(), axis=1)
            )

            df["{}_qualify".format(div)] = [
                0 if (q == 0) else 1
                for q in df["{}_add".format(div)]
            ]

        # performance and components qualify calc
        df["perf_comp_qualify"] = 1
        for coil_id in df.index:
            print(coil_id)
            if coil_id in self.df_pc.index:
                df.loc[coil_id, "perf_comp"] = (
                    self.df_pc.loc[coil_id, "block_reason"])
                df.loc[coil_id, "qualify"] = 0
                df.loc[coil_id, "perf_comp_qualify"] = 0
            else:
                pass

        # calc qualify weight
        df["slab_weight"] = df["板坯重量"]
        df["act_weight"] = df["实际重量"].apply(pd.to_numeric, errors='coerce')
        df["qualify_weight"] = df["qualify"] * df["act_weight"]

        for sub_qualify in self.sub_qualify_list:
            df["{}_weight".format(sub_qualify)] = (
                df[sub_qualify] * df["act_weight"])
        return df

    def cut_date(self, df):
        # deal with month list
        df["datetime"] = df["开始日期"].apply(lambda x: x + " ") + df["开始时间"]
        df["datetime"] = df["datetime"].apply(lambda x: parse(str(x)))

        # first_datetime = parse(str(df.head(1)["datetime"].values[0]))
        # last_datetime = parse(str(df.tail(1)["datetime"].values[0]))

        first_datetime = parse(str(self.ctx.start_month * 100 + 1))
        last_datetime = datetime.today()
        print(first_datetime)
        print(last_datetime)

        weektime_list = self.ctx.weeker.get_weektime_list(
            first_datetime,
            last_datetime
        )

        df["date_bin"] = pd.cut(
            df["datetime"],
            bins=weektime_list
        ).apply(lambda x: str(x))

        return df

    def get_summary(self, df_source):
        summary = pd.DataFrame()

        group_col = self.ctx.group_col
        df = df_source.loc[df_source[group_col].notnull()]

        summary["合格板坯块数"] = df.groupby(group_col)["qualify"].sum()
        summary["生产板坯块数"] = df.groupby(group_col)["slab_weight"].size()

        summary["合格板坯吨位"] = df.groupby(group_col)["qualify_weight"].sum()
        summary["生产板坯吨位"] = df.groupby(group_col)["slab_weight"].sum()

        summary["{}".format(self.ctx.cn_name)] = (
            summary["合格板坯吨位"] / summary["生产板坯吨位"] * 100
        ).apply(lambda x: round(x, 2))

        summary["main_qualify_rate"] = summary["{}".format(self.ctx.cn_name)]

        for sub_qualify in self.sub_qualify_list:
            summary["{}_weight".format(sub_qualify)] = (
                df.groupby(group_col)["{}_weight".format(sub_qualify)].sum()
            )
            summary["{}_rate".format(sub_qualify)] = (
                summary["{}_weight".format(sub_qualify)] /
                summary["生产板坯吨位"] * 100
            ).apply(lambda x: round(x, 2))

        # print(summary)
        return summary
