import carmensystems.publisher.api as P
import xml.sax
import os
import sys
import traceback
from carmensystems.basics.atfork.atfork import basics_fork, BASICS_ATFORK_NONE

from utils.performance import profileme, clockme

def render(inFile, outFile, ignoreEmpty=True, doSubreports=True):
	print "prtmf render started",inFile,outFile,os.getpid()
	fn = __file__
	if fn[-4:] == '.pyc': fn = fn[:-1]
	cmdline = '$CARMSYS/bin/carmrunner "%s" %s %s "%s" "%s"' % (fn, str(int(bool(ignoreEmpty))), str(int(bool(doSubreports))), inFile, outFile)
	print ">>",cmdline
	os.system(cmdline)
	print "prtmf render ended",os.getpid()

@clockme
def do_render(inFile, outFile, ignoreEmpty=True, doSubreports=True):
	ext = outFile.split(".")[-1]
	base = outFile.split(".")[:-1]
	base = [x for x in base if x]
	print base
	print ext
	
	skip = None
	if ignoreEmpty:
		# Skip subreports containing no elements
		def _skip(rep):
			i = 'n/a'
			j = 'n/a'
			try:
				i = rep.index(">",2)
				j = rep.index("</", i)
				return not rep[i+1:j].strip()
			except:
				print "Malformed XML:"
				print rep
				print "i=%r, j=%r" % (i,j)
				raise
		skip = _skip
	
	if ext.lower() in ("htm","html"):
		fmt = P.HTML
	else:
		fmt = P.PDF
	tmpl = file(inFile,"r").read()
	print "Beginning"
	if doSubreports and "<newReport" in tmpl:
		reps = tmpl.split("<newReport")
		header = reps[0]
		footer = reps[-1]
		i = footer.index("</newReport")
		j = footer.index(">", i)
		reps[-1] = reps[-1][:j+1]
		footer = footer[j+1:]
		print "Have subreports"
		reps = reps[1:]
		print "%d reports to render" % len(reps)
		N = 8
		isplit = len(reps)/N
		allfiles = []
		pids = []
		for i in range(N-1):
			repsi = reps[i*isplit:(i+1)*isplit]
			pid = basics_fork(BASICS_ATFORK_NONE)
			if not pid:
				doMulti(repsi, header, footer, base, ext, fmt, skip)
				os.kill(os.getpid(),9) # Child process
			else:
				pids.append(pid)
				print "Forked off worker"
				allfiles += fileNames(repsi, header, footer, base, ext, fmt, skip)
		repsi = reps[i*isplit:]
		doMulti(repsi, header, footer, base, ext, fmt, skip)
		allfiles += fileNames(repsi, header, footer, base, ext, fmt, skip)
		print "Waiting for children to die"
		waitchildren(pids)
		return allfiles
	else:
		print "Rendering as one"
		doRender(tmpl, outFile, fmt)
		return [outFile]
	
@clockme
def waitchildren(pids):
	os.waitpid(-1,0)

def fileNames(reps, header, footer, base, ext, fmt, skip):
	allfiles = []
	for rep in reps:
		if skip and skip(rep): continue
		i = rep.index('name="') + 6
		j = rep.index('"', i+1)
		name = rep[i:j].replace("/","_").replace("\\","_").replace(":","")
		if base[0][-1] == '/':
			fileName = base[0] + '.'.join(base[1:] + [name, ext])
		else:
			fileName = '.'.join(base + [name, ext])
		allfiles.append(fileName)
	return allfiles
	
def doMulti(reps, header, footer, base, ext, fmt, skip):
	for rep in reps:
		if skip and skip(rep): continue
		i = rep.index('name="') + 6
		j = rep.index('"', i+1)
		name = rep[i:j].replace("/","_").replace("\\","_").replace(":","")
		i = rep.index(">",j)+1
		j = rep.find("</newReport",i)
		if j > 0:
			rep = header + rep[i:j] + footer
		else:
			rep = header + rep[i:] + footer
		if base[0][-1] == '/':
			fileName = base[0] + '.'.join(base[1:] + [name, ext])
		else:
			fileName = '.'.join(base + [name, ext])
		print "Generating",fileName
		doRender(rep, fileName, fmt)
	
_DATA = None 
	
def doRender(xmldata, outFile, fmt):
	global _DATA
	_DATA = xmldata
	sys.modules["ProxyReport"] = sys.modules[__name__]
	outFile = os.path.realpath(outFile)
	#print "Generating",outFile
	P.generateReport("ProxyReport", outFile, fmt, "")
	pass
	
class ProxyReport(P.Report):
	def __init__(self):
		P.Report.__init__(self)
		#print "I am a report"
		pass
	def create(self):
		#print args
		#global _DATA
		#print _DATA
		#print "Hej"
		xml.sax.parseString(_DATA, Handler(self))
	
