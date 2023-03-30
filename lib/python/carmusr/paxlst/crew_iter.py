# [acosta:07/327@11:00] Created.
# [acosta:07/334@13:28] Updated with "incremental" / "full" MCL.

"""
Get Rave variables for APIS crew lists (Crew Manifest and Master Crew List).
"""

from AbsTime import AbsTime
from RelTime import RelTime

from utils.rave import RaveIterator
from utils.selctx import FlightFilter, BasicContext
from utils.edifact.tools import ISO3166_1 as co


# Crew data faults ======================================================={{{1

class CrewIterFault:
    """Base class for all known crew list faults. The method 'test()' should
    return a list of failtexts. To each fault we should have a remedy
    explaining how to recover from the fault."""

    def test(self, crew, leg=None):
        raise NotImplementedError('test() not implemented')


class BlockedNationality(CrewIterFault):
    """Some crew is not allowed on some flights."""

    crew_from = None
    c_flight = None
    remedy = "Crew of %s nationality should not be rostered on flights to %s." % (crew_from, c_flight)

    def test(self, c, l):
        f = []
        if (l.end_country == self.c_flight or l.start_country == self.c_flight) and c.nationality == self.crew_from:
            f.append('%s flying from/to %s' % (self.crew_from, self.c_to))
        return f


class JP_US(BlockedNationality):
    """Japanese crew not allowed on flights to USA."""

    crew_from = "JP"
    c_flight = "US"


class CN_US(BlockedNationality):
    """Chinese crew not allowed on flights to USA."""

    crew_from = "CN"
    c_flight = "US"


class NoNationality(CrewIterFault):
    """Nationality not found."""

    remedy = "Update 'crew_document' with a valid passport."

    def test(self, c, l=None):
        f = []
        if not c.nationality or not c.passport:
            f.append('no valid passport - no nationality')
        return f


class BadCountryInDocuments(CrewIterFault):
    """Could not find country used in 'crew_document'."""

    remedy_general = ("Use only OFFICIAL two-letter country codes (see ISO-3166),"
        " these codes are found in the table 'country'.")
    remedy_spec = "The 'subtype' value of column 'doc' in table 'crew_document' needs to be updated with a valid country."
    remedy = "%s %s" % (remedy_spec, remedy_general)

    def test(self, c, l=None):
        f = []
        fmt = "invalid %s issuer '%s'"
        if c.passport:
            if self.country_code_failure(c.passport_issuer):
                f.append(fmt % ('passport', c.passport_issuer))
        if c.visa:
            if self.country_code_failure(c.visa_issuer):
                f.append(fmt % ('visa', c.visa_issuer))
        if hasattr(c, 'license_issuer'):
            if c.license_issuer:
                if self.country_code_failure(c.license_issuer):
                    f.append(fmt % ('license', c.license_issuer))
        return f

    def country_code_failure(self, cty):
        try:
            co.alpha2to3(cty)
            return False
        except:
            return True


class BadCountryBirthRes(BadCountryInDocuments):
    """Could not translate country of birth."""

    remedy_spec = "Update column 'bcountry' in table 'crew' with a valid country."
    
    def test(self, c, l=None):
        f = []
        if self.country_code_failure(c.birth_country):
            f.append('invalid country of birth')
        return f


class NoCrewPassport(CrewIterFault):
    """No passport or names missing."""

    remedy = ("Enter names to table 'crew_passport'. It is important that this"
        " table contains EXACTLY the same names as in the official passport.")

    def test(self, c, l=None):
        f = []
        if not c.gn:
            f.append('given name missing')
        if not c.sn:
            f.append('surname missing')
        return f


class NoRecentPassport(CrewIterFault):
    """No valid passport found."""

    remedy = "Update 'crew_document' with a valid passport."

    def test(self, c, l=None):
        f = []
        if not c.passport:
            f.append('no passport')
        return f


class DHSCategory(CrewIterFault):
    """No DHS category (no employment)."""

    remedy = ("The DHS category could not be determined, probably because the crew"
        " member lacks a valid employment record in the table 'crew_employment'.")

    def test(self, c, l=None):
        f = []
        if not c.dhs_category:
            f.append('DHS category missing')
        return f


