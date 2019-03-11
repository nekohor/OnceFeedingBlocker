import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set(color_codes=True)
sns.set(rc={'font.family': [u'Microsoft YaHei']})
sns.set(rc={'font.sans-serif':
            [u'Microsoft YaHei', u'Arial',
             u'Liberation Sans', u'Bitstream Vera Sans',
             u'sans-serif']})
mpl.style.use('ggplot')


class Trender:
    def __init__(self, ctx, rec):
        self.ctx = ctx
        self.rec = rec

        self.df_trend = self.get_trend_table()
        self.update_trend_table()

    def get_trend_table_name(self):
        return "trend/{freq}/trend_{year}_{freq}.xlsx".format(
            freq=self.ctx.frequency,
            year=self.ctx.current_year
        )

    def get_trend_table(self):
        df_trend = pd.read_excel(
            self.get_trend_table_name()
        )
        return df_trend

    def get_trend_item_name(self, tag):
        """对应df_trend["名称"]"""
        return "{}{}{}".format(
            self.rec.get_item_name(),
            self.ctx.lang_map[tag],
            self.ctx.cn_name
        )

    def update_trend_table(self):
        summary = pd.read_excel(
            self.rec.get_item_file_name("result.xlsx")
        )
        summary.index = summary[self.ctx.group_col]

        for tag in self.ctx.tags:
            rate = summary.loc[
                self.get_summary_idx(),
                "{}_qualify_rate".format(tag)
            ]
            self.df_trend.loc[
                self.get_trend_item_name(tag),
                self.get_cur_col()
            ] = rate

        self.df_trend.to_excel(
            self.get_trend_table_name())

    def get_summary_idx(self):
        summary_idx_map = {
            "weekly": self.ctx.weeker.get_date_bin(self.ctx.week_num),
            "monthly": self.ctx.month_num
        }
        return summary_idx_map[self.ctx.frequency]

    def get_format_col(self):
        format_col_map = {
            "weekly": "第{}周",
            "monthly": "{}月"
        }
        return format_col_map[self.ctx.frequency]

    def get_cur_num(self):
        cur_num_map = {
            "weekly": self.ctx.week_num,
            "monthly": self.ctx.mon
        }
        return cur_num_map[self.ctx.frequency]

    def get_cur_col(self):
        cur_col_map = {
            "weekly": self.get_format_col().format(self.get_cur_num()),
            "monthly": self.get_format_col().format(self.get_cur_num())
        }
        return cur_col_map[self.ctx.frequency]

    def get_col_list(self):
        if self.get_cur_num() < 8:
            this_num = 8
        else:
            this_num = self.get_cur_num()
        col_list = [
            self.get_format_col().format(i + 1)
            for i in range(this_num)]
        return col_list

    def get_table_for_doc(self):
        tbl = self.df_trend[
            ["负责人", "去年实绩", "目标值"] +
            self.get_col_list()[-8:]
        ]
        tbl["是否达标"] = self.get_reach_standard(self.df_trend)
        self.data = self.df_trend[self.get_col_list()]
        tbl["累计值"] = self.get_cumulative_value(self.data)
        return tbl

    def get_reach_standard(self, df):
        return [
            "√" if (x is True) else "×"
            for x in (
                df["目标值"] <= df[self.get_cur_col()]
            )
        ]

    def get_cumulative_value(self, df):
        return df.mean(axis=1).apply(lambda x: round(x, 2))

    def plot(self):
        self.FONTSIZE = 20
        self.col_max = 8
        self.col_list = self.get_col_list()
        self.plot_col = self.col_list[-self.col_max:]
        for tag in self.ctx.tags:
            trnd = self.df_trend.loc[self.get_trend_item_name(tag)]
            df_plot = self.build_plot_data(trnd)
            self.plot_single(df_plot, tag)

    def plot_single(self, df, tag):
        plt.figure(figsize=(21, 7))
        self.plot_chart(df)
        self.plot_table(df)
        plt.savefig(
            self.rec.get_item_file_name("{}_trend.png").format(tag)
        )
        plt.close("all")

    def build_plot_data(self, trnd):
        df = pd.DataFrame(
            index=self.plot_col,
            columns=["目标值", "实际值", "累计值"])

        print([trnd["目标值"]] * len(self.plot_col))
        print(trnd)
        print(self.plot_col)

        df["目标值"] = [trnd["目标值"]] * len(self.plot_col)
        df["实际值"] = trnd[self.plot_col]
        df["累计值"] = trnd[self.col_list].cumsum(
        )[-self.col_max:].apply(lambda x: round(x, 2))

        # 求累计均值的分母
        count_array = np.array([
            0 if np.isnan(x) else 1
            for x in trnd[self.col_list]
        ])
        cumcount_array = count_array.cumsum()[-self.col_max:]

        df["累计值"] = (df["累计值"] / cumcount_array).apply(lambda x: round(x, 2))
        return df

    def plot_chart(self, df):
        plt.subplot(2, 1, 1)
        size = df.shape[0]
        print(df)
        aim_vals = df["目标值"].values
        act_vals = df["实际值"].values
        acc_vals = df["累计值"].values
        x = np.arange(size)

        total_width, n = 0.8, 2     # 有多少个类型，只需更改n即可
        width = total_width / n
        half_width = width / 2
        x = x - (total_width - width) / 2

        plt.title(self.rec.get_item_name(), fontsize=self.FONTSIZE)
        plt.bar(x - half_width, aim_vals, width=width,
                label='目标值', color="#C0504D")
        plt.bar(x + half_width, act_vals, width=width,
                label='实际值', color="#9BBB59")
        plt.plot(acc_vals, marker='.', markersize=18,
                 label='累计值', color="#352A43")

        plt.ylim((0, 100))
        plt.xticks(np.arange(df.shape[0] + 1),
                   list(self.col_list) + [""], fontsize=self.FONTSIZE)
        plt.legend(loc="upper center", ncol=3, fontsize=self.FONTSIZE)

    def plot_table(self, df):
        plt.subplot(2, 1, 2, axisbg='#000000')
        col_labels = self.col_list
        print(col_labels)
        row_labels = ['目标值', '实际值', '累计值']
        table_vals = df[row_labels].T.values
        mytable = plt.table(cellText=table_vals, colWidths=[0.06] * 8,
                            rowLabels=row_labels, colLabels=col_labels,
                            # rowColours=row_colors, colColours=row_colors,
                            loc='center')
        mytable.set_fontsize(self.FONTSIZE)
        # mytable.auto_set_font_size(value=True)
        mytable.scale(2, 2)
        plt.grid(b=None)
        plt.axis('off')
