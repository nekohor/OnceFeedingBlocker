from context import Context
from oncefeeding import OnceFeeding
from analyzer import Analyzer
from record import Record
from entry import Entry
from pptxrender import PPTXRender
from trender import Trender


def main(ent):

    ctx = Context(ent)

    for idx in ctx.config_table.index:
        rec = Record(ctx, idx)
        fed = OnceFeeding(ctx, rec)
        Analyzer(ctx, fed, rec)


def render(ent):
    ctx = Context(ent)
    for idx in ctx.config_table.index:
        rec = Record(ctx, idx)
        ppt_render = PPTXRender(ctx, rec)
        ppt_render.build_pptx()

        trnd = Trender(ctx, rec)
        trnd.plot()


if __name__ == '__main__':

    ent = Entry()
    # ========== freqency =============
    # ent.frequency = "weekly"
    ent.frequency = "monthly"
    # =================================

    # ========== current ==============
    ent.month_num = 201902
    # ent.week_num
    # =================================

    ent.table_use = "single"
    # ent.table_use = "normal"

    # for select by month in database
    ent.start_month = 201902
    ent.end_month = 201902

    # main(ent)

    # now render func is just for single table use
    render(ent)