class BirthData(CrewIterFault):
    """Missing birth data."""

    remedy = ("Update table 'crew' with birth data."
            " This data should have the same time and location as in the passport.")

    def test(self, c, l=None):
        f = []
        if not c.birth_country:
            f.append('country of birth missing')
        if not c.birth_place:
            f.append('place of birth missing')
        if not c.birthday:
            f.append('date of birth missing')
        return f
    

class Gender(CrewIterFault):
    """Unknown gender."""

    remedy = "Update table 'crew', column 'sex'."

    def test(self, c, l=None):
        f = []
        if not c.gender:
            f.append('cannot determine gender')
        return f


class HomeAddress(CrewIterFault):
    """Residential address."""

    remedy = ("Update table 'crew_address' temporarily. Notify HR department - this"
        " table is mirrored from the HR system.")

    def test(self, c, l=None):
        f = []
        if not c.res_country:
            f.append('no country of residence')
        if not c.res_street and not c.res_city and not c.res_postal_code:
            f.append('no residential address')
        return f


class FaultExtractor:
    def __init__(self):
        self.tests = [
            NoCrewPassport(),
            BirthData(),
            Gender(),
            DHSCategory(),
            JP_US(),
            CN_US(),
            BlockedNationality(),
            NoNationality(),
            BadCountryInDocuments(),
            BadCountryBirthRes(),
            HomeAddress(),
        ]
        self.counter = 0
        self.remedies = {}
        
    def test(self, crew, leg):
        """Run available tests."""
        f = []
        for tc in self.tests:
            faults = tc.test(crew, leg)
            if faults:
                if tc.remedy in self.remedies:
                    fcode = self.remedies[tc.remedy]
                else:
                    self.counter += 1
                    fcode = self.counter
                    self.remedies[tc.remedy] = fcode
                f.extend([self.get_fcode(fcode, x) for x in faults])
        return f

    def get_code(self, num, text):
        return "(%s) %s" % (num, text)

    def get_fcode(self, num, text):
        return self.get_code(num, text)

    def get_rcode(self, num, text):
        return self.get_code(num, text)

    def get_remedies(self):
        L = [(c, r) for (r, c) in self.remedies.iteritems()]
        L.sort()
        return [self.get_rcode(c, r) for (c, r) in L]


# CrewListError =========================================================={{{1
class CrewListError(TypeError):
    """To signal that function was called with to few arguments."""
    msg = ''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)


# Mappings Rave/Python ==================================================={{{1

# CrewInfoBase -----------------------------------------------------------{{{2
class CrewInfoBase:
    """Name, identity, birth."""
    def __init__(self, date='report_crewlists.%leg_start_lt%'):
        #print "init MCLMCL CrewInfoBase"
        self.fields = {
            'sn': 'report_crewlists.%%crew_passport_sn%%(%s)' % (date,),
            'gn': 'report_crewlists.%%crew_passport_gn%%(%s)' % (date,),
            'gender': 'report_crewlists.%crew_gender%',
            'birth_country': 'report_crewlists.%crew_birth_country%',
            'birthday': 'report_crewlists.%crew_birthday%',
            'birth_place': 'report_crewlists.%crew_birth_place%',
            'birth_state': 'report_crewlists.%crew_birth_state%',
            'res_postal_code': 'report_crewlists.%%crew_res_postal_code%%(%s)' % (date,),
            'res_city': 'report_crewlists.%%crew_res_city%%(%s)' % (date,),
            'res_state': 'report_crewlists.%%crew_res_state%%(%s)' % (date,),
            'res_street': 'report_crewlists.%%crew_res_street%%(%s)' % (date,),
            'res_country': 'report_crewlists.%%crew_res_country%%(%s)' % (date,),
            'position': 'report_crewlists.%%crew_title_rank%%(%s)' % (date,),
            'is_pilot': 'report_crewlists.%crew_is_pilot%',
            'phone_primary': 'report_crewlists.%com_primary_phone%',
            'license':  'report_crewlists.%%crew_license_no%%(%s)' % (date,),
            'license_issuer': 'report_crewlists.%%crew_license_issuer%%(%s)' % (date,),
            'license_validto': 'report_crewlists.%%crew_license_validto%%(%s)' % (date,),

        }


