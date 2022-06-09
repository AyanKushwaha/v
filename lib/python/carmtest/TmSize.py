############################################################

#
# Module containing functions to measure the database size
#
############################################################
                                                                                                                                                          
import tm
import operator

def printTablesSize():
    """
    Prints the loaded tables size
    """

    TM = tm.TM

    res = []

    for table in TM._entity:
        table_name = table.entity
        table_size = len(TM.table(table_name))
        if table_size != 0:
            res.append((table_name, table_size))

    res.sort(key=operator.itemgetter(1), reverse=True)
    for r in res:
        print "%s: %d" %r

