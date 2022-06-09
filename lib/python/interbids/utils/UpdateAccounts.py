from tm import TM
import modelserver
import Errlog
import carmusr.AccountHandler as AH
import Cui
import carmensystems.rave.api as R
from AbsTime import AbsTime
from RelTime import RelTime
import utils.Names as Names
import interbids.rostering.days_off_response_handler as days_off_response_handler

import carmusr.application as application

def updateAccounts():
    """
    Finds certain objects in plan and adds them to account_entry table if the entry doesn't already exist.
    """
    account_list = ['FS']
    need_reload = False
    username = Names.username()
    nowtime = AH._get_now_time()

    # Set not published in rostering, but published in Pre and CCT
    if application.isPlanning:
        published = False
    else:
        published = True
    
    ppstart = R.eval("pp_start_time")[0]
    ppend = R.eval("pp_end_time")[0]
    ppend += RelTime('00:01')
    
    Errlog.log("UpdateAccounts.py:: -------------------------------------------")
    Errlog.log("UpdateAccounts.py:: Starting to update %s accounts for all crew" % account_list[0])
    Errlog.log("UpdateAccounts.py:: -------------------------------------------")

    #initialize created account count
    account_count = {}
    for account in account_list:
        account_count[account] = 0
    
    default_bag = R.context('sp_crew').bag()
    leg_filter = ('leg.%%code%% = "%s" and leg.%%start_hb%% >= %s and leg.%%end_hb%% <= %s' % (account_list[0], ppstart, ppend))
    existingAccountEntries = getExistingAccountEntries(account)
    
    for roster_bag in default_bag.iterators.roster_set():
        crew_id = roster_bag.crew.id()

        for leg_bag in roster_bag.iterators.leg_set(where=leg_filter, sort_by='leg.%start_utc%'):
                start_hb = leg_bag.leg.start_hb()
                end_hb = leg_bag.leg.end_hb()
                days = int((end_hb - start_hb)/RelTime('24:00'))
                amount = 0
                start_date = None
                
                for i in xrange(days):
                    date = start_hb + i*RelTime('24:00')
                    if (crew_id not in existingAccountEntries.keys()) or (date not in existingAccountEntries[crew_id]):
                        amount += -100
                        if not start_date:
                            start_date = date
                    else:
                        Errlog.log("UpdateAccounts.py:: %s already exists on %s for crew %s" % (account, start_hb, crew_id))
                if amount:
                    entry={'crew':crew_id,
                           'amount':amount,
                           'account':account,
                           'tim':start_date,
                           'source':'model',
                           'si':'Created by UpdateAccounts script',
                           'reason':'OUT Correction',
                           'nowtime':nowtime,
                           'username':username,
                           'rate':100,
                           'published':False
                          }
    
                    if account_count.has_key(account):
                        account_count[account] += 1
                    else:
                        account_count[account] = 1 # in case leg affects account not in list.
                    
                    Errlog.log("UpdateAccounts.py:: Found %s on %s for crew %s" % (account, start_hb, crew_id))
                    
                    AH._create_account_entry(entry)
                    need_reload = True
    
    for account, count in account_count.items():
        Errlog.log("UpdateAccounts.py:: Added %s %s entries to account_entry"%\
                   (count, account))
    
    if need_reload:
        Errlog.log("UpdateAccounts.py:: Reload account_entry")
        Cui.CuiReloadTable("account_entry", 1)
            
    Errlog.log("UpdateAccounts.py:: Finished update of %s accounts for all crew" % account_list[0])
    
def getExistingAccountEntries(account):
    """
    Returns a dictionary of accounts already in account_entry table.
    """
    AccountEntries = {}
    for row in TM.account_entry.search('(account=%s)' % (account)):

        if not row.rate:
            Errlog.log("UpdateAccounts.getExistingAccountEntries:: rate is empty for crew %s account %s on %s" % (row.crew.id, account, row.tim))
            continue

        for i in xrange(abs(row.amount/row.rate)):
            try:
                AccountEntries[row.crew.id].append(row.tim + i*RelTime('24:00'))
            except:
                AccountEntries[row.crew.id] = []
                AccountEntries[row.crew.id].append(row.tim + i*RelTime('24:00'))
    return AccountEntries