# CrewInfo ---------------------------------------------------------------{{{2
class CrewInfo(CrewInfoBase):
    """Will be evaluated on levels.leg"""
    def __init__(self, *a, **k):
        CrewInfoBase.__init__(self, *a, **k)
        self.fields.update({
            'for_stays_of': 'report_crewlists.%for_stays_of%(report_crewlists.%leg_end_country%)',
            'dhs_category': 'report_crewlists.%dhs_category%',
        })

class CrewInfoNop(CrewInfoBase):
    def __init__(self, *a, **k):
        CrewInfoBase.__init__(self, *a, **k)
        self.fields.update({
            'crew_id'               : 'report_crewlists.%nop_crew_id%',
            'sn'                    : 'report_crewlists.%nop_crew_sn%',
            'gn'                    : 'report_crewlists.%nop_crew_gn%',
            'gender'                : 'report_crewlists.%nop_crew_gender%',
            'birth_country'         : 'report_crewlists.%nop_crew_birth_country%',
            'birthday'              : 'report_crewlists.%nop_crew_birthday%',
            'birth_place'           : 'report_crewlists.%nop_crew_birth_place%',
            'birth_state'           : 'report_crewlists.%nop_crew_birth_state%',
            'nationality'           : 'report_crewlists.%nop_crew_nationality%',
            'nationality_prefer_US' : False,
            'res_postal_code'       : 'report_crewlists.%nop_crew_res_postal_code%',
            'res_city'              : 'report_crewlists.%nop_crew_res_city%',
            'res_state'             : 'report_crewlists.%nop_crew_res_street%',
            'res_street'            : 'report_crewlists.%nop_crew_res_street%',
            'res_country'           : 'report_crewlists.%nop_crew_res_country%',
            'phone'                 : 'report_crewlists.%phone%',
            'email'                 : 'report_crewlists.%email%',
            'position'              : 'report_crewlists.%nop_crew_position%',
            'is_pilot'              : False,
            'dhs_category'          : 'report_crewlists.%nop_crew_dhs_category%',
            'passport'              : 'report_crewlists.%nop_crew_passport%',
            'passport_issuer'       : 'report_crewlists.%nop_crew_passport_issuer%',
            'passport_validto'      : 'report_crewlists.%nop_crew_passport_validto%',
            'visa_type'             : 'report_crewlists.%nop_crew_visa_type%',
            'visa'                  : 'report_crewlists.%nop_crew_visa_number%',
            'visa_issuer'           : 'report_crewlists.%nop_crew_visa_country%',
            'visa_validto'          : 'report_crewlists.%nop_crew_visa_validto%',
        })
    

    

# CrewInfoMCL ------------------------------------------------------------{{{2
class CrewInfoMCL(CrewInfoBase):
    """Will be evaluated on levels.chain"""
    def __init__(self, *a, **k):
        CrewInfoBase.__init__(self, *a, **k)
        self.fields.update({
            'id': 'report_crewlists.%crew_id%',
            'dhs_category': 'report_crewlists.%dhs_category_mcl%',
        })


# RaveIterator classes ==================================================={{{1

# CrewIter ---------------------------------------------------------------{{{2
class CrewIter(RaveIterator):
    """Iterate over leg_set (for a flight). Fill with crew info."""
    def __init__(self):
        iterator = RaveIterator.iter('iterators.leg_set',
                where='fundamental.%is_roster%',
                sort_by='report_crewlists.%sort_key%')
        RaveIterator.__init__(self, iterator, CrewInfo())

