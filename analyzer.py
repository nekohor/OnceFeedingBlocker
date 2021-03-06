import numpy as np
import pandas as pd
from distplot import DistPlot
import logging


class Analyzer:

    def __init__(self, ctx, feed, rec):
        self.ctx = ctx
        self.feed = feed
        self.rec = rec

        self.record = rec.get_record()

        self.df_defect_desc = self.get_main_defect(self.feed.df_final)
        self.df_defect_desc.to_excel(
            self.rec.get_item_file_name("inter.xlsx")
        )

        self.ctx.tags = ["main"] + self.ctx.sub_list
        print(self.ctx.tags)
        for tag in self.ctx.tags:
            if self.df_defect_desc.shape[0] == 0:
                pass
            elif self.ctx.frequency == "weekly":
                pass
            else:
                self.build_pivot_table(self.df_defect_desc, tag)
                self.plot(self.df_defect_desc, tag)

    def get_main_defect(self, df_origin):
        df = df_origin
        df["main_qualify"] = df["qualify"]
        df["main_defect"] = np.nan

        if self.ctx.frequency == "monthly":
            df_shape = df[self.ctx.defects["shape"]]
            shape_defects = self.ctx.defects["shape"]
            for idx in df_shape.index:
                print("shape", idx)
                defect_idx_array = np.where(df_shape.loc[idx] == 0)[0]
                if len(defect_idx_array) == 0:
                    continue
                else:
                    defect_idx = defect_idx_array[0]
                    df.loc[idx, "shape_defect"] = shape_defects[defect_idx]
                    df.loc[idx, "main_defect"] = shape_defects[defect_idx]
        else:
            df.loc["shape_defect"] = np.nan

        df_surface = df[self.ctx.defects["surface"]]
        surface_defects = self.ctx.defects["surface"]
        for idx in df_surface.index:
            print("surface", idx)
            defect_idx_array = np.where(df_surface.loc[idx] == 0)[0]
            if len(defect_idx_array) == 0:
                continue
            else:
                defect_idx = defect_idx_array[0]
                df.loc[idx, "surface_defect"] = surface_defects[defect_idx]
                df.loc[idx, "main_defect"] = surface_defects[defect_idx]

        for idx in df.index:
            print("perf_comp", idx)
            perf_comp_defect = df.loc[idx, "perf_comp"]
            print(perf_comp_defect)
            if isinstance(perf_comp_defect, str):
                df.loc[idx, "perf_comp_defect"] = perf_comp_defect
                df.loc[idx, "main_defect"] = perf_comp_defect
            else:
                continue
        return df

    def select_block_data(self, df_origin, tag):
        df = df_origin.loc[df_origin["{}_qualify".format(tag)] == 0]
        # df = df.loc[df[self.ctx.group_col] == self.ctx.time_seg]
        df.to_excel(
            self.rec.get_item_file_name("{}_block.xlsx".format(tag))
        )
        return df

    def build_pivot_table(self, df_origin, tag):
        df = self.select_block_data(df_origin, tag)
        pt = pd.pivot_table(
            df,
            index=[
                self.ctx.group_col,
                "{}_defect".format(tag),
                "steel_grade"],
            values=["act_weight"],
            aggfunc=[np.sum, np.size]
        )
        try:
            pt.to_excel(
                self.rec.get_item_file_name(
                    "{}_pivot_table.xlsx".format(tag)
                )
            )
        except Exception as e:
            pass

        # pivot table for docx render
        # s = pd.DataFrame()

    def plot(self, df_origin, tag):

        df = self.select_block_data(df_origin, tag)

        df["plot_defect"] = df["{}_defect".format(tag)]
        df["plot_grade"] = df["steel_grade"]
        df["plot_thick"] = df["aim_thick"].apply(lambda x: round(x, 2))
        df["plot_width"] = df["aim_width"].apply(lambda x: x / 50 * 50)

        self.ctx.tag = tag

        dp = DistPlot(self.ctx, self.rec)
        dp.plot(df)
