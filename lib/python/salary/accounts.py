# changelog {{{2
# [acosta:09/008@16:03] Now possible to use baselines.
# }}}

"""
Some routines for resetting/converting various compensation days accounts.
"""

# imports ================================================================{{{2
import modelserver
import logging

from AbsTime import AbsTime
from RelTime import RelTime

from tm import TM
from salary.reasoncodes import REASONCODES
from utils.Names import username
from utils.TimeServerUtils import now
from collections import namedtuple

# exports ================================================================{{{1
__all__ = [
    'CrewAccountList', 'CrewAccountBalance', 'CrewAccountDict',
    'CrewBalanceDict', 'AccountDict', 'AccountBalanceDict', 'Reset',
    'Conversion'
]

log = logging.getLogger('salary.accounts')
log.setLevel(logging.INFO)


# classes ================================================================{{{1

# baseline_tuple ---------------------------------------------------------{{{2
class baseline_tuple(tuple):
    """Tuple with time and value for a baseline."""
    def __new__(cls, baseline):
        if baseline is None:
            return tuple.__new__(cls, (None, 0))
        else:
            return tuple.__new__(cls, (baseline.tim, baseline.val or 0))

    def __init__(self, baseline):
        """Allow attribute access as well."""
        # tim can be None, but don't allow the value to be None (or
        # additions etc. will fail)
        if baseline is None:
            self.id = None
            self.crew = None
            self.tim = None
            self.val = 0
        else:
            self.id = baseline.id
            self.crew = baseline.crew
            self.tim = baseline.tim
            self.val = baseline.val

    def __int__(self):
        """The value of the baseline."""
        return int(self.val)


# default_filter ---------------------------------------------------------{{{2
def default_filter(*a, **k):
    """Private function. Default test that always passes."""
    return True


# GenericQuery -----------------------------------------------------------{{{2
class GenericQuery:
    """Base class, used for searches in both 'account_entry' and
    'account_baseline'."""
    def __init__(self, crew=None, account=None, hi=None, lo=None):
        self.crew = crew
        self.account = account
        self.hi = hi
        self.lo = lo

    def __iter__(self):
        """ Return result set. """
        try:
            return self.query()
        except modelserver.EntityNotFoundError, enf:
            # Invalid account or invalid crew
            return iter([])


# BaselineQuery ----------------------------------------------------------{{{2
class BaselineQuery(GenericQuery):
    """
    The poor design of Manpower's 'account_baseline', makes it impossible to
    use referers for the 'id' field (which should be a reference to 'account_set'
    named 'account', see BZ 32280).
    """
    def match(self, rec):
        try:
            # No need to compare crew, since if crew is not None, we will use
            # referers
            return (
                (self.hi is None or rec.tim < self.hi)
                and
                (self.lo is None or rec.tim >= self.lo)
                and
                (self.account is None or rec.id == self.account)
            )
        except (ValueError, modelserver.ReferenceError), err:
            # Referential errors or rec.tim is None
            return False
            
    def query(self):
        """ Create the query. """
        if self.crew is None:
            Q = []
            if not self.hi is None:
                Q.append('(tim<%s)' % (self.hi))
            if not self.lo is None:
                Q.append('(tim>=%s)' % (self.lo))
            if not self.account is None:
                Q.append('(id=%s)' % (self.account))
            if len(Q) > 1:
                return TM.account_baseline.search('(&%s)' % (''.join(Q)))
            elif Q:
                return TM.account_baseline.search('%s' % (''.join(Q)))
            else:
                return iter(TM.account_baseline)
        else:
            TM('account_baseline')
            return iter([x for x in TM.crew[(self.crew,)].referers('account_baseline', 'crew')
                    if self.match(x)])


