

"""
Interactive routines for sending and checking Flight Crew Manifests (FCM) These
are normally sent (using PAXLST format) by batch routines. These manual
routines makes it possible to create FCM as a fallback solution.

See CR 436 and SASCMS-1454.
"""


import __main__
import os
import traceback
from tempfile import mkstemp

import Cfh
import Cui
import carmensystems.rave.api as rave
import carmusr.Attributes
import carmusr.paxlst.crew_manifest
import utils.mnu # Needed - don't ask me why [acosta:10/062@13:56] 
import utils.edifact
import utils.cfhtools as cfhtools
import utils.mnu as mnu
import report_sources.hidden.apis_info as apis_info
import report_sources.hidden.apis_log as apis_log
import report_sources.hidden.apis_flights as apis_flights

from carmstd import cfhExtensions
from AbsTime import AbsTime
from utils.rave import MiniEval, Entry
from utils.mailtools import send_mail
from dig.DigJobQueue import DigJobQueue


# globals ================================================================{{{1
channel = 'manifest_manual'
submitter = 'manifest_manual_jobs'

# Will be filled in by end user the first time 'leg_apis_text()' is called.
mail_address = None
valid_countries = None

def append_fo_to_RU(c):
    "to know if 'RU' is flyover og dest/dep country"
    return "RU_fo" if c == "RU" else c

def strip_fo_from_RU(c):
    "if 'RU_fo' then 'RU'"
    return "RU" if c == "RU_fo" else c

def strip_fo_from_RU_in_list(lst):
    return map(strip_fo_from_RU, lst)


# Forms for entering data ================================================{{{1

# FCMBox -----------------------------------------------------------------{{{2
class FCMBox(cfhtools.BasicBox):
    """Let user confirm creation of Crew Manifest."""
    def __init__(self, leg, country):
        cfhtools.BasicBox.__init__(self, "FCM for %s" % leg)
        self.leg = leg
        self.country = country
        self.l1 = self.c_label("xm_question.pm", dim=(2, 2), loc=(0, 0))
        self.l2 = self.c_label('Do you want to submit a Crew Manifest for %s?' % leg, loc=(0, 3))
        self.l3 = self.c_label('The manifest will be sent to %s authorities.' % country, loc=(1, 3))
        self.b_ok = self.Done(self)
        self.b_cancel = self.Cancel(self)
        self.build()


# MailAddressForm --------------------------------------------------------{{{2
class MailAddressForm(cfhtools.BasicBox):
    """Let user fill in an email address."""
    def __init__(self, title='Enter email address'):
        cfhtools.BasicBox.__init__(self, title)
        if mail_address is None:
            ma = ''
        else:
            ma = mail_address
        self.l1 = self.c_label('Mail address', loc=(0, 0))
        self.f_mail_address = self.c_string('', maxlength=50, loc=(0, 15))
        self.done = self.Done(self)
        self.cancel = self.Cancel(self)
        self.build()

    @property
    def mail_address(self):
        return self.f_mail_address.valof()


# StartEndBox ------------------------------------------------------------{{{2
class StartEndBox(cfhtools.BasicBox):
    """Input box where end user can enter start and end dates."""
    choices = ['country and time', 'time']
    def __init__(self, module):
        cfhtools.BasicBox.__init__(self, module.title)
        self.l_start = self.c_label("Start time", loc=(0, 0))
        self.dt_start = self.c_datetime(module.get_default_start(), loc=(0, 6))
        self.l_end = self.c_label("End time", loc=(1, 0))
        self.dt_end = self.c_datetime(module.get_default_end(), loc=(1, 6))
        self.l_choice = self.c_label("Sort by", loc=(2, 0))
        self.s_choice = self.c_string(self.choices[0], loc=(2, 6))
        self.s_choice.setMenu([''] + self.choices)
        self.s_choice.setStyle(Cfh.CfhSChoiceRadioCol)
        self.b_ok = self.Done(self)
        self.b_cancel = self.Cancel(self)
        self.build()

    @property
    def start_time(self):
        return AbsTime(self.dt_start.valof())

    @property
    def end_time(self):
        return AbsTime(self.dt_end.valof())

    @property
    def sort_by_country(self):
        return self.s_choice.valof() == self.choices[0]


