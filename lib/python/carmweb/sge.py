'''
Interface to the Sun Grid Engine

@author: rickard.petzall
'''

import subprocess
from xml.dom.minidom import parseString
    
def _safe_run(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout,stderr = p.communicate("")
    if p.returncode <> 0:
        raise Exception, "Command '%s' failed: %s" % (cmd, stderr)
    return stdout

class Elem(object):
    def __init__(self, nd):
        self.name = nd.nodeName
        self.attributes = {}
        for at in nd.attributes.keys():
            self.attributes[at] = nd.attributes[at].value
        self.text = ""
        self.children = {}
        for ch in nd.childNodes:
            if ch.nodeType == 3:
                self.text += ch.nodeValue
            elif ch.nodeType == 1:
                e = Elem(ch)
                if not hasattr(self, ch.nodeName):
                    setattr(self, ch.nodeName, e)
                oa = []
                if hasattr(self, ch.nodeName+"s"):
                    oa = getattr(self, ch.nodeName+"s")
                oa.append(e)
                setattr(self, ch.nodeName+"s", oa)
                self.children[ch.nodeName] = oa
        self.text = self.text.strip()
    def __str__(self):
        return str(self.text)
    def __repr__(self):
        return self.xml()
    def xml(self, i=0):
        ids = ' ' * i
        attst = ''
        if len(self.attributes) > 0:
            for at in self.attributes:
                attst += ' %s="%s"' % (at, self.attributes[at])
        l = [ids + "<%s%s>" % (self.name, attst)]
        hc = ''
        if self.text:
            l.append(self.text)
        for chn in self.children:
            hc = '\n'
            l += [x.xml(i+1) for x in self.children[chn]]
        l.append((hc and ids or '') + "</%s>" % self.name)
        return hc.join(l)
    
class Job(object):
    def __init__(self, djob_info):
        self.job_number = str(djob_info.element.JB_job_number)
        self.submission_time = int(str(djob_info.element.JB_submission_time))
        self.uid = int(str(djob_info.element.JB_uid))
        self.gid = int(str(djob_info.element.JB_gid))
        self.owner = str(djob_info.element.JB_owner)
        self.name = str(djob_info.element.JB_job_name)
        self.script = str(djob_info.element.JB_script_file)
        try:
            self.args = [str(arg.ST_name) for arg in djob_info.element.JB_job_args.elements]
        except:
            self.args = []
        self.res_cpu = -1
        self.res_mem = -1
        try:
            for scaled in djob_info.element.JB_ja_tasks.ulong_sublist.JAT_scaled_usage_list.scaleds:
                if str(scaled.UA_name) == 'cpu':
                    self.res_cpu = float(str(scaled.UA_value))
                elif str(scaled.UA_name) == 'vmem':
                    self.res_mem = float(str(scaled.UA_value))
        except:
            pass
        self.context = {}
        try:
            for ctx in djob_info.element.JB_context.context_lists:
                self.context[str(ctx.VA_variable)] = str(ctx.VA_value)
        except:
            pass
        
    def __str__(self):
        return "Job #%s" % self.job_number
    def __repr__(self):
        l = []
        for m in dir(self):
            if m[0] == '_': continue
            v = getattr(self, m)
            if isinstance(v, str) or isinstance(v, int) or isinstance(v, long) or isinstance(v, float):
                l.append("%s=%s" % (m,v))
            elif isinstance(v, dict) or isinstance(v, list):
                l.append("%s=%s" % (m,repr(v)))
        return "Job[%s]" % ', '.join(l)
        
def _xml_run(cmd):
    doc = parseString(_safe_run(cmd))
    e = Elem(doc.documentElement)
    doc.unlink()
    return e

def get_job_ids(name_prefix=''):
    jobInfo = _xml_run("qstat -xml")
    l = []
    try:
        job_lists = jobInfo.queue_info.job_lists
    except:
        job_lists = [] # qstat -xml doesn't even return the list object if it's empty
    for job_list in job_lists:
        if not name_prefix or str(job_list.JB_name)[:len(name_prefix)] == name_prefix:
            l.append(str(job_list.JB_job_number))

    return l

def get_job(id):
    try:
        return Job(_xml_run("qstat -xml -j %s" % id).djob_info)
    except:
        # qstat has the decency to return non-wellformed xml if the job is not found
        return None

def setSGEcontext(jobId, var, val):
    if not val:
        cmd = 'qalter %s -dc %s > /dev/null || true' % (jobId,var)
    else:
        cmd = 'qalter %s -ac %s=%s > /dev/null || true' % (jobId,var,val)
    _safe_run(cmd)

def kill_job(id):
    cmd = 'qdel %s' % id
    s = _safe_run(cmd)
    if "is already in deletion" in s: raise Exception,s

def getSGEcontext(jobId, var, default=''):
    j = get_job(jobId)
    if var in j.context:
        return str(j.context[var])
    return default

def list_jobs(name_prefix=''):
    return [get_job(x) for x in get_job_ids(name_prefix)]

if __name__ == '__main__':
    l = list_jobs('TwS_')
    if l: print '\n'.join([repr(x) for x in l])