# AccountQuery -----------------------------------------------------------{{{2
class AccountQuery(GenericQuery):
    """
    Return result set from query applied on the 'account_entry' entity.
    The flag 'published' is interpreted like this:
        'None' -> published and unpublished Vacation
        'False' -> unpublished only
        'True' -> published only
    """
    def __init__(self, crew=None, account=None, hi=None, lo=None, published=None):
        GenericQuery.__init__(self, crew=crew, account=account, hi=hi, lo=lo)
        self.published = published

    def match(self, rec):
        try:
            # No need to compare crew, since if crew is not None, we will use
            # referers
            return (
                (self.hi is None or rec.tim < self.hi)
                and
                (self.lo is None or rec.tim >= self.lo)
                and
                (self.account is None or rec.account.id == self.account)
                and
                (self.published is None or rec.published == self.published)
            )
        except (ValueError, modelserver.ReferenceError), err:
            # Referential errors or rec.tim is None
            return False
            
    def query(self):
        """ Create the query. """
        if self.crew is None:
            if self.account is None:
                Q = []
                if not self.hi is None:
                    Q.append('(tim<%s)' % (self.hi))
                if not self.lo is None:
                    Q.append('(tim>=%s)' % (self.lo))
                if not self.published is None:
                    Q.append('(published=%s)' % ('false', 'true')[bool(self.published)])
                if len(Q) > 1:
                    return TM.account_entry.search('(&%s)' % (''.join(Q)))
                elif Q:
                    return TM.account_entry.search('%s' % (''.join(Q)))
                else:
                    return iter(TM.account_entry)
            else:
                TM('account_entry')
                return iter([x for x in TM.account_set[(self.account,)].referers(
                    'account_entry', 'account') if self.match(x)])
        else:
            TM('account_entry')
            return iter([x for x in TM.crew[(self.crew,)].referers(
                'account_entry', 'crew') if self.match(x)])


# SortedAccountQuery -----------------------------------------------------{{{2
class SortedAccountQuery(AccountQuery):
    """
    AccountQuery() sorted by tim and entrytime.
    """
    def __iter__(self):
        """ Return result set. """
        try:
            L = [(time2num(x.tim), time2num(x.entrytime), x) for x in
                    self.query()]
            L.sort()
            return (x[2] for x in L)
        except modelserver.EntityNotFoundError, enf:
            # Invalid account or invalid crew
            return iter([])


# SortedBaselineQuery ----------------------------------------------------{{{2
class SortedBaselineQuery(BaselineQuery):
    """
    BaselineQuery() sorted by tim.
    """
    def __iter__(self):
        """ Return sorted list of entries """
        try:
            L = [(time2num(x.tim), x) for x in self.query()]
            L.sort()
            return (x[1] for x in L)
        except modelserver.EntityNotFoundError, enf:
            # Invalid account or invalid crew
            return iter([])


# AccountEntry -----------------------------------------------------------{{{2
class AccountEntry:
    """
    This is a wrapper class that is wrapped around the entities, to be
    able to perform sum(), min(), max(), and other operations on a list.

    The sum() function can be applied to a list of entries to get the
    balance at a given date.
    """
    def __init__(self, obj):
        """ obj is of type GenericEntity """
        self.object = obj
        try:
            # For account_entry
            self.value = obj.amount
            self.is_baseline = False
        except:
            # For account_baseline
            self.value = obj.val
            self.is_baseline = True

    def __repr__(self):
        return '<AccountEntry ' + ' '.join(['%s="%s"' % Z for Z in self.__dict__.iteritems()]) + '>'

    def __getattr__(self, val):
        try:
            return getattr(self.object, val)
        except:
            return self.__dict__[val]

    # These methods are for arithmetics and comparison.
    def __abs__(self): return abs(self.value)
    def __add__(self, other): return self.value + self.__cast(other)
    def __cmp__(self, other): return cmp(self.value, self.__cast(other))
    def __div__(self, other): return self.value / self.__cast(other)
    def __eq__(self, other): return self.value == self.__cast(other)
    def __ge__(self, other): return self.value >= self.__cast(other)
    def __gt__(self, other): return self.value >  self.__cast(other)
    def __int__(self): return self.value
    def __le__(self, other): return self.value <= self.__cast(other)
    def __lt__(self, other): return self.value <  self.__cast(other)
    def __mul__(self, other): return self.value * self.__cast(other)
    def __ne__(self, other): return self.value != self.__cast(other)
    def __neg__(self): return -self.value
    def __pos__(self): return +self.value
    def __sub__(self, other): return self.value - self.__cast(other)

    # This is regrettably needed...
    def __coerce__(self, other): return self.value, self.__cast(other)

    def __cast(self, other):
        try:
            return other.value
        except:
            return other

    def __iadd__(self, other):
        # Creating a new object or the sum operation would touch the first
        # object in a list.
        x = self.__class__(self.object)
        x.value += int(other)
        return x

    # Aliases
    __radd__ = __add__
    __rdiv__ = __div__
    __rmul__ = __mul__
    __rsub__ = __sub__
    __str__ = __repr__