# CrewIter ---------------------------------------------------------------{{{2
class CrewIterNop(RaveIterator):
    """Iterate over leg_set (for a flight). Fill with crew info."""
    def __init__(self):
        iterator = RaveIterator.times('report_crewlists.%num_assigned_nop_crew%')
        fields = {
            'id'                    : 'report_crewlists.%_assigned_nop_crew%(fundamental.%py_index%)',
            'crew_id'               : 'report_crewlists.%nop_crew_id%(fundamental.%py_index%)',
            'sn'                    : 'report_crewlists.%nop_crew_sn%(fundamental.%py_index%)',
            'gn'                    : 'report_crewlists.%nop_crew_gn%(fundamental.%py_index%)',
            'gender'                : 'report_crewlists.%nop_crew_gender%(fundamental.%py_index%)',
            'birth_country'         : 'report_crewlists.%nop_crew_birth_country%(fundamental.%py_index%)',
            'birthday'              : 'report_crewlists.%nop_crew_birthday%(fundamental.%py_index%)',
            'birth_place'           : 'report_crewlists.%nop_crew_birth_place%(fundamental.%py_index%)',
            'birth_state'           : 'report_crewlists.%nop_crew_birth_state%(fundamental.%py_index%)',
            'nationality'           : 'report_crewlists.%nop_crew_nationality%(fundamental.%py_index%)',
            'nationality_prefer_US' : False,
            'res_postal_code'       : 'report_crewlists.%nop_crew_res_postal_code%(fundamental.%py_index%)',
            'res_city'              : 'report_crewlists.%nop_crew_res_city%(fundamental.%py_index%)',
            'res_state'             : 'report_crewlists.%nop_crew_res_street%(fundamental.%py_index%)',
            'res_street'            : 'report_crewlists.%nop_crew_res_street%(fundamental.%py_index%)',
            'res_country'           : 'report_crewlists.%nop_crew_res_country%(fundamental.%py_index%)',
            'position'              : 'report_crewlists.%nop_crew_position%(fundamental.%py_index%)',
            'is_pilot'              : False,
            'dhs_category'          : 'report_crewlists.%nop_crew_dhs_category%(fundamental.%py_index%)',
            'passport'              : 'report_crewlists.%nop_crew_passport%(fundamental.%py_index%)',
            'passport_issuer'       : 'report_crewlists.%nop_crew_passport_issuer%(fundamental.%py_index%)',
            'passport_validto'      : 'report_crewlists.%nop_crew_passport_validto%(fundamental.%py_index%)',
            'visa_type'             : 'report_crewlists.%nop_crew_visa_type%(fundamental.%py_index%)',
            'visa'                  : 'report_crewlists.%nop_crew_visa_number%(fundamental.%py_index%)',
            'visa_issuer'           : 'report_crewlists.%nop_crew_visa_country%(fundamental.%py_index%)',
            'visa_validto'          : 'report_crewlists.%nop_crew_visa_validto%(fundamental.%py_index%)',
        }
        RaveIterator.__init__(self, iterator, fields)

        #RaveIterator.__init__(self, iterator, CrewInfoNop())

# CrewIterMCL ------------------------------------------------------------{{{2
class CrewIterMCL(RaveIterator):
    """Iterate over roster_set (for complete MCL). Fill with crew info."""
    def __init__(self, date, country):
        iterator = RaveIterator.iter('iterators.roster_set',
            where='crew.%%is_valid_for_crew_manifest%%("%s", %s)' % (country, date)
        )
        RaveIterator.__init__(self, iterator, CrewInfoMCL(date))


# CountryIter -------------------------------------------------------------{{{2
# This has replaced DocIter, to let rave evaluate what is current documents instead.
# Rave will handle bad quality of data, duplicates, etc, and be specific for different countries
class CountryIter(RaveIterator):
    """Get values for crew and country."""
    def __init__(self, date='report_crewlists.%cntry_lt%'):
        """MCL: the date will be end of search period."""
        iterator = RaveIterator.times('report_crewlists.%cntry_count_at%')
        fields = {
            'cntry_code':             'report_crewlists.%cntry_code%',
            'cntry_nationality':      'report_crewlists.%%cntry_nationality%%(%s)' % (date,),
            'cntry_passport_no':      'report_crewlists.%%cntry_passport_no%%(%s)' % (date,),
            'cntry_passport_issuer':  'report_crewlists.%%cntry_passport_issuer%%(%s)' % (date,),
            'cntry_passport_validto': 'report_crewlists.%%cntry_passport_validto%%(%s)' % (date,), 
            'cntry_visa_no':          'report_crewlists.%%cntry_visa_no%%(%s)' % (date,),
            'cntry_visa_issuer':      'report_crewlists.%%cntry_visa_issuer%%(%s)' % (date,),
            'cntry_visa_validto':     'report_crewlists.%%cntry_visa_validto%%(%s)' % (date,),
        }
        RaveIterator.__init__(self, iterator, fields)