# Dynamic menus and actions =============================================={{{1

menu_mode = 'IsAPIS'


# APISendMenu ------------------------------------------------------------{{{2
class APISSendMenu(mnu.Menu):
    """Depending on the number of countries applicable, have one entry per
    country."""
    def __init__(self, title, name='APIS_SUBMIT_MENU_X', mnemonic='_S'):
        mnu.Menu.__init__(self, name, title=title, mnemonic=mnemonic,
                menuMode=menu_mode)

    def __call__(self):
        """Called each time the menu is selected. Add one submenu entry for
        each country where APIS can be sent to."""
        leg = get_leg_info()
        countries = strip_fo_from_RU_in_list(get_recipient_countries(leg))
        if countries:
            for country in countries:
                button = mnu.Button(self.get_button_text(country),
                        action=self.Action(leg, country),
                        menuMode=menu_mode)
                button.attach(self.name)
        else:
            title = mnu.Title("N/A", menuMode=menu_mode)

    def get_button_text(self, country):
        return 'Submit to %s' % country

    class Action:
        """Action - Submit APIS to country."""
        def __init__(self, leg, country):
            self.leg = leg
            self.country = country

        def __call__(self):
            f = FCMBox(self.leg, self.country)
            if f.run() == Cfh.CfhOk:
                djq = DigJobQueue(channel=channel, submitter=submitter,
                        reportName='report_sources.report_server.rs_crew_manifest')
                jobid = djq.submitJob(dict(fd=self.leg.fd, udor=self.leg.udor,
                    adep=self.leg.adep, country=self.country))
                cfhtools.InfoDialog('A job with job id %s has been submitted.' % jobid, 
                        'The job will create a FCM for %s authorities.' % self.country, 
                        title='Job Submitted').run()
            else:
                cfhtools.InfoDialog('The operation was aborted.',
                        title='Aborted').run()


# PDFReportMenu ----------------------------------------------------------{{{2
class PDFReportMenu(APISSendMenu):
    """Depending on the number of countries applicable, have one entry per
    country."""
    def __init__(self, title, name='PDF_REPORT_MENU_X', mnemonic='_R'):
        APISSendMenu.__init__(self, title, name=name, mnemonic=mnemonic)

    def get_button_text(self, country):
        return 'Show %s' % country

    class Action:
        """Action - Show crew manifest (PDF)."""
        def __init__(self, leg, country):
            self.country = country

        def __call__(self):
            if self.country == 'CN':
                import report_sources.hidden.CrewManifestCN as R
            elif self.country == 'JP':
                import report_sources.hidden.CrewManifestJP as R
            elif self.country == 'TH':
                import report_sources.hidden.CrewManifestTH as R
            elif self.country == 'AE':
                import report_sources.hidden.CrewManifestAE as R
            else:
                cfhtools.InfoDialog('Not available', 
                        'The report is not available for %s.' % self.country, 
                        title='Not available').run()
                return
            try:
                R.reportSelectedFlight()
            except Exception, e:
                cfhtools.InfoDialog('Could not display report', str(e),
                        title='Error').run()


# help functions ========================================================={{{1