# CrewAccountList --------------------------------------------------------{{{2
class CrewAccountList(list):
    """
    List of details for one crew and one account.  The list will contain
    entries (in the form of AccountEntry objects) from the datetime 'lo' (or
    the beginning), until the datetime 'hi'.

    To get a balance use the following construction:
        cal = CrewAccountList('20525', 'F7', AbsTime("20070516"))
        balance = sum(cal)
    """
    def __init__(self, crew, account, lastdate=None, firstdate=None, published=None,
            use_baseline=True):

        def filter(acc):
            return acc==account

        list.__init__(self)
        rows = CrewAccountDict(crew, lastdate, lo=firstdate, published = published,
                               filter=filter, use_baseline=use_baseline)
        if account in rows:
            self.extend(rows[account])
        else:
            self.extend([])



# CrewAccountBalance -----------------------------------------------------{{{2
class CrewAccountBalance:
    """
    Balance for one crew and one account.  The list will create a balance by
    adding entries from the datetime 'lo' (or the beginning), until the
    datetime 'hi'.

    To get a balance use the following construction:
        balance = int(CrewAccountBalance('20525', 'F7', AbsTime("20070516")))
    """
    def __init__(self, crew, account, hi, lo=None, published=None,
            use_baseline=True):
        self.balance = 0
        if use_baseline and lo is None:
            lo, self.balance = baseline(crew, account, hi)
        for x in AccountQuery(crew=crew, account=account, hi=hi, lo=lo,
                published=published):
            self.balance += x.amount

    def __int__(self):
        """ Return the balance. """
        return self.balance


# CrewBaselineDict -------------------------------------------------------{{{2
class CrewBaselineDict(dict):
    """
    Dictionary of baseline values for one crew and several accounts.

    CrewBaselineDict(...) = {
        'account_1': baseline_tuple1,
        'account_2': baseline_tuple2,
        ...
        'account_N': baseline_tupleN,
    }
    where:
        baseline_tuple = (<latest baseline time>, <baseline balance>)
    """
    def __init__(self, crew, hi=None, lo=None, filter=default_filter):
        dict.__init__(self)

        # Figure out when the latest baseline was created
        latest_baseline_run = AbsTime("1JAN1986")
        for entry in TM.accumulator_int_run.search("(accname='balance')"):
            try:
                key = entry.acckey
                # Are baselines always created at the same time for F and C?
                # Maybe the crew main category needs to be checked.
                if key in ('C','F'):
                    latest_baseline_run = AbsTime(entry.accstart)
            except Exception, err:
                Errlog.log('accounts.py:: Getting baseline %s'%err)

        for b in SortedBaselineQuery(crew=crew, hi=hi, lo=lo):
            account = b.id
            if filter(account):
                if b.tim >= latest_baseline_run:
                    if account in self:
                        tim, val = self[account]
                        # Keep the latest baseline
                        if b.tim >= tim:
                            self[account] = baseline_tuple(b)
                    else:
                        self[account] = baseline_tuple(b)
                if not account in self:
                    # Make sure that there is an entry at the latest baseline run 
                    self[account] = baseline_tuple(namedtuple("Baseline", ["id", "crew", "tim", "val"])(id=account, crew=crew, tim=latest_baseline_run, val=0))


