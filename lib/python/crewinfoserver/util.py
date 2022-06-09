from __future__ import print_function
from datetime import datetime
import sys
import os
import json


# # # # #


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in xrange(0, len(lst), n):
        yield lst[i:i + n]


# # # # #

def split_trip_id(trip_id, as_abstime=False):
    parts = trip_id.split("+")
    ttid = "+".join(parts[2:])
    if as_abstime:
        return isodate_to_abstime(parts[0]), isodate_to_abstime(parts[1]), str(ttid)
    return [parts[0], parts[1]], str(ttid)


# # # # #

def timed(f):
    """returns a tuplet consisting of result of running 'f' and time elapsed printable in form: hh:mm:ss.mmmmmm"""
    start_dt = datetime.now()
    res = f()
    elapsed = datetime.now() - start_dt
    return res, elapsed


# # # # #

def datetime_to_abstimestr(date_str):
    sep = ':'
    spl_date = sep.join(date_str.split(sep, 2)[:2])
    sep2 = 'T'
    rest = spl_date.split(sep2, 1)
    rest[0] = str(isodate_to_absdate(rest[0]))
    rest[1] = str(rest[1])
    rest = ' '.join(rest)
    return rest


def datetime_to_absdatestr(date_str, form='abs'):
    sep = 'T'
    rest = date_str.split(sep, 1)
    if form == 'abs':
        return str(isodate_to_absdate(rest[0]))
    elif form == 'iso':
        return rest[0]
    else:
        print('ERROR! Wrong format type')


def isodate_to_absdatestr(isodate_str):
    return "".join(isodate_str.split("-"))


def isodate_to_absdate(isodate_str):
    from AbsDate import AbsDate
    return AbsDate(isodate_to_absdatestr(str(isodate_str)))


def isodate_to_abstime(isodate_str):
    from AbsTime import AbsTime
    return AbsTime(isodate_to_absdatestr(str(isodate_str)))


def now_as_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

# # # # #

def print_trace():
    import traceback
    traceback.print_exc()


def format_trace():
    import traceback
    return traceback.format_exc()


def eprint(*args, **kwargs):
    """Prints to stderr."""
    # https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
    print(*args, file=sys.stderr, **kwargs)


def show_message(message, title=""):
    """A basic modal dialog for presenting a (multiline) string in studio.
    :param message: String. A possibly multiline string to be shown as a mesage in a popup-window.
    :param title: String. An optional title for the window.
    :return:
    """
    import tempfile
    import carmstd.cfhExtensions as ext

    f_name = tempfile.mktemp()
    f = open(f_name, "w")
    f.write(message)
    f.close()
    ext.showFile(f.name, title)


# # # # #

def ensure_path(dir_path):
    """Ensures that directories for path exist.
    :return: None """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def ensured_path(dir_path):
    """
    :return: The path as string.
    """
    ensure_path(dir_path)
    return dir_path


def touch_file(file_path):
    """Touches (creates if needed) the file, ensuring directories exist along the way."""
    basedir = os.path.dirname(file_path)
    ensure_path(basedir)
    with open(file_path, "a"):
        os.utime(file_path, None)


def load_json(fp, verbose=True):
    if not os.path.isfile(fp):
        if verbose:
            print("WARNING: File doesn't exists  (%s)" % fp)
        return {}
    try:
        return json.load(file(fp))
    except ValueError, e:
        if verbose:
            print("WARNING: %s  (%s)" % (e, fp))
        return {}


def dump_json(fp, data):
    touch_file(fp)
    json.dump(data, open(fp, "w"), indent=2)


USER = os.getenv("USER")
CARMTMP = os.getenv("CARMTMP")
HOSTNAME = os.getenv("HOSTNAME")
CARMUSR = os.getenv("CARMUSR")


def log_command(cmd, output):
    """Writes data to a logfile, same as sysomnd-driven commands."""
    date_str = datetime.now().strftime("%Y%m%d.%H%M.%S")
    logdir_path = "%s/logfiles/triptrade/%s" % (CARMTMP, cmd)
    ensure_path(logdir_path)
    logfile_path = "%s/%s.%s.%s.%s" % (logdir_path, cmd, USER, date_str, HOSTNAME)
    with open(logfile_path, "w") as f:
        f.write(output)
        f.write("\n")


# # # # #

def log_to_influxdb(server, data, timeout=10):
    import pycurl
    try:
        c = pycurl.Curl()

        # Example:
        #  c.setopt(pycurl.URL,'http://h1cms48a:8086/write?db=teststat')
        #  data = 'cms_kpis,host=h1cms50a total_save_time=10.33,total_save_cpu=10.33'

        ### Simple ping
        #  c.setopt(pycurl.URL,'http://devgw01:25991/ping')
        #  data = ''
        
        c.setopt(pycurl.URL, server)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        c.setopt(pycurl.VERBOSE, 1)
        c.setopt(pycurl.TIMEOUT, timeout)
        c.perform()
        print ("Sent this data to influxDB: " + data)
        print (c.getinfo(pycurl.RESPONSE_CODE))
        c.close()
    except Exception as e:
        eprint(e)


# # # # #
