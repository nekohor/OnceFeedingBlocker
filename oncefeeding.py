from dateutil.parser import parse
from datetime import datetime
import pandas as pd
import rollen

from defects import Defects
import logging


class OnceFeeding():

    def __init__(self, ctx, rec):

        self.ctx = ctx
        self.rec = rec
        self.record = self.rec.get_record()

        self.sub_qualify_list = [
            "{}_qualify".format(sub) for sub in self.ctx.sub_list
        ]

        # step
        self.get_data()

        self.df_qualify = self.build_qualify(self.df_block)

        if self.ctx.frequency == "monthly":
            self.df_final = self.df_qualify
        else:
            self.df_final = self.cut_date(self.df_qualify)

        self.summary = self.get_summary(self.df_final)
        self.summary.to_excel(
            self.rec.get_item_file_name("result.xlsx")
        )

    def get_data(self):

        line = "{}".format(self.record["line"])

        rln = rollen.roll(line)

        self.df_block = rln.db.table("shift_block").where(
            "month", "in", self.ctx.mdates).get()

        self.df_cid = rln.db.table("cid").where(
            "month", "in", self.ctx.mdates).get()

        self.df_perform = rln.db.table("performance_components").where(
            "month", "in", self.ctx.year_list).get()

        self.df_block = self.prepare(self.df_block)

    def prepare(self, df):

        specific_grade = self.record["specific_grade"]

        df = self.ctx.utils.grade.select(
            df, "steel_grade", specific_grade)

        df["block_reason"] = (df["外观缺陷"] + df["表检缺陷"]).apply(lambda x: str(x))

        df["record_qualify"] = [
            1 if ("合格" in state) else 0
            for state in df["block_state"]
        ]

        cols = ["datetime", "aim_thick", "aim_width"]

        for col in cols:
            df[col] = self.df_cid[col]

        return df

    def build_qualify(self, df):

        logging.info(self.df_block.shape)
        df = self.build_shape_qualify(df)

        logging.info(self.df_block.shape)
        df = self.build_surface_qualify(df)

        logging.info(self.df_block.shape)
        df = self.build_perf_comp_qualify(df)

        df = self.merge_qualify(df)
        # calc qualify weight
        df = self.calc_qualify_weight(df)
        return df

    def build_shape_qualify(self, df):
        """ shape, surface qualify calc """
        suffix = "LEVEL"

        if self.ctx.frequency == "weekly":
            df["shape_qualify"] = 1
        else:
            level_cols = [
                x + suffix for x in self.ctx.defects["shape"]]

            logging.info(self.ctx.df_crit)
            logging.info(self.ctx.df_crit.columns)

            df[level_cols] = self.ctx.df_crit[level_cols]

            df["shape_qualify"] = 1

            for defect_col in self.ctx.defects["shape"]:
                df[defect_col] = [0 if x in ["D", "E"] else 1
                                  for x in df[defect_col + suffix]]

                df["shape_qualify"] *= df[defect_col]

        return df

    def build_surface_qualify(self, df):
        """ surface qualify calc """
        div_list = ["surface"]

        for div in div_list:

            df["{}_mult".format(div)] = 1

            for defect in self.ctx.defects[div]:

                df[defect] = [
                    0 if (defect in reason) else 1
                    for reason in df["block_reason"]
                ]

                df["{}_mult".format(div)] *= df[defect]

            df["{}_add".format(div)] = (
                df[["{}_mult".format(div), "record_qualify"]].apply(
                    lambda x: x.sum(), axis=1)
            )

            df["{}_qualify".format(div)] = [
                0 if (q == 0) else 1
                for q in df["{}_add".format(div)]
            ]

        return df

    def build_perf_comp_qualify(self, df):
        """performance and components qualify calc"""

        df["perf_comp_qualify"] = 1

        for coil_id in df.index:

            print("perf_comp", coil_id)

            if coil_id in self.df_perform.index:

                df.loc[coil_id, "perf_comp"] = (
                    self.df_perform.loc[coil_id, "block_reason"])

                df.loc[coil_id, "perf_comp_qualify"] = 0

            else:
                pass

        return df

    def merge_qualify(self, df):
        df["qualify"] = 1

        for sub_qualify in self.sub_qualify_list:
            df["qualify"] *= df[sub_qualify]

        return df

    def calc_qualify_weight(self, df):
        """ calc qualify weight """
        df["slab_weight"] = self.df_cid["slab_weight"]
        df["act_weight"] = self.df_cid["coil_weight"]
        df["qualify_weight"] = df["qualify"] * df["act_weight"]

        for sub_qualify in self.sub_qualify_list:

            df["{}_weight".format(sub_qualify)] = (
                df[sub_qualify] * df["act_weight"])

        return df

    def cut_date(self, df):
        # deal with month list
        df["datetime"] = self.df_cid["datetime"]
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
        print(weektime_list)
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