# get_leg_info -----------------------------------------------------------{{{2
def get_leg_info():
    """Get some Rave values for current leg."""
    class FCMEntry(Entry):
        def __str__(self):
            return "%s/%s %s-%s" % (self.fd.strip(), self.udor.split()[2],
                    self.adep, self.ades)

    Cui.CuiCrgSetDefaultContext(Cui.gpc_info,
            Cui.CuiAreaIdConvert(Cui.gpc_info, Cui.CuiWhichArea), 'OBJECT')
    return MiniEval({
        'fd': 'report_crewlists.%leg_flight_descriptor%',
        'udor': 'report_crewlists.%leg_udor%',
        'adep': 'report_crewlists.%leg_adep%',
        'ades': 'report_crewlists.%leg_ades%',
        'start_country': 'report_crewlists.%leg_start_country%',
        'end_country': 'report_crewlists.%leg_end_country%',
        'is_apis': 'report_crewlists.%leg_is_apis%',
        'dk_nsch': 'report_crewlists.%leg_is_dk_nsch%',
        'no_nsch': 'report_crewlists.%leg_is_no_nsch%',
        'ie_neu': 'report_crewlists.%leg_is_ie_neu%',
        }, FCMEntry).eval(rave.selected(rave.Level.atom()))


# get_recipient_countries ------------------------------------------------{{{2
def get_recipient_countries(leg):
    """Return list of recipient countries, the list could contain anything from
    zero to several countries depending on flight route."""
    countries = []
    if leg.start_country in get_valid_countries(leg):
        countries.append(leg.start_country)
    if leg.end_country in get_valid_countries(leg):
        if leg.end_country not in countries:
            countries.append(leg.end_country)
    countries = countries + get_flyover_countries(leg)
    return countries


# get_start_end ----------------------------------------------------------{{{2
def get_start_end(module):
    """Ask end user for start time and end time."""
    box = StartEndBox(module)
    if box.run() == Cfh.CfhOk:
        return {'startdate': box.start_time, 'enddate': box.end_time,
                'sort_by_country': box.sort_by_country}
    return {}


# get_valid_countries ----------------------------------------------------{{{2
def get_valid_countries(leg):
    """Return list of valid countries."""
    global valid_countries
    if valid_countries is None:
        if leg.ie_neu:
            valid_countries = rave.set('leg.apis_countries_ie').members()
        elif leg.dk_nsch:
            valid_countries = rave.set('leg.apis_countries_dk').members()
        elif leg.no_nsch:
            valid_countries = rave.set('leg.apis_countries_no').members()
        else:
            valid_countries = rave.set('leg.apis_countries').members()
    return valid_countries

# get_flyover_countries --------------------------------------------------{{{2
def get_flyover_countries(leg):
    """Return list of flyover countries."""
    evals = {}
    for ctry in get_valid_countries(leg):
        evals[ctry] = 'leg.%leg_has_flyover%("' + ctry + '")'

    fo = MiniEval(evals).eval(rave.selected(rave.Level.atom()))

    flyover_countries = []
    for ctry in get_valid_countries(leg):
        if getattr(fo, ctry):
            flyover_countries.append(append_fo_to_RU(ctry))

    return flyover_countries


# actions ================================================================{{{1

# leg_apis_info ----------------------------------------------------------{{{2
def leg_apis_info():
    """Show APIS info for leg in readable format."""
    leg = get_leg_info()
    apis_info.run(fd=leg.fd, udor=leg.udor, adep=leg.adep)


# leg_apis_text ----------------------------------------------------------{{{2
def leg_apis_text():
    """Show APIS message, to be cut and pasted into a Telex."""
    global mail_address

    leg = get_leg_info()
    countries = get_recipient_countries(leg)
    if not countries:
        cfhtools.ErrorDialog('This leg does not require a Crew Manifest.').run()
        return

    utils.edifact.debug = False
    filename = None
    try:
        try:
            rlist = []
            for country in countries:
                sa = carmusr.paxlst.crew_manifest.SITAAddresses(strip_fo_from_RU(country))
                for message in carmusr.paxlst.crew_manifest.crewlist(fd=leg.fd,
                        udor=leg.udor, adep=leg.adep, country=country):
                    for recipient in sa.recipients:
                        rlist.append(sa.add_recipient(recipient, message))
            fd, filename = mkstemp(suffix='.tmp', prefix='paxlst_mmi',
                    dir=os.environ['CARMTMP'], text=True)
            tmpfile = os.fdopen(fd, 'w')
            print >>tmpfile, "\n\n===\n\n".join(rlist)
            tmpfile.close()
            subject = "APIS in text format for %s." % leg
            f = MailAddressForm()
            if f.run() == Cfh.CfhOk:
                if f.mail_address:
                    send_mail(filename, f.mail_address, subject=subject)
            cfhExtensions.showFile(filename, subject)
        finally:
            if filename is not None:
                try:
                    os.unlink(filename)
                except:
                    pass
    except:
        traceback.print_exc()
        cfhtools.ErrorDialog("Failed creating APIS message",
                "A data problem may have prevented this operation.",
                "Try running APIS Info Report to locate and correct the problem.").run()

    
