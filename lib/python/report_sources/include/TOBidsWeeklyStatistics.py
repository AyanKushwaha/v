
import carmensystems.publisher.api as prt


def create_timeoff_bids_weekly_statistics(timeOfData, headerBackground):
    weekly_col = prt.Row()
    weekly_col.add(get_timeoff_bids_weekday_data(timeOfData, headerBackground))
    weekly_col.add(prt.Row(''))
    return(weekly_col)

def get_timeoff_bids_weekday_data(timeOfData, headerBackground):

    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    box = prt.Column()
    box.add(dataRow("Weekdays", weekdays, headerBackground, table_header=True))
    t_bids = []
    g_bids = []
    p_bids = []
    for weekday in weekdays:
        t_bid = timeOfData.getWeekdaySum("Placed Bids", weekday)
        g_bid = timeOfData.getWeekdaySum("Fulfilled Bids", weekday)

        t_bids.append(t_bid)
        g_bids.append(g_bid)
        if t_bid > 0:
            p_bids.append(int(round(float(g_bid) / float(t_bid) * 100 , 0)))
        else:
            p_bids.append(0)

    box.add(dataRow("Placed Bids", t_bids))
    box.add(dataRow("Fulfilled Bids", g_bids))
    box.add(dataRow("Ratio (%)", p_bids, percent=True))

    return box

def dataRow(header, items, headerBackground=None, percent=False, table_header=False):
    """
    Generates a row in the appropriate format.
    """
    output = prt.Row()

    if table_header:
        output.add(prt.Text(header, font=prt.Font(weight=prt.BOLD), background=headerBackground))
    else:
        output.add(prt.Text(header))

    for item in items:
        if percent:
            item = str(item) + "%"
        if table_header:
            output.add(prt.Text(item, align=prt.RIGHT, font=prt.Font(weight=prt.BOLD), background=headerBackground))
        else:
            output.add(prt.Text(item, align=prt.RIGHT))

    return output
