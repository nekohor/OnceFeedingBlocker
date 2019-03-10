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


class TrendPlot(object):

    def __init__(self, ctx, rec, trnd):
        self.ctx = ctx
        self.rec = rec

        # trnd is a series
        self.trnd = trnd
        self.df_plot = self.build_dataframe()

    def build_plot_data(self):
        df = pd.DataFrame()
        df["目标值"] = self.trnd["目标值"]
        df["实际值"] = self.trnd[self.trnd]
        df["累计值"] = self.record[self.wk_cols].cumsum()

        i = 0
        for idx in df.index:
            if np.isnan(df.loc[idx, "实际值"]):
                df.loc[idx, "num"] = np.nan
            else:
                i = i + 1
                df.loc[idx, "num"] = i

        df["累计值"] = (df["累计值"] / df["num"]).apply(lambda x: round(x, 2))

        return df

    def plot(self, plot_filename):
        plt.figure(figsize=(21, 7))
        self.plot_chart()
        self.plot_table()
        plt.savefig(plot_filename)
        plt.close("all")
        return plot_filename

    def plot_chart(self):
        plt.subplot(2, 1, 1)
        size = self.df.shape[0]
        print(self.df)
        aim_vals = self.df["目标值"].values
        act_vals = self.df["实际值"].values
        acc_vals = self.df["累计值"].values
        x = np.arange(size)

        total_width, n = 0.8, 2     # 有多少个类型，只需更改n即可
        width = total_width / n
        half_width = width / 2
        x = x - (total_width - width) / 2

        plt.title(self.plot_name, fontsize=self.cfg.FONTSIZE)
        plt.bar(x - half_width, aim_vals, width=width,
                label='目标值', color="#C0504D")
        plt.bar(x + half_width, act_vals, width=width,
                label='实际值', color="#9BBB59")
        plt.plot(acc_vals, marker='.', markersize=18,
                 label='累计值', color="#352A43")

        plt.ylim((0, 100))
        plt.xticks(np.arange(self.df.shape[0] + 1),
                   list(self.wk_cols) + [""], fontsize=self.cfg.FONTSIZE)
        plt.legend(loc="upper center", ncol=3, fontsize=self.cfg.FONTSIZE)

    def plot_table(self):
        plt.subplot(2, 1, 2, axisbg='#000000')
        col_labels = self.wk_cols
        print(col_labels)
        row_labels = ['目标值', '实际值', '累计值']
        table_vals = self.df[row_labels].T.values
        mytable = plt.table(cellText=table_vals, colWidths=[0.06] * 8,
                            rowLabels=row_labels, colLabels=col_labels,
                            # rowColours=row_colors, colColours=row_colors,
                            loc='center')
        mytable.set_fontsize(self.cfg.FONTSIZE)
        # mytable.auto_set_font_size(value=True)
        mytable.scale(2, 2)
        plt.grid(b=None)
        plt.axis('off')
