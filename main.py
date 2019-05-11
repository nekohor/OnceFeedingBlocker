from context import Context
from oncefeeding import OnceFeeding
from analyzer import Analyzer
from record import Record
from entry import Entry
from pptxrender import PPTXRender
from docxrender import DOCXRender
from trender import Trender
import logging

logging.basicConfig(
    format=(
        "%(asctime)s - %(pathname)s[line:%(lineno)d] - "
        "%(levelname)s: %(message)s"
    ),
    level=logging.DEBUG)


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

        if ctx.frequency == "monthly":
            pptx_render = PPTXRender(ctx, rec)
            pptx_render.build_pptx()

        if ctx.table_use == "single":
            trnd = Trender(ctx, rec)
            trnd.plot()

            docx_render = DOCXRender(ctx, rec, trnd)
            docx_render.build_docx()


if __name__ == '__main__':

    ent = Entry()
    # ========== freqency =============
    ent.frequency = "weekly"
    # ent.frequency = "monthly"
    # =================================

    # ========== current ==============
    ent.mdate_num = 201904
    ent.week_num = 19
    # =================================

    ent.table_use = "single"
    # ent.table_use = "normal"

    # for select by month in database just like range
    ent.start_month = 201903
    ent.end_month = 201904

    ent.year_list = [2018, 2019]

    ent.crit_file_path = "e:/crit_result_data/crti_1580_cold_20190401_20190429.xlsx"

    main(ent)

    # now render func is just for single table use
    render(ent)
