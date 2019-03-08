import os


class Record():

    def __init__(self, ctx, idx):
        super(Record, ).__init__()
        self.ctx = ctx
        self.idx = idx
        self.srs = self.get_record()

    def get_record(self):
        return self.ctx.config_table.loc[self.idx]

    def get_item_name(self):
        return "{}{}".format(self.srs["line"], self.srs["specific_grade"])

    def make_dir(self, dir_name):
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

    def get_item_dir(self):
        item_dir = "{}/{}".format(
            self.ctx.result_dir,
            self.get_item_name())
        self.make_dir(item_dir)
        return item_dir

    def get_item_file_name(self, name):
        """name must has suffix like 01.xlsx"""
        return (
            self.get_item_dir() +
            "/{}_{}".format(self.get_item_name(), name)
        )
