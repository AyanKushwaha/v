
"""
Rules and Parameters
------------------------------

Functionality:
RuleSet class for handling rule sets
ParameterSet class for handling parameter sets
Parameters for handling single parameters

"""
from application import application
import os, re

if application=="Matador":
    import carmstd.matador.parameters as parameters
else:
    import carmstd.studio.parameters as parameters


#------------------------ Rule Set -------------------------
def getCurrentRuleSet():
    """
    Returns the currently loaded rule set

    returns: RuleSet
    """
    return RuleSet(parameters.getCurrentRuleSetName())

class RuleSet:
    """
    Ex:
    CabinCCR=RuleSet('CabinCCR')
    CabinCCR.compile()
    CabinCCR.load()
    """
    def __init__(self,name,apps="gpc"):
        """
        Create an instance of a rule set

        name: Name of the rule set (basename) or the full path
        apps: Applications using the rule set (Used when compiling)
        """
        if os.path.basename(name) == name:
            self.name = name
        else:
            self.name = os.path.basename(name)
        self.apps=apps

    def __str__(self):
        return self.getName()

    def getName(self):
        """
        Returns the name of the rule set

        returns: string
        """
        return self.name

    def getFilePath(self):
        """
        Returns the file path to the top source file

        returns: filepath
        """
        return os.path.join(os.environ['CARMUSR'],
                            'crc',
                            'source',
                            self.getName())

    def load(self):
        """
        Load the rule set
        """
        print "parameters.RuleSet('"+self.name+"').load()"
        parameters.loadRuleSet(self.name)

    def compile(self,apps=None):
        """
        Compile the rule set
        """
        if apps==None:
            apps=self.apps
        print "parameters.RuleSet('"+self.name+"').compile()"
        cmd = '$CARMSYS/bin/crc_compile -optimize '+ apps 
        cmd += ' "$CARMUSR/crc/source/%s"' % (self.name)
        os.system(cmd)

    def __eq__(self,other):
        return isinstance(other,RuleSet) and self.name==other.name

#------------------------ Parameter Set -------------------------
class ParameterSet:
    """
    Ex:
    params=ParameterSet('CabinCCR/Default')
    params.load() # Will load the parameters CabinCCR/Default
    params.saveAs('CabinCCR/Default_copy') # Will save them again
    
    """

    def __init__(self,filePath,regexp=None):
        """
        Instantiate a parameter set

        name: the filepath from $CARMUSR/crc/parameters or the full path
        """
        self.filePath=filePath
        if regexp:
            raise ValueError("Not yet supported!")
        self.regexp=regexp

    def load(self):
        """
        Load the parameter set
        """
        print "parameters.ParameterSet('"+self.filePath+"').load()"
        parameters.loadParameterSet(self.filePath)

    def save(self):
        """
        Saves the parameter set
        """
        print "parameters.ParameterSet('"+self.filePath+"').save()"
        self.saveAs(filePath)

    def saveAs(self,filePath):
        """
        Save the parameter set

        name: Name of the parameter set
        """
        print "rave.ParameterSet('"+self.filePath+"').saveAs('"+filePath+"')"
        self.filePath=filePath
        parameters.saveParameterSet(self.filePath)

#------------------------ Parameter -------------------------
class Parameters:
    """
    Ex:
    from carmstd.parameters import parameter
    parameter['matador.shift_improve_tw_length']='48:00'

    NB! This class is a singleton class, and it is already initialized by rave.parameter

    Will become obsolete when the python rave api is extended with set functionality
    for parameters.

    """
    _parameters=None
    def __init__(self):
        """
        Instantiate the parameter class

        cache: Should the parameters be cached (Do not use together with a GUI)
        """
        # Make sure it can not be initialized (It is already initialized by rave.parameter)
        if Parameters._parameters:
            raise ValueError("This class is a singleton. Use already initialized rave.parameter")
        Parameters._parameters=self

        # Setup a cache dictionary
        self.cache={}

    def set(self,name,value):
        """
        Sets a parameter

        name: Name of the parameter
        value: Value of the parameter as a string
        """
        print "parameters.parameter['"+name+"']="+str(value)
        if parameters.useParameterCache:
            self.cache[name]=str(value)
        parameters.setParameterValue(name,str(value))

    def get(self,name):
        """
        Returns the value of a parameter 
        If cache is used, the value is taken from python without
        interaction with rave.

        !Note: The return type is a BSIRAP type in
        Studio and a string in matador.
        """
        print "parameters.parameter['"+name+"']"
        if parameters.useParameterCache and self.cache.has_key(name):
            return self.cache[name]
        else:
            return parameters.getParameterValue(name)
            
    def __setitem__(self,name,value):
        self.set(name,value)

    def __getitem__(self,name):
        return self.get(name)
        
parameter=Parameters()
