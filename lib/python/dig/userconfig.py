import os
import sys
import re
from time import time
import utils.config

_t = 0
_config = None
_patterns = None
def _getConfig():
    import carmensystems.dig.framework.dave as D
    conn = D.DaveConnector(os.environ['DB_URL'], os.environ['DB_SCHEMA'])
    c = {}
    patterns = {}
    #for k in conn.runSearch(D.DaveSearch("dig_reporttype_set","")):
    #    c[(k['maintype'],k['subtype'])] = {}
    #for k in conn.runSearch(D.DaveSearch("dig_reportrecipient_set","")):
    #    a = c.get((k['reporttype_maintype'],k['reporttype_subtype']), {})
    #    a[k['rcpttype']] = {}
    for k in conn.runSearch(D.DaveSearch("dig_recipients","")):
        rep = (k['recipient_reporttype_maintype'],k['recipient_reporttype_subtype'],k['recipient_rcpttype'])
        a = c.get(rep, None)
        if a is None:
            a = {}
            c[rep] = a
        b = a[k['protocol']] = []
        for kv in k['target'].split(";"):
            b.append({'target':kv, 'subject':k['subject']})
    
    for k in conn.runSearch(D.DaveSearch("dig_string_patterns","")):
        rep = (k['recipient_reporttype_maintype'],k['recipient_reporttype_subtype'],k['recipient_rcpttype'])
        a = patterns.get(rep, None)
        if a is None:
            a = []
            patterns[rep] = a
        pattern = k.get('pattern','')
        if not pattern: continue
        try:
            regex = re.compile(pattern)
            a.append(regex)
        except:
            print >>sys.stderr, "WARN: Bad regular expression in table dig_string_patterns: %s for %s" % (pattern, rep)
            print "Bad regular expression in table dig_string_patterns: %s for %s. Ignoring pattern" % (pattern, rep)
    return c, patterns

def _check():
    global _config, _patterns, _t
    if _config is None or time() - _t > 5*60:
        _t = time() 
        _config, _patterns = _getConfig()
        utils.config.get_default_service_config(True)

def lookup(mainreport, subreport='', rcpttype=''):
    def _expandvars(unexpanded):
        if unexpanded is None:
            return None
        config = utils.config.get_default_service_config()
        return str(config._expandvars(unexpanded))
    _check()
    global _config

    rv = []
    for (mt,st,rt),v in _config.items():
        if (mt == mainreport or mt == "*") and (st == subreport or st == "*") and (rt == rcpttype or rt == "*"):
            for p,vv in v.items():
                for tv in vv:
                    protocol = _expandvars(p)
                    target = _expandvars(tv['target'])
                    subject = _expandvars(tv['subject'])
                    rv.append({'protocol':protocol, 'target':target, 'subject':subject})
    return rv
        
def searchpatterns(string, mainreport, subreport=''):
    _check()
    global _patterns
    
    rcpts = set()
    
    for (mt,st,rt),patts in _patterns.items():
        if (mt == mainreport or mt == "*") and (st == subreport or st == "*"):
            for pattern in patts:
                if not pattern.search(string) is None:
                    rcpts.add(rt)
    return list(rcpts)
    
if __name__ == '__main__':
    try:
        print '-- lookup("BALANCING_REPORT","OVERTIME","SE"):'
        print lookup("BALANCING_REPORT","OVERTIME","SE")
        print '-- lookup("CREW_MEAL","CreateCari","*")'
        print lookup("CREW_MEAL","CreateCari","*")
    except ImportError:
        sys.exit(os.system("$CARMSYS/bin/carmpython '%s'" % __file__))
