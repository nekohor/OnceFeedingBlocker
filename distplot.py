import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl

sns.set(color_codes=True)
sns.set(rc={'font.family': [u'Microsoft YaHei']})
sns.set(rc={'font.sans-serif':
            [u'Microsoft YaHei', u'Arial',
             u'Liberation Sans', u'Bitstream Vera Sans',
             u'sans-serif']})
mpl.style.use('ggplot')


class DistPlot():

    def __init__(self, ctx, rec):
        self.ctx = ctx
        self.rec = rec
        self.max_dist_num = int(12)

    def plot(self, df):
        cfg_table = self.ctx.plot_config
        for idx in cfg_table.index:
            cfg = cfg_table.loc[idx]
            plot_func_name = cfg["func"]
            getattr(self, plot_func_name)(cfg, df)

    def plot_dist_absolute(self, cfg, df):
        dist_col = cfg["dist_col_x"]
        data_col = cfg["data_col"]
        plot_kind = cfg["kind"]
        plot_color = cfg["color"]
        plot_alpha = cfg["alpha"]

        data_series = df.groupby(
            dist_col
        ).sum(
        ).sort_values(
            by=data_col, ascending=False
        )[data_col]

        if data_series.shape[0] > self.max_dist_num:
            data_series = data_series.iloc[:self.max_dist_num]

        data_series.plot(
            kind=plot_kind, color=plot_color, alpha=plot_alpha)
        self.title(cfg)
        self.labelxy(cfg)
        self.rotation(cfg)
        self.save(cfg)

    def plot_dist_relative(self, cfg, df):
        dist_col = cfg["dist_col_x"]
        data_col = cfg["data_col"]
        plot_kind = cfg["kind"]
        plot_color = cfg["color"]
        plot_alpha = cfg["alpha"]

        data_series = df.groupby(
            dist_col
        ).sum(
        ).sort_values(
            by=data_col, ascending=False
        )[data_col] / df[data_col].sum() * 100

        data_series = data_series.apply(lambda x: round(x, 2))

        if data_series.shape[0] > self.max_dist_num:
            data_series = data_series.iloc[:self.max_dist_num]

        data_series.plot(
            kind=plot_kind, color=plot_color, alpha=plot_alpha)
        self.title(cfg)
        self.labelxy(cfg)
        self.rotation(cfg)
        self.save(cfg)

    def plot_hex(self, cfg, df):
        col_x = cfg["dist_col_x"]
        col_y = cfg["dist_col_y"]
        sns.jointplot(df[col_x], df[col_y], kind='hex')
        self.title(cfg)
        self.labelxy(cfg)
        self.save(cfg)

    def title(self, cfg):
        plot_title = cfg["title"]
        plt.title(
            "{}一次封闭{}({})".format(
                self.rec.get_item_name(),
                plot_title,
                self.ctx.lang_map[cfg["data_col"]]
            )
        )

    def labelxy(self, cfg):
        plot_xlabel = cfg["xlabel"]
        plot_ylabel = cfg["ylabel"]
        plt.xlabel(plot_xlabel)
        plt.ylabel(plot_ylabel)

    def rotation(self, cfg):
        plot_rotation = cfg["rotation"]
        plt.xticks(rotation=plot_rotation)

    def save(self, cfg):
        plot_title = cfg["title"]
        plot_file_name = (
            self.rec.get_item_file_name(
                "{}_{}.png".format(self.ctx.tag, plot_title)
            )
        )
        plt.savefig(plot_file_name)
        plt.close("all")