def populateRosterRequestAwards():
    """
    Add F7S and FS entries from account_entry to roster_request_awards
    """
    pp_start, = R.eval('fundamental.%pp_start%')
    pp_end, = R.eval('fundamental.%pp_end%')
    pp_end += RelTime('00:01')

    Errlog.log("UpdateAccounts.populateRosterRequestAwards:: -------------------------------------------")
    Errlog.log("UpdateAccounts.populateRosterRequestAwards:: Clear roster_request_awards from %s to %s" % (pp_start, pp_end))
    Errlog.log("UpdateAccounts.populateRosterRequestAwards:: -------------------------------------------")

    clearRosterRequestAwards(pp_start, pp_end)

    Errlog.log("UpdateAccounts.populateRosterRequestAwards:: -------------------------------------------")
    Errlog.log("UpdateAccounts.populateRosterRequestAwards:: Starting to populate roster_request_awards")
    Errlog.log("UpdateAccounts.populateRosterRequestAwards:: -------------------------------------------")

    account_list = ['FS', 'F7S']
    default_bag = R.context('sp_crew').bag()

    leg_filter = ('(leg.%%code%% = "%s" or leg.%%code%% = "%s") and leg.%%start_hb%% >= %s and leg.%%end_hb%% <= %s' % (account_list[0], account_list[1], pp_start, pp_end))

    roster_items = {}

    for roster_bag in default_bag.iterators.roster_set():
        crew_id = roster_bag.crew.id()
        roster_items[crew_id] = []

        for leg_bag in roster_bag.iterators.leg_set(where=leg_filter, sort_by='leg.%start_utc%'):
            start_hb = leg_bag.leg.start_hb()
            end_hb = leg_bag.leg.end_hb()
            days = int((end_hb - start_hb)/RelTime('24:00'))
            account = str(leg_bag.leg.code())
            for i in xrange(days):
                date = start_hb + i*RelTime('24:00')
                roster_items[crew_id].append({'account':account, 'date':date})

    counter = {}
    counter[account_list[0]] = 0
    counter[account_list[1]] = 0

    for crew in roster_items.keys():
        crew_generic_entity = TM.table('crew')[(str(crew),)]
        crew_attributes = days_off_response_handler.CrewRequestAttributeSet(TM, crew_generic_entity)
        for entry in roster_items[crew]:
            for crew_group in crew_attributes.get_values("RequestGroup", date):
                Errlog.log("UpdateAccounts.populateRosterRequestAwards:: Trying to increment for [crew=%s\tcrew_group=%s\ttim=%s]" % (crew_generic_entity.id, crew_group.name+crew_group.cat, entry['date']))
                try:
                    award_row = TM.table("roster_request_awards")[(crew_group, entry['account'], entry['date'])]
                    award_row.awarded = award_row.awarded + 1
                except modelserver.EntityNotFoundError:
                    award_row = TM.table("roster_request_awards").create((crew_group, entry['account'], entry['date']))
                    award_row.awarded = 1
                counter[entry['account']] += 1

    for account in account_list:
        Errlog.log("UpdateAccounts.populateRosterRequestAwards:: Added %s %s entries to roster_request_awards" % (counter[account], account))

    Errlog.log("UpdateAccounts.populateRosterRequestAwards:: Reload roster_request_awards")
    Cui.CuiReloadTable("roster_request_awards", 1)

    Errlog.log("UpdateAccounts.populateRosterRequestAwards:: Finished populating of roster_request_awards")

def clearRosterRequestAwards(st,et):
    """
    Clear roster_request_awards table for the specified period.
    """
    for row in TM.roster_request_awards.search('(&(tim>=%s)(tim<%s))' % (st, et)):
        row.remove()
        Errlog.log("UpdateAccounts.clearRosterRequestAwards:: Removed [%s,%s,%s,%s]" % (row.crew_filter._id, row.request_type, row.tim, row.awarded))

if __name__ == "__main__":
    populateRosterRequestAwards()