# leg_clear_error --------------------------------------------------------{{{2
def leg_clear_error():
    carmusr.Attributes.RemoveLegAttrCurrent("FCMERROR")


# leg_submit_apis --------------------------------------------------------{{{2
def leg_submit_apis():
    """Present a form where the end user can confirm creation of Manual FCM. If
    ok, submit DIG job."""
    leg = get_leg_info()
    countries = strip_fo_from_RU_in_list(get_recipient_countries(leg))
    if not countries:
        cfhtools.ErrorDialog('This leg does not require a Crew Manifest.').run()
        return
    f = FCMBox(leg, countries)
    if f.run() == Cfh.CfhOk:
        djq = DigJobQueue(channel=channel, submitter=submitter,
                reportName='report_sources.report_server.rs_crew_manifest')
        if f.countries:
            for country in f.countries:
                jobid = djq.submitJob(dict(fd=leg.fd, udor=leg.udor, adep=leg.adep,
                    country=country))
                cfhtools.InfoDialog('A job with job id %s has been submitted.' % jobid, 
                        'The job will create a FCM for %s authorities.' % country, 
                        title='Job Submitted').run()
        else:
            cfhtools.WarningDialog('No job submitted.', 'No recipient was selected.',
                    title='Warning - no job submitted').run()
    else:
        cfhtools.InfoDialog('The operation was aborted.',
                title='Aborted').run()


# plan_apis_flights ------------------------------------------------------{{{2
def plan_apis_flights():
    """Let user pick a date range. Show all flights that require APIS for that
    period."""
    period = get_start_end(apis_flights)
    if period:
        apis_flights.run(**period)


# plan_apis_log ----------------------------------------------------------{{{2
def plan_apis_log():
    """Let user pick a date range. Show APIS transmission log for the
    period."""
    period = get_start_end(apis_log)
    if period:
        apis_log.run(**period)


# run ===================================================================={{{1
def run(action='leg_submit_apis'):
    """Main entry point for Studio's menu system."""
    if action == 'plan_apis_flights':
        plan_apis_flights()
    elif action == 'plan_apis_log':
        plan_apis_log()
    elif action == 'leg_submit_apis':
        leg_submit_apis()
    elif action == 'leg_apis_info':
        leg_apis_info()
    elif action == 'leg_apis_text':
        leg_apis_text()
    elif action == 'leg_clear_error':
        leg_clear_error()
    else:
        raise ValueError("Invalid value of parameter 'action'.")


# activate_menus ========================================================={{{1
def activate_menus(attach_to='APISLeg'):
    """Dynamic menu 'APIS', attached to 'Assignment Object'."""
    items = [
        PDFReportMenu('Reports'),
        APISSendMenu('Submit APIS'),
        mnu.Separator(),
        mnu.Button("APIS Info Report", action=leg_apis_info, mnemonic='_A',
            menuMode=menu_mode),
        mnu.Button("APIS as Text", action=leg_apis_text, mnemonic='_T',
            menuMode=menu_mode),
        mnu.Button('Clear FCM Error', action=leg_clear_error, mnemonic='_C',
            menuMode=menu_mode),
    ]
    for item in items:
        item.attach(attach_to)


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    # For basic tests.
    activate_menus()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
