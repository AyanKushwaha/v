"""
     `Export to CrewAlert`
        f.exec PythonEvalExpr("__import__('carmusr.fatigue.crewalert').fatigue.crewalert.export()")

"""
import json
import urllib2
import Cui
from datetime import datetime
import os
import getpass
import carmensystems.rave.api as rave
import carmusr.concert.log as log
logger = log.get_logger()


def populate_frm_data(chain_bag):
    """function to extract all data from the bag"""

    metadata = {}
    metadata["application"] = chain_bag.report_crewalert.application()
    metadata["version"] = chain_bag.report_crewalert.version()
    metadata["shareStart"] = chain_bag.report_crewalert.share_start()
    metadata["shareEnd"] = chain_bag.report_crewalert.share_end()
    metadata["scenario"] = chain_bag.report_crewalert.id()
    metadata["scenarioDescription"] = "Exported by %s at %s" % (get_current_user(), get_now())

    settings = {}
    settings["diurnalType"] = chain_bag.report_crewalert.setting_diurnal_type()
    settings["habitualSleepLength"] = chain_bag.report_crewalert.setting_habitual_sleep_length()
    settings["homeBaseTimeZone"] = chain_bag.report_crewalert.setting_homebase_time_zone()

    data = []
    for leg in chain_bag.iterators.leg_set(): # where="report_crewalert.%export_leg%"
        d = {}
        d["flightNumber"] = leg.report_crewalert.flight_no()
        d["depUTC"] = leg.report_crewalert.dep_utc()
        d["arrUTC"] = leg.report_crewalert.arr_utc()
        d["depStn"] = leg.report_crewalert.dep_stn()
        d["arrStn"] = leg.report_crewalert.arr_stn()
        d["type"] = leg.report_crewalert.type()
        d["briefing"] = leg.report_crewalert.briefing()
        d["debriefing"] = leg.report_crewalert.debriefing()
        d["awakeBefore"] = leg.report_crewalert.wake_before()
        d["awakeAfter"] = leg.report_crewalert.wake_after()
        d["inflightSleep"] = leg.report_crewalert.inflight_sleep()
        d["endsAtHomeBase"] = leg.report_crewalert.ends_at_homebase()
        d["comment"] = leg.report_crewalert.comment()
        data.append(d)

    return {'metadata': metadata, 'data': data, 'settings': settings}
try:
    from nth.studio.message import show_text

except ImportError:
    from tempfile import mktmp
    import Csl
    csl = Csl.Csl()

    def _show_file(title, filepath):
        csl.evalExp('csl_show_file("%s", "%s")' % (title, filepath))

    def show_text(title, text):
        fn = mktmp()
        f = open(fn, 'w')
        f.write(text)
        f.close()
        _show_file(title, fn)
        os.unlink(fn)


def get_current_user():
    return getpass.getuser()


def get_now():
    return datetime.today().strftime('%Y-%m-%d_%H:%M.%S')


def write_file(suffix, content):
    directory = os.path.expandvars("$CARMTMP/CREWALERT/")
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = "%s/%s_%s_%s" % (directory, get_current_user(), get_now(), suffix)
    with open(filename, 'w') as fil:
        fil.write(content)

    return filename


def write_urls_to_file(urls):
    content = "<html><body><h1>CrewAlert scenario links</h1>\n"
    for key, url in urls.iteritems():
        content += "<p><a href='%s'>%s</a></p>\n" % (url, key)

    content += "</body></html>"
    return write_file(suffix="crewalert_export.html", content=content)


def show_urls(urls):
    text_to_show = ""
    for url in urls.values():
        text_to_show += url + "\n\n"

    show_text("CrewAlert Export", text_to_show)


def show_urls_in_firefox(urls):
    # This is a workaround for STUDIO-16722 (fixed in R21 SP10),
    # which causes the csl dialogue to be invisible on certain
    # text lengths.
    html_file = write_urls_to_file(urls)
    # ABS indicates absolute path
    Cui.CuiStartExternalBrowser(html_file, "ABS")


def construct_urls(bag_desc, debug=False):
    chains = rave.selected(rave.level("levels.chain")).bag().chain_set()
    jsons = dict()
    for chain in chains:
        crewalert_json_dict = populate_frm_data(chain)
        if debug:
            logger.info(crewalert_json_dict)
        url = 'crewalert://scheduleload/' + urllib2.quote(json.dumps(crewalert_json_dict))
        key = crewalert_json_dict['metadata']['scenario']
        jsons[key] = url

    return jsons


def export(bag_description, target="show_in_ff", debug=False):
    """ This function makes sense to wrap in your customization layer. """
    urls = construct_urls(bag_description, debug)

    if target == "show":
        show_urls(urls)
    if target == "show_in_ff":
        show_urls_in_firefox(urls)
    elif target == "file":
        write_urls_to_file(urls)
