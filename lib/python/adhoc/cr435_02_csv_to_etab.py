#!/bin/env python


"""
Small script that reads CSV file and writes data as Etable.
"""

import sys


def tonum(s):
    try:
        return int(s)
    except:
        return 0


def run(input, output, f0saldo):
    inp = open(input, "r")
    oup = open(output, "w")
    print >>oup, '\n'.join((
        '/* Convertible Overtime from Excel */',
        '3',
        'Screwid "Crew ID",',
        'Astartdate "Salary month",',
        'Iconvot "Convertible Overtime in minutes",',
        '',
    ))
    oup2 = open(f0saldo, "w")
    print >>oup2, '\n'.join((
        '/* F0_BUFFER saldo from Excel */',
        '3',
        'Screwid "Crew ID",',
        'Atim "Bookingdate",',
        'Iconvot "Convertible Overtime in minutes",',
        '',
    ))

    try:
        for row in inp:
            fields = row.split(';')
            crewid = fields[0]
            if tonum(fields[4]):
                print >>oup2, '"%s", 01SEP2009, %s,' % (crewid, tonum(fields[4]))
            if tonum(fields[5]):
                print >>oup, '"%s", 01SEP2009, %s,' % (crewid, tonum(fields[5]))
            if tonum(fields[6]):
                print >>oup, '"%s", 01OCT2009, %s,' % (crewid, tonum(fields[6]))
            if tonum(fields[7]):
                print >>oup, '"%s", 01NOV2009, %s,' % (crewid, tonum(fields[7]))
            if tonum(fields[8]):
                print >>oup, '"%s", 01DEC2009, %s,' % (crewid, tonum(fields[8]))
            if tonum(fields[14]):
                print >>oup, '"%s", 01JAN2010, %s,' % (crewid, tonum(fields[14]))
            #if tonum(fields[19]):
            #    print >>oup2, '"%s", 01FEB2010, %s,' % (crewid, tonum(fields[19]))
    finally:
        if inp:
            inp.close()
        if oup:
            oup.close()
        if oup2:
            oup2.close()


if __name__ == '__main__':
    run("cr435_indata.csv", "cr435_indata.etab", "cr435_expected_balances.etab")


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
