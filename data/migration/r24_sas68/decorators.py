#!/bin/env python 



from adhoc.fixrunner import OnceException



def dec(function):
    try:
        function()
    except Exception as e:
        print "\n"*3
        print "*"*100
	print "[*]%r" % e
        print "*"*100
        print "\n"*3
