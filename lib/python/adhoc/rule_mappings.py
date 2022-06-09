'''
Created on 6 aug 2010

@author: rickard.petzall
'''

import os
import sys
import csv

CARMUSR = os.path.realpath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append("%s/lib/python/utils/python-xlsx" % CARMUSR)

import xlsx
cases = {}
rules = {}
stats = [0,0,0,0]

def lev(s,t):
    s = ' ' + s
    t = ' ' + t
    d = {}
    S = len(s)
    T = len(t)
    for i in range(S):
        d[i, 0] = i
    for j in range (T):
        d[0, j] = j
    for j in range(1,T):
        for i in range(1,S):
            if s[i] == t[j]:
                d[i, j] = d[i-1, j-1]
            else:
                d[i, j] = min(d[i-1, j] + 1, d[i, j-1] + 1, d[i-1, j-1] + 1)
    return d[S-1, T-1]
try:
    import Levenshtein
    lev = Levenshtein.distance
    print >>sys.stderr, "Levenshtein c library used. It will be quick"
except:
    print >>sys.stderr, "Levenshtein c library not found. Using slow fallback"
def tokenize(rmk):
    strp = lambda x: ''.join([y for y in x if y in 'abcdefghijklmnopqrstuvwxyz'])
    return strp(rmk.lower())
    #m = map(strp, rmk.lower().split())
    #print m
    #return ''.join(m)
    

def loadCases(excelFile):
    print >>sys.stderr, "Reading Excel document...",
    wb = xlsx.Workbook(excelFile)
    try:
        sheet = wb["Rules"]
    except:raise ValueError("I expected to find a worksheet named Rules")
    assert sheet["A1"].value == "Nr", "I expected column Nr at pos A1"
    assert sheet["B1"].value == "Rule", "I expected column Rule at pos B1"
    assert sheet["C1"].value == "Rule remark", "I expected column Rule remark at pos C1"
    rows = sheet.rows()
    print >>sys.stderr, "Done"
    print >>sys.stderr, "Extracting data from Excel document...",
    for rownum in range(2,len(rows)+1):
        row = rows[unicode(rownum)]
        ruleNr = row[0].value.encode("latin-1",'ignore').strip()
        if ruleNr:
            ruleDesc = row[1].value.encode("latin-1",'ignore').strip()
            ruleRemark = row[2].value.encode("latin-1",'ignore').strip()
            ruleLike = tokenize(ruleRemark)
            if not ruleLike in cases:
                cases[ruleLike] = []
            cases[ruleLike].append((ruleNr, ruleDesc, ruleRemark))
    
    print >>sys.stderr, "Done. #cases:", len(cases)

def loadRules(csvFile):
    if not os.path.exists(csvFile):
        raise ValueError("Please run $CARMUSR/java_src/rulestocsv.sh first!")
    f = csv.reader(file(csvFile, 'r'))
    print >>sys.stderr, "Reading CSV document...",
    l = list(f)
    assert l[0][0] == "Rule", "I do not recognize this data/doc/rules.csv"
    
    for row in l[1:]:
        ruleName = row[0].strip()
        ruleModule = row[1].strip()
        ruleRemark = row[2].strip()
        ruleLike = tokenize(ruleRemark)
        if ruleLike in cases:
            print >>sys.stderr, "Conflicting rule remarks. Ignoring rule %s.%s" % (ruleModule, ruleName)
        
        rules[ruleLike] = (ruleName, ruleModule, ruleRemark)
    print >>sys.stderr, "Done. #rules:", len(l)-1
    
def findBestMatch(token, dic):
    if token in dic:
        stats[0] += 1
        return 0,dic[token]
    else:
        led = 1000000000
        tok = None
        i = 0
        for tks in dic:
            i += 1
            ld = lev(tks, token)
            if ld < led:
                tok = tks
                led = ld
        badness = led / float(max(len(token), len(tok)))
        if badness > 0.52:
            stats[2] += 1
            if dic is rules:
                return badness,('','','')
            else:
                return badness,[('','','')]
        else:
            stats[1] += 1
            return badness,dic[tok]
            #print "Fuzzy match:",token,"->",tok, " badness=",badness
def main(excelFile):
    if not os.path.exists(excelFile):
        raise ValueError("Could not find that file!")
    loadRules(os.path.join(CARMUSR, "data/doc/rules.csv"))
    loadCases(excelFile)
    
    csvout = file(os.path.join(CARMUSR, "data/doc/rule_map.csv"),"w")
    print >>csvout, r'Nr,Desc,RemarkOverview,RemarkRave,Name,Module,Fuzziness'
    print >>sys.stderr, "Mapping rules...",
    lout = []
    fix = lambda x: x.replace('\r','').replace('\n','').replace('"','')
    for tk in cases:
        fuzziness, matches = findBestMatch(tk, rules)
        m = matches
        for cs in cases[tk]:
            ruleNr = fix(cs[0])
            ruleDesc = fix(cs[1])
            ruleRemark = fix(cs[2])
            ruleName = fix(m[0])
            ruleModule = fix(m[1])
            ruleRemarkRave = fix(m[2])
            lout.append(r'"%s","%s","%s","%s","%s","%s",%d' %(
               ruleNr, ruleDesc, ruleRemark, ruleRemarkRave, ruleName, ruleModule, int(fuzziness*1000)))
    print >>csvout, '\n'.join(sorted(lout))
    print "Done"
    print "%d perfect matches, %d fuzzy matches, %d misses, %d re-uses" % tuple(stats)
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >>sys.stderr, "Usage: %s <path to rule_overview.xlsx>" % __file__
        sys.exit(1)
    try:
        main(sys.argv[1])
    except ValueError:
        print >>sys.stderr, sys.exc_info()[1]
        sys.exit(1)
    except AssertionError:
        print >>sys.stderr, sys.exc_info()[1]
        sys.exit(1)