# FlightIter -------------------------------------------------------------{{{2
class FlightIter(RaveIterator):
    """Iterate over flight_leg_set to get info about the specific flight."""
    def __init__(self, filter):
        iterator = RaveIterator.iter('iterators.flight_leg_set', where=filter.asTuple())
        fields = {
            'fd'        : 'report_crewlists.%leg_flight_descriptor%', 
            'udor'      : 'report_crewlists.%leg_udor%',
            'adep'      : 'report_crewlists.%leg_adep%',
            'ades'      : 'report_crewlists.%leg_ades%',
            'ac_reg': 'report_crewlists.%leg_ac_reg%',
            'ac_type': 'report_crewlists.%leg_ac_type%', # Used by Manifest CN
            'fd_number': 'report_crewlists.%leg_fd_number%',
            'fd_carrier': 'report_crewlists.%leg_fd_carrier%',
            'sta': 'report_crewlists.%leg_sta_lt%',
            'std': 'report_crewlists.%leg_std_lt%',
            'std_utc': 'report_crewlists.%leg_std_utc%',
            'end_country': 'report_crewlists.%leg_end_country%',
            'start_country': 'report_crewlists.%leg_start_country%',
            'out_bound': 'report_crewlists.%out_bound%',
            'ac_owner': 'report_crewlists.%leg_aircraft_owner%',
        }
        RaveIterator.__init__(self, iterator, fields)


# functions =============================================================={{{1

# crewlist ---------------------------------------------------------------{{{2
def crewlist(fd=None, udor=None, adep=None, country=None, with_nop=False):
    """Return list for Crew Manifest."""
    #print "called crewlist with",fd, udor,adep, country, with_nop
    if fd is None:
        raise CrewListError("crewlist(): Argument 'fd' is mandatory.")
    if udor is None:
        raise CrewListError("crewlist(): Argument 'udor' is mandatory.")
    try:
        ff = FlightFilter.fromComponents(fd, udor, adep, includeSuffix=True)
    except ValueError:
        raise CrewListError("crewlist(): Cannot parse flight ID '%s'." % (fd,))
    except:
        raise CrewListError("crewlist(): Date of origin '%s' is not usable." % (udor,))

    fi = FlightIter(ff)
    ci = CrewIter()
    yi = CountryIter()
    ni = CrewIterNop()
    nop_fi = FlightIter(ff)
    nop_ci = CrewIter()
    nop_yi = CountryIter()

    if with_nop:
        ci.link(cntrys=yi)
        fi.link(crew=ci)
        fi.link(nop=ni)
        legs = fi.eval(ff.context(includeSuffix=True))
        for leg in legs:
            leg.__dict__ = _unnullify(leg.__dict__)
            for crew in leg.chain('crew'):
                # Homebound flt, use dep country
                _country = country if country else (leg.end_country if leg.out_bound or leg.end_country=="US" else leg.start_country)
                _modify_object(crew, _country)
                crew.__dict__ = _unnullify(crew.__dict__)
            for nop in leg.chain('nop'):
                nop.__dict__ = _unnullify(nop.__dict__)
    else:
        nop_ci.link(cntrys=nop_yi)

        nop_fi.link(nop=ni)
        nop_legs = nop_fi.eval(ff.context(includeSuffix=True))

        ci.link(cntrys=yi)
        fi.link(crew=ci)
        legs = fi.eval(ff.context(includeSuffix=True))
        for leg in legs:
            leg.__dict__ = _unnullify(leg.__dict__)
            for crew in leg.chain('crew'):
                # Homebound flt, use dep country
                _country = country if country else (leg.end_country if leg.out_bound or leg.end_country=="US" else leg.start_country)
                _modify_object(crew, _country)
                crew.__dict__ = _unnullify(crew.__dict__)
            for nop_leg in nop_legs:
                    for nop in nop_leg.chain('nop'):
                        nop.__dict__ = _unnullify(nop.__dict__)
                        leg.chain('crew').append(nop)
    return legs


