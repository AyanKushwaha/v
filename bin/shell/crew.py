import sys, os
from carmensystems.dig.framework.dave import DaveSearch, DaveMultiSearch, createOp, DaveConnector, DaveStorer
from AbsTime import AbsTime

_dc = None
def _dbsearch(entity, expr=[], entity2=None, expr2=[], withDeleted=False):
	global _dc
	if not _dc: _dc = DaveConnector(os.environ['DB_URL'], os.environ['DB_SCHEMA'])
	if isinstance(expr, str):
		expr = [expr]
	if isinstance(expr2, str):
		expr = [expr2]
	if entity2:
		return dict(_dc.runSearch(DaveMultiSearch([DaveSearch(entity, expr, withDeleted), DaveSearch(entity2, expr2, withDeleted)])))
	else:
		return list(_dc.runSearch(DaveSearch(entity, expr, withDeleted)))
		
def _format(res):
	dr = {}
	for entry in res:
		vf = entry.get("validfrom", None)
		vt = entry.get("validto", None)
		for k in entry.keys():
			if k in ("validfrom", "validto", "revid"): continue
			if entry[k] and not k in dr: dr[k] = []
			if entry[k] or k in dr:
				dr[k].append((entry[k], vf, vt))
	maxlen = max(map(len, dr.keys()))
	def comparer(a,b):
		first = ("id",)
		if a in first and not b in first: return -1
		elif b in first and not a in first: return 1
		elif a < b: return -1
		elif b < a: return 1
		return 0
	def formatval(k,v):
		if k in ("birthday", "employmentdate"):
			return str(AbsTime(1440*int(v))).replace(" 00:00","")
		elif k in ("validfrom", "validto"):
			return str(AbsTime(int(v)))
		else:
			if isinstance(v, str):
				v = v.decode('latin1')
				return v.encode('utf-8')
			else:
				return str(v)
	for k in sorted(dr.keys(), comparer):
		if len(dr[k]) == 1: v = formatval(k, dr[k][0][0])
		else:
			v0 = None; f0 = None; t0 = None
			vs = []
			for v,f,t in dr[k]:
				if v0 != v:
					if not v0 is None:
						vs.append((v0, f0, t0))
					v0 = v
					f0 = f
				t0 = t
			if not v0 is None:
				vs.append((v0, f0, t0))
			if len(vs) == 1:
				v = formatval(k, vs[0][0])
			else:
				v = ('\n  ' + ' ' * maxlen).join(['%s (%s-%s)' % (formatval(k,x[0]), str(AbsTime(x[1])).replace(" 00:00",""), str(AbsTime(x[2])).replace(" 00:00","")) for x in vs])
		print ("%"+str(maxlen)+"s: %s") % (k, v)
		
def _cond(col, val):
	if "," in val:
		return "%s in (%s)" % (col, val)
	elif "*" in val:
		return (col, "LIKE", val.replace('*','%'))
	elif "%" in val:
		return (col, "LIKE", val)
	elif val[:1] in ('<','>'):
		l = 1
		if val[1] == '=': l = 2
		return (col, val[:l], val[l:])
	else:
		if val[0] == '"': val = val.replace('"',"'")
		return (col, "=", str(val))

def id(crewid):
	match = False
	for entry in _dbsearch("crew", "id = '%s'" % crewid):
		print "Crew:"
		_format([entry])
		match = True
	if not match:
		print >>sys.stderr, "Crew '%s' not found" % crewid
	else:
		print "Employment:"
		_format(_dbsearch("crew_employment", "crew = '%s'" % crewid))

def empno(extperkey):
	match = False
	crew = {}
	for entry in _dbsearch("crew_employment", "extperkey = '%s'" % extperkey):
		if not entry["crew"] in crew:
			print "Matching crew",entry["crew"]
			id(entry["crew"])
			match = True
			crew[entry["crew"]] = 1
	if not match:
		print >>sys.stderr, "No crew found with employment nr '%s'" % extperkey
	

def search(filter=None, rank=None, region=None, base=None, name=None, time=None):
	match = False
	fltstr = []
	empfltstr = []
	if filter: fltstr.append(filter)
	if rank: empfltstr.append(_cond("crewrank",rank))
	if region: empfltstr.append(_cond("region",region))
	if base: empfltstr.append(_cond("base",base))
	if name: fltstr.append(_cond("name",name))
	if time:
		if not time.isdigit(): time = int(AbsTime(time))
		empfltstr.append(("validfrom","<=",time))
		empfltstr.append(("validto",">",time))
	crewlist = set()
	if len(empfltstr) == 0:
		crewlist = set(crew["id"] for crew in _dbsearch("crew", fltstr))
	elif len(fltstr) == 0:
		crewlist = set(crew["crew"] for crew in _dbsearch("crew_employment", empfltstr))
	else:
		vs = _dbsearch("crew", fltstr,"crew_employment", empfltstr)
		crewlist = set(crew["id"] for crew in vs.get("crew",[]))
		crewlist.intersection_update(crew["crew"] for crew in vs.get("crew_employment",[]))
	if len(crewlist) > 0:
		print '\n'.join(sorted(crewlist))
	else:
		print >>sys.stderr, "No crew matches query"
		