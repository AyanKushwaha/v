from Etab import Etable
import carmensystems.rave.api as r
import carmstd.plan as plan
import os


def add_etab_column(etab, col_type, col_name, default_val):
    """
    Adds a new column to etab, if not already added
    """

    if etab.hasColumn(col_name):
        return

    num_cols = etab.getNumOfColumns()
    new_etab = Etable()

    new_etab.appendColumns(etab)

    new_etab.appendColumn(col_type + col_name +",")

    for row in etab:
        new_row = row + (default_val, )
        new_etab.appendRow(new_row)

    return new_etab


def change_none_to_void(etab):
    # Change None to void
    num_cols = etab.getNumOfColumns()
    for r_ix in range(etab.getNumOfRows()):
        for c_ix in range(num_cols):
            cell = etab.getCell(r_ix+1, c_ix+1)
            if (cell == None or cell == "None"):
                etab.setCell(r_ix+1, c_ix+1, "void")

    return etab
        
def run():
    table_name = r.eval("leg.%aircraft_types_table%")[0]
    lp = plan.getCurrentLocalPlan()
    lp_etab_path = lp.getEtabPath()

    full_table_name = os.path.join(lp_etab_path, table_name)
    etab = Etable(full_table_name)

    new_etab = add_etab_column(etab, "S", "version", "")

    if new_etab:
        new_etab = change_none_to_void(new_etab)
        new_etab.save(filename=full_table_name)

if __name__ == '__main__':
    run()
