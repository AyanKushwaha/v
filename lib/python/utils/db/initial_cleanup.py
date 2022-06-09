#This script needs to be run from within cmsshell

from string import Template
from subprocess import call


for year in range(2008,2016):
    print "RUNNING INITIAL CLEANUP UP TO " + str(year)
    args = {'date': str(year)+'-01-01',
            'date_2013': str(min(year,2013))+'-01-01',
            'date_2014': str(min(year,2014))+'-01-01'}
    with open('initial_cleanup.template') as f:
        s = f.read()
    with open('/tmp/initial_cleanup.xml', 'w') as f:
        f.write(Template(s).substitute(args))
    call(['dave_cleanup', '-c', 'oracle:cms_production2/cms_production2@h1cms17a.net.sas.dk/CMSPR', '-s', 'cms_production2', '-g', '/tmp/initial_cleanup.xml'])


