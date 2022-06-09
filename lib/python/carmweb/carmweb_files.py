import utils
import os, time

@utils.webpage
def __root__(request):
    return "You must specify the path to browse"

def getmimetype(fileName):
    from subprocess import Popen, PIPE
    stdout,_ = Popen("file -bi '%s'" % fileName, shell=True, stdout=PIPE, stdin=PIPE).communicate("")
    return stdout.strip()

def getFileType(fileName):
    link = None
    try:
        if os.path.islink(fileName):
            link = os.readlink(fileName)
            fileName = os.path.realpath(fileName)
    except:
        return "(Unreadable)"
    if os.path.isdir(fileName):
        if link:
            return "(Link to directory)"
        return "(Directory)"
    try:
        if os.path.islink(fileName):
            return "%s file (symlink)" % os.path.splitext(fileName)[-1].upper()
    except: pass
    return "%s file" % os.path.splitext(fileName)[-1].upper()

def doSort(request, directory, contents):
    ret = []
    for f in contents:
        t = getFileType(os.path.join(directory, f))
        l = f
        isDir = False
        dt = ''
        try:
            rawdt = os.path.getmtime(os.path.join(directory, f))
            dt = time.ctime(rawdt)
        except:
            rawdt = 0
        if t[0]=='(':
            l += "/"
            isDir = True
        ret.append((f,l,t,dt,isDir,rawdt))
    s = request.args.get('sort',['name'])[0]
    if s == 'date':
        return [x[:4] for x in sorted(ret, key=lambda x:(-int(x[4]),-x[5]))]
    elif s == 'type':
        return [x[:4] for x in sorted(ret, key=lambda x:(-int(x[4]),x[2]))]
    return  [x[:4] for x in sorted(ret, key=lambda x:(-int(x[4]),x[0]))]

def base(dirsym, request):
    path = request.path
    parent = '/'.join(path.split('/')[:-1])
    if len(parent) <= 6: parent = ''
    directory = os.path.expandvars('$%s/%s' % (dirsym, '/'.join(request.path.split('/')[3:])))
    if os.path.isfile(directory):
        request.setHeader("content-type", getmimetype(directory))
        return file(directory).read()
    try:
        contents = os.listdir(directory)
    except Exception, e:
        return "Unable to read directory: %s" % e
    contents = doSort(request, directory, contents)
    return utils.template('filereader.html', locals())

@utils.webpage
def CARMDATA(request):
    return base('CARMDATA',request)

@utils.webpage
def CARMUSR(request):
    return base('CARMUSR',request)

@utils.webpage
def CARMSYS(request):
    return base('CARMSYS',request)
