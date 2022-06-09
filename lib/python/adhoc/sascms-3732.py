import subprocess

def fixit():
    subprocess.call("etabdiff -c $DATABASE -s $SCHEMA -n -a -f $CARMUSR/crc/etable/adhoc/sascms-3732/etabdiff.xml $CARMUSR/crc/etable/adhoc/sascms-3732/est_driver_class_set.etab $CARMUSR/crc/etable/adhoc/sascms-3732/est_driver.etab", shell=True)

if __name__ == '__main__':
    fixit()
