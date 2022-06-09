#
# Customized initialization for Studio
# Imported from the standard Studio startup file.
# 

print "StudioServerCustom:: starting to load customized modules..."

def IMPORT_SK(module):
    """
    Wrapper in order to make the system continue importing
    modules if for some reason it fails when starting up.

    You cannot do an try - except.
    """
    try:
        importStatement = 'import %s' % module
        exec importStatement in globals()
    except:
        print importStatement + ' FAILED!'
        try:    traceback.print_exc()
        except: pass

IMPORT_SK('traceback')

##############################
# Common CMS functionality CARMUSR

IMPORT_SK('carmusr.FileHandlingExt')
IMPORT_SK('MenuState')

print "StudioServerCustom:: loading finished."

# eof