# mcl --------------------------------------------------------------------{{{2
def mcl(date=None, country='US'):
    """Return list for Master Crew List. 'date' is an AbsTime."""
    if date is None:
        date = 'fundamental.%now%'
    else:
        date = AbsTime(date)
    ci = CrewIterMCL(date, country)
    yi = CountryIter(date)
    ci.link(cntrys=yi)

    bc = BasicContext()
    rosters = ci.eval(bc.getGenericContext())
    for crew in rosters:
        _modify_object(crew, country)
        crew.__dict__ = _unnullify(crew.__dict__)
    return rosters


# private functions ======================================================{{{1

def _modify_object(c, country):
    """Modify the iteration object to flatten out the structure so it can be 
    used by the classes in crew_manifest."""
    #print "modify object for ",country
    c.nationality = None
    c.passport = None
    c.passport_issuer = None
    c.passport_validto = None
    c.visa = None
    c.visa_tupe = None
    c.visa_issuer = None
    c.visa_validto = None

    lookup = "**" # fallback, if country is not specifed from rave, meaning visa not required for apis
    for cntry in c:
        if cntry.cntry_code == country:
            lookup = country # the country exist as special data
    for cntry in c:
        if cntry.cntry_code == lookup:
             c.nationality = cntry.cntry_nationality
             c.passport = cntry.cntry_passport_no
             c.passport_issuer = cntry.cntry_passport_issuer
             c.passport_validto = cntry.cntry_passport_validto
             c.visa = cntry.cntry_visa_no
             c.visa_issuer = cntry.cntry_visa_issuer
             c.visa_validto = cntry.cntry_visa_validto


# _unnullify -------------------------------------------------------------{{{2
def _unnullify(map):
    """Change all occurences of None to empty string, to make it easier for the
    print out stage."""
    for key in map:
        if map[key] is None:
            map[key] = ""
    return map


# bit --------------------------------------------------------------------{{{2
def bit(iter, mcl=False):
    """For basic tests."""
    def print_crew():
        print " - rank            :", crew.position
        print "   sn              :", crew.sn
        print "   gn              :", crew.gn
        print "   gender          :", crew.gender
        print "   birthday        :", crew.birthday
        print "   country of birth:", crew.birth_country
        print "   state of birth  :", crew.birth_state
        print "   place of birth  :", crew.birth_place
        print "   nationality     :", crew.nationality
        print "   street          :", crew.res_street
        print "   city            :", crew.res_city
        print "   state           :", crew.res_state
        print "   postal code     :", crew.res_postal_code
        print "   country         :", crew.res_country
        print "   DHS category    :", crew.dhs_category
        print "   passport        :", crew.passport
        print "      issuer       :", crew.passport_issuer
        print "      validto      :", crew.passport_validto
        print "   visa            :", crew.visa
        print "      issuer       :", crew.visa_issuer
        print "      validto      :", crew.visa_validto
        print "   license         :", crew.license
        print "      issuer       :", crew.license_issuer
        print "      validto      :", crew.license_validto
    if mcl:
        for crew in iter:
            print_crew()
    else:
        for leg in iter:
            print "---"
            print "fd          :", leg.fd
            print "udor        :", leg.udor
            print "carrier     :", leg.fd_carrier
            print "number      :", leg.fd_number
            print "std         :", leg.std
            print "adep        :", leg.adep
            print "ades        :", leg.ades
            print "sta         :", leg.sta
            print "from country:", leg.start_country
            print "to country  :", leg.end_country
            print "A/C reg     :", leg.ac_reg
            print "A/C type    :", leg.ac_type
            print "A/C owner   :", leg.ac_owner
            print "crew:"
            for crew in leg:
                print_crew()


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    print "main"
    bit(crewlist("SK939", "20170204"))
    bit(mcl(AbsTime("20170204")), True)
    #bit(mcl(AbsTime("20070710"), RelTime(10 * 24 * 60), 'US'), True)
    #x = complete_mcl('fundamental.%now%')
    #bit(x, True)
    #print "Nr of long haul crew", len(x)

#def main():
#    print "mainf"
#    bit(crewlist("SK939", "20170204"))
#    bit(mcl(AbsTime("20170204")), True)


#main()

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
