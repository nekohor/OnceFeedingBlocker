from context import Context
from oncefeeding import OnceFeeding
from analyzer import Analyzer
from record import Record
from entry import Entry


def main(ent):

    ctx = Context(ent)

    for idx in ctx.config_table.index:
        rec = Record(ctx, idx)
        fed = OnceFeeding(ctx, rec)
        ana = Analyzer(ctx, fed, rec)
        ana


if __name__ == '__main__':

    ent = Entry()
    # ent.frequency = "weekly"
    ent.frequency = "monthly"

    ent.table_use = "single"

    # time_segment =
    ent.start_month = 201902
    ent.end_month = 201902

    main(ent)