# CrewAccountDict --------------------------------------------------------{{{2
class CrewAccountDict(dict):
    """
    Dictionary of lists for one crew and several accounts.

    CrewAccountDict(...) = {
        'account_1': [AccountEntry_11, AccountEntry_12, ..., AccountEntry_1N],
        'account_2': [AccountEntry_21, AccountEntry_22, ..., AccountEntry_2N],
        ...,
        'account_K': [AccountEntry_K1, AccountEntry_K2, ..., AccountEntry_KN],
    }
        
    Each dictionary entry will contain a list of details (AccountEntry objects).
    The list can be limited by entering a highest level date.  The low level
    date can be used if the balance at this date was zero.

    To get balances for each account use this technique:

        cad = CrewAccountDict('20525', AbsTime("20070516"))
        for account in cad:
            print "balance for account %s is %d" % (account, sum(cad[account]))

    The filter argument can be used to limit the selection of accounts.

        def myFilter(account):
            return account in ['VA', 'VA1', 'VA_SAVED']

        cad = CrewAccountDict('20525', AbsTime("20070516"), filter=myFilter)

    NOTE: This filter will have one argument which is a string and is expected
        to return True/False.
    """
    def __init__(self, crew, hi=None, lo=None, published=None,
            filter=default_filter, use_baseline=True):
        dict.__init__(self)
        if use_baseline and lo is None:
            __cbd = CrewBaselineDict(crew, hi=hi, lo=lo, filter=filter)
            for account in __cbd:
                self[account] = [AccountEntry(__cbd[account])]
        for x in SortedAccountQuery(crew=crew, hi=hi, lo=lo,
                published=published):
            try:
                account = x.account.id
            except modelserver.ReferenceError, re:
                continue
            if filter(account):
                try:
                    # Will fail if not 'use_baseline'
                    tim, val = __cbd[account]
                    if x.tim < tim:
                        continue
                except:
                    pass
                if account in self:
                    self[account].append(AccountEntry(x))
                else:
                    self[account] = [AccountEntry(x)]


# CrewBalanceDict --------------------------------------------------------{{{2
class CrewBalanceDict(dict):
    """
    Dictionary of balances for one crew and several accounts.

    CrewBalanceDict(...) = {
        'account_1': balance_1,
        'account_2': balance_2,
        ...,
        'account_N': balance_N,
    }
        
    Each dictionary entry will contain a balance.  The balance value is created
    by adding entries until highest level date.  The low level date can be
    used if the balance at this date was zero (or if we had a baseline value).

    To get balances for each account use this technique:

        cbd = CrewBalanceDict('20525', AbsTime("20070516"))
        for account in cbd:
            print "balance for account %s is %d" % (account, cbd[account])

    The filter argument can be used to limit the selection of accounts:

        def myFilter(account):
            return account in ['VA', 'VA1', 'VA_SAVED']

        cbd = CrewBalanceDict('20525', AbsTime("20070516"), filter=myFilter)

    NOTE: This filter will have one argument which is a string and is expected
        to return True/False.
    """
    def __init__(self, crew, hi=None, lo=None, published=None,
            filter=default_filter, use_baseline=True):
        dict.__init__(self)
        if use_baseline and lo is None:
            __cbd = CrewBaselineDict(crew, hi, lo, filter)
            for account in __cbd:
                self[account] = int(__cbd[account])
        for x in AccountQuery(crew=crew, hi=hi, lo=lo, published=published):
            try:
                account = x.account.id
            except modelserver.ReferenceError, re:
                continue
            if filter(account):
                try:
                    tim, val = __cbd[account]
                    if x.tim < tim:
                        continue
                except:
                    pass
                if account in self:
                    self[account] += x.amount
                else:
                    self[account] = x.amount


# AccountBaselineDict ----------------------------------------------------{{{2
class AccountBaselineDict(dict):
    """
    Dictionary of baselines for one account.

    AccountBaselineDict(...) = {
        'crewid_1': baseline_tuple1,
        'crewid_2': baseline_tuple2,
        ...
        'crewid_N': baseline_tupleN,
    }
    where:
        baseline_tuple = (<latest baseline time>, <baseline balance>)

    NOTE: This filter will have one argument which is a modelserver.Entity
        object and is expected to return True/False.
    """
    def __init__(self, account, hi, lo=None, filter=default_filter):
        dict.__init__(self)
        for b in SortedBaselineQuery(account=account, hi=hi, lo=lo):
            try:
                crewid = b.crew.id
            except modelserver.ReferenceError, re:
                continue
            if filter(b):
                if crewid in self:
                    tim, val = self[crewid]
                    if b.tim > tim:
                        self[crewid] = baseline_tuple(b)
                else:
                    self[crewid] = baseline_tuple(b)