class Handler(xml.sax.handler.ContentHandler):
	els = []
	struct = []
	children = None
	depth = 0
	text = None
	addPos = None
	args = {}
	bufferedOp = None
	lastel = None
	hasChildren = False
	def __init__(self, rep):
		xml.sax.handler.ContentHandler.__init__(self)
		self.rep = rep
		self.struct.append(rep)
		
	def startDocument(self):
		pass
		
	def startElement(self, el,a):
		if el == "newReport": return
		self.lastel = el
		if not el in ["s","newReport","add"]:
			args = {}
			for k in dict(a):
				if k != k.lower(): continue
				v = str(a[k])
				k = str(k)
				if k in ["width", "height", "colspan", "rowspan", "align", "size", "orientation"]:
					if v == "None":
						continue
					try:
						v = int(v)
					except:
						v = getattr(P, v)
				elif v[:1] == ":" and v.find(":",1) > 1:
					nm = v.split(":")[1]
					f = getattr(P,nm)
					xargs = mkdict(v.split(":")[2])
					try:
						v = f(**xargs)
					except:
						print "Problem with arg %s" % nm
						print f, xargs
						traceback.print_exc()
						print xargs
				elif v == "None":
					continue
				args[k] = v
			if not el in ["Crossref"]:
				self.args = args
			else:
				cref = P.Crossref(**args)
				if self.children is None:
					raise ValueError("Unsupported child Crossref")
				self.children.append(cref)
			#print el,"Setting args to",self.args
		if len(self.els) == 0:
			#print "beginning report",el
			for k in self.args:
				if k == "orientation":
					self.rep.setpaper(self.args[k])
				elif k == "font":
					self.rep.set(font=self.args[k])
		else:
			if el == "s":
				pass
			elif el == "add":
				self.hasChildren = True
				self.addPos = str(a.get("p","")) or None
			else:
				if not hasattr(P,el):
					raise ValueError("PRT does not support '%s' in %s" % (el,self.els))
				self.text = None
				
				if el not in ["Text","Isolate","Crossref"]:
					Cls = getattr(P, el)
					if not isinstance(Cls, type):
						raise ValueError("Not a PRT class: %s" % el)
					try:
						o = Cls(**self.args)
					except:
						print "Problem with class %s" % el
						print self.args
						traceback.print_exc()
						#print self.els
						#print "Element",el
						sys.exit(1)
					prev = self.struct[-1]
					o1 = self.doBufferedOp(o)
					if o1:
						self.struct.append(o1)
					self.struct.append(o)
					if self.addPos:
						raise ValueError("Unsupported add position '%s'" % self.addPos)
					if o1:
						prev.add(o1)
						#print "++ 1 Adding %s to %s" % (o1, prev)
					else:
						prev.add(o)
						#print "++ 2 Adding %s to %s" % (o, prev)
						#print self.struct
				elif not el in ["Text","Crossref"]:
					self.bufferedOp = (el, self.args)
				elif el =="Text":
					self.children = []
		self.els.append(el)
	
	def doBufferedOp(self, o):
		if self.bufferedOp:
			sel, sargs = self.bufferedOp
			self.bufferedOp = None
			if sel == "Isolate":
				#print "Creating Isolate"
				return P.Isolate(o, **sargs)
			else:
				raise ValueError("Unsupported buffered creation of %s" % sel)
		return None
		
	def endElement(self, el):
		if el == "newReport":
			if self.hasChildren:
				self.struct[-1].newpage()
			self.hasChildren = False
			return
		if self.els[-1] == el:
			del self.els[-1]
		else:
			raise "Mismatch"
		#print "End",el, "    "
		if el == "s":
			if self.children is None:
				raise ValueError("text not valid here")
			if not self.text is None:
				self.children.append(self.text)
				self.text = None
		if el == "Text":
			#print "textargs:", self.args
			#print "Text is",repr(self.text)
			#firstString = ""
			#if len(self.children) > 0:
			#	firstString = self.children[0]
			#print self.children
			o = P.Text(*tuple(self.children), **self.args)
			#for string in self.children[1:]:
			#	o.add(string)
			o1 = self.doBufferedOp(o)
			prev = self.struct[-1]
			if o1:
				self.struct.append(o1)
			#print "++ 3 Adding %s to %s" % (o, prev)
			prev.add(o)
			self.children = None

		if el == "add":
			if self.addPos == "page0":
				self.struct[-1].page0()
			elif self.addPos == "page":
				self.struct[-1].page()
			elif self.addPos == "newpage":
				self.struct[-1].newpage()
			elif self.addPos:
				raise ValueError("Unsupported 'add' position '%s'" % self.addPos)
		if not el in ["s", "add", "Text", "Crossref"]:
			#print " -- ", self.struct[-1] 
			del self.struct[-1]
			#print self.struct
		self.lastel = None
			
	def characters(self, chars):
		if not self.children is None and self.lastel == "s":
			if not self.text:
				try:
					self.text = str(chars)
				except:
					self.text = chars.encode('latin1')
			else:
				try:
					self.text += str(chars)
				except:
					self.text += chars.encode('latin1')
def mkdict(s):
	d = {}
	for a in str(s).split(";"):
		k,v = a.split("=")
		if k in ["top","bottom","left","right","face","weight","size","style","inner_horizontal","inner_vertical","inner_wall"]:
			try:
				v = int(v)
			except:
				raise ValueError("Not an int: %s" % repr(v))
		d[k] = v
	return d
if __name__ == '__main__':
	if len(sys.argv) < 3:
		print >>sys.stderr, "Usage: %s {1|0} <filename.xml> [output_basename.pdf]" % sys.argv[0]
		sys.exit(1)
	ignoreEmpty = int(sys.argv[1])
	doSubreports = int(sys.argv[2])
	inf = sys.argv[3]
	if inf[-4:] != '.xml': inf += '.xml'
	outf = inf[:-4] + '.pdf'
	if len(sys.argv) > 4:
		outf = sys.argv[4]
	do_render(inf, outf, bool(ignoreEmpty), bool(doSubreports))