# AccountDict ------------------------------------------------------------{{{2
class AccountDict(dict):
    """
    Dictionary of lists for one account and several crew members.

    AccountDict(...) = {
        'crewid_1': [AccountEntry_11, AccountEntry_12, ..., AccountEntry_1j],
        'crewid_2': [AccountEntry_21, AccountEntry_22, ..., AccountEntry_2j],
        ...,
        'crewid_i': [AccountEntry_i1, AccountEntry_i2, ..., AccountEntry_ij],
    }
        
    Each dictionary entry will contain a list of details (AccountEntry objects).
    The list can be limited by entering a highest level date.  The low level
    date can be used if the balance at this date was zero.

    To get balances for each account use this technique:

        ad = AccountDict('VA', AbsTime("20070516"))
        for crew in ad:
            print "VA balance for crewid %s is %d" % (crew, sum(ad[crew]))

    The filter argument can be used to limit the selection of crew:

        def myFilter(crew):
            # Return True if crew is FlightCrew, else False
            ...

    NOTE: This filter will have one argument which is a modelserver.Entity
        object and is expected to return True/False.

        ad = AccountDict('VA', AbsTime("20070516"), filter=myFilter)
    """
    def __init__(self, account, hi, lo=None, published=None,
            filter=default_filter, use_baseline=True):
        dict.__init__(self)
        if use_baseline and lo is None:
            __abd = AccountBaselineDict(account, hi, lo, filter)
            for crewid in __abd:
                self[crewid] = [AccountEntry(__abd[crewid])]
        for x in SortedAccountQuery(account=account, hi=hi, lo=lo,
                published=published):
            try:
                crewid = x.crew.id
            except modelserver.ReferenceError, re:
                continue
            if filter(x):
                try:
                    tim, val = __abd[crewid]
                    if x.tim < tim:
                        continue
                except:
                    pass
                if crewid in self:
                    self[crewid].append(AccountEntry(x))
                else:
                    self[crewid] = [AccountEntry(x)]


# AccountBalanceDict -----------------------------------------------------{{{2
class AccountBalanceDict(dict):
    """
    Dictionary of balances for one account and several crew members.

    AccountBalanceDict(...) = {
        'crewid_1': balance_1,
        'crewid_2': balance_2,
        ...,
        'crewid_N': balance_N,
    }
        
    Each dictionary entry will contain a balance.  The balance value is created
    by summing entries until highest level date.  The low level date can be
    used if the balance at this date was zero.

    To get balances for each account use this technique:

        abd = AccountBalanceDict('VA', AbsTime("20070516"))
        for crew in abd:
            print "VA balance for crewid %s is %d" % (crew, abd[crew])

    The filter argument can be used to limit the selection of crew:

        def myFilter(crew):
            # Return True if crew is FlightCrew, else False
            ...

    NOTE: This filter will have one argument which is a modelserver.Entity
        object and is expected to return True/False.

        abd = AccountBalanceDict('VA', AbsTime("20070516"), filter=myFilter)
    """
    def __init__(self, account, hi, lo=None, published=None,
            filter=default_filter, use_baseline=True):
        dict.__init__(self)
        if use_baseline and lo is None:
            __abd = AccountBaselineDict(account, hi, lo, filter)
            for crewid in __abd:
                self[crewid] = int(__abd[crewid])
        for x in AccountQuery(account=account, hi=hi, lo=lo,
                published=published):
            try:
                crewid = x.crew.id
            except modelserver.ReferenceError, re:
                continue
            if filter(x):
                try:
                    tim, val = __abd[crewid]
                    if x.tim < tim:
                        continue
                except:
                    pass
                if crewid in self:
                    self[crewid] += x.amount
                else:
                    self[crewid] = x.amount


# Reset ------------------------------------------------------------------{{{2
class Reset:
    """
    Base class for reset jobs.  This class can be used directly.

        Reset("BOUGHT", AbsTime("20070517")).reset()
    """
    def __init__(self, account, hi, lo=None, reason=None, filterfunc=None):
        # No use for values other than 'None' for 'lo', avoid that.
        if not reason:
            reason = REASONCODES['PAY']
        self.filterfunc = filterfunc
        self.reason = reason
        self.account = account
        self.hi = hi
        self.lo = lo
        self.username = username()

    def reset(self):
        """ Create out payment records for each positive value in account."""
        log.info("Reset account %s up %s-%s", self.account, self.lo, self.hi)
        abd = AccountBalanceDict(self.account, self.hi, self.lo,
                filter=self.filter, use_baseline=True)

        # Add result of previous RESET runs so we are able to run this job
        # several times.
        prev_reset = AccountBalanceDict(self.account, self.hi + RelTime(1),
                self.hi, filter=self.reset_filter)
        for crew in prev_reset:
            abd[crew] = abd.get(crew, 0) + prev_reset[crew]
        
        # Create reset records
        count = 0
        sum = 0
        sign = -1 if self.account in ('SOLD', 'F36') else 1
        for (id, value) in abd.iteritems():
            if value * sign > 0: # before: SOLD and F36 was always counted, also when positive
                log.info("  Reset %s day crew %s (%f)", self.account, id, value / 100.0)
                count += 1
                sum += value
                self.record(id, -value)
        log.info("Created %d reset records for %s (sum: %f)", count, self.account, sum / 100.0)

    def record(self, id, amount):
        """ Add record to account_entry. """
        if amount != 0:
            rec = TM.account_entry.create((TM.createUUID(),))
            rec.crew = TM.crew[id,]
            rec.tim = self.hi
            rec.account = TM.account_set[self.account,]
            rec.source = strclass(self.__class__)
            rec.amount = amount
            rec.man = True # SASCMS-1209
            # rec.si = None
            rec.rate = 100 * (1, -1)[amount < 0]
            rec.published = True
            rec.reasoncode = self.reason
            rec.entrytime = now()
            rec.username = self.username

    def filter(self, ent):
        if self.filterfunc:
            return self.filterfunc(ent)
        return True

    def reset_filter(self, ent):
        return self.filter(ent) and (ent.reasoncode == self.reason)



# Conversion -------------------------------------------------------------{{{2
class Conversion:
    """
    Base class for conversion jobs.  This class must be subclassed.  For
    examples, see 'compconv.py'.
    """
    def __init__(self, bookingDate, day_rate=100):
        self.bookingDate = bookingDate
        # How many days an entry is worth (should always be 1 day for F-day
        # conversions)
        self.day_rate = day_rate 
        self.username = username()

    def record(self, id, account, amount):
        """ Add record to account_entry. """
        if amount != 0:
            rec = TM.account_entry.create((TM.createUUID(),))
            rec.crew = TM.crew[id,]
            rec.tim = self.bookingDate
            rec.account = TM.account_set[account,]
            rec.source = strclass(self.__class__)
            rec.amount = amount
            rec.man = False
            # rec.si = None
            rec.published = True
            # rate -> same sign as amount; days = amount / rate
            rec.rate = self.day_rate * amount / abs(amount)
            rec.reasoncode = (REASONCODES['OUT_CONV'], REASONCODES['IN_CONV'])[amount > 0]
            rec.entrytime = now()
            rec.username = self.username


# public functions ======================================================={{{1

# balance ----------------------------------------------------------------{{{2
def balance(crew, account, timestamp, published=True):
    """Return balance for crew member's account at timestamp."""
    return int(CrewAccountBalance(crew=crew, account=account,
        hi=timestamp, published=published, use_baseline=True))


# baseline ---------------------------------------------------------------{{{2
def baseline(crew, account, timestamp):
    """Return baseline values for crew member's account at timestamp."""
    try:
        return max([baseline_tuple(x) for x in
            BaselineQuery(crew=crew, account=account, hi=timestamp)])
    except:
        # No baseline found with 'tim' less than 'hi'
        return baseline_tuple(None)


# private ================================================================{{{1
def strclass(cls):
    """ Return <module_name>.<class_name>. """
    return "%s.%s" % (cls.__module__, cls.__name__)


def time2num(a):
    if a is None:
        return 0
    return int(a)


# bit --------------------------------------------------------------------{{{2
def bit():
    """ For basic tests. """
    import test_accounts
    test_accounts.main()


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    bit()


# modeline ==============================================================={{{2
# vim: set fdm=marker fdl=1:
# eof